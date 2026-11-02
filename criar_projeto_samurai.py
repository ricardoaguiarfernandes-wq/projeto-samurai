"""
criar_projeto_samurai.py — V2.0 Full (Gamificação + Vision + RAG)

ENTREGAS:
1. DB: Cria a tabela 'user_stats' para guardar o XP e o Nível.
2. API: Adiciona XP toda vez que um hábito é concluído.
3. API: Cria a rota '/webhook/telegram' para receber fotos (Vision) e textos (RAG).
4. UI: Exibe o Nível e XP no topo da página Home (Dojo).

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

# ============================================================
# SEGURANÇA — varredura de segredos no stage
# ============================================================
def _git_run_safe(args: list[str]) -> subprocess.CompletedProcess:
    r = subprocess.run(["git"] + args, cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if r.stdout is None: r.stdout = ""
    if r.stderr is None: r.stderr = ""
    return r

def scan_stage_secrets() -> list[str]:
    problemas: list[str] = []
    r = _git_run_safe(["diff", "--cached", "--name-only"])
    for f in (r.stdout or "").splitlines():
        f = f.strip()
        if not f: continue
        if Path(f).name in {".env", "config.json", "secrets.toml"} or f in {".streamlit/secrets.toml", ".streamlit/config.toml"}:
            problemas.append(f"Arquivo sensível: {f}")
    r = _git_run_safe(["diff", "--cached", "--unified=0"])
    for linha in (r.stdout or "").splitlines():
        if not linha.startswith("+") or linha.startswith("+++"): continue
        if re.search(r"postgres(?:ql)?://[^:]+:[^@\s]+@", linha):
            problemas.append(f"URL Postgres no diff: {linha[:80]}")
    return problemas

def read(p: Path) -> str: return p.read_text(encoding="utf-8")
def write_validated(p: Path, content: str) -> None:
    if p.suffix == ".py":
        try: ast.parse(content, filename=str(p))
        except SyntaxError as e:
            print(f"[ABORTA] Sintaxe quebrada em {p}: {e}"); sys.exit(1)
    p.write_text(content, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")

# ============================================================
# 1. CORE/SCHEMA.PY — Tabela de Gamificação
# ============================================================
def fix_schema_gamification() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)
    if "user_stats" in txt:
        print("[SKIP] schema.py — user_stats já existe.")
        return

    # Adiciona o DDL
    marker = '"""CREATE TABLE IF NOT EXISTS patrimony_fixed_income (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, rate TEXT);""",'
    nova_linha = marker + '\n        """CREATE TABLE IF NOT EXISTS user_stats (id INTEGER PRIMARY KEY, xp INTEGER NOT NULL DEFAULT 0, level INTEGER NOT NULL DEFAULT 1);""",'
    if marker in txt:
        txt = txt.replace(marker, nova_linha, 1)
    
    # Adiciona o Seed na init_db
    marker_seed = '    for name, pillar, desc in SEED_HABITS:\n        if not query_one("SELECT id FROM habits WHERE name = ?", (name,)):\n            execute("INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)", (name, pillar, desc))'
    seed_user = marker_seed + '\n\n    if not query_one("SELECT id FROM user_stats WHERE id = 1"):\n        execute("INSERT INTO user_stats (id, xp, level) VALUES (1, 0, 1)")'
    if marker_seed in txt:
        txt = txt.replace(marker_seed, seed_user, 1)

    write_validated(p, txt)

# ============================================================
# 2. API_SAMURAI.PY — XP, Webhook Telegram (Vision + RAG)
# ============================================================
def fix_api_telegram_and_gamification() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "/webhook/telegram" in txt:
        print("[SKIP] api_samurai.py — Webhook já configurado.")
        return

    # 2.1 Adicionar imports necessários
    txt = txt.replace("import hmac\n", "import hmac\nimport io\nimport requests\n", 1)

    # 2.2 Adicionar lógica de XP no toggle de hábito
    old_toggle = '''    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (habit_id, today_iso, new_val),
    )
    return {"habit_id": habit_id, "date": today_iso, "done": bool(new_val)}'''
    
    new_toggle = '''    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (habit_id, today_iso, new_val),
    )
    
    # Gamificação: ganha 10 XP ao concluir
    if new_val == 1:
        try:
            execute("UPDATE user_stats SET xp = xp + 10 WHERE id = 1")
        except Exception:
            pass
            
    return {"habit_id": habit_id, "date": today_iso, "done": bool(new_val)}'''
    
    if old_toggle in txt:
        txt = txt.replace(old_toggle, new_toggle, 1)

    # 2.3 Adicionar a rota do Webhook do Telegram (antes do webhook de email)
    marker_webhook = '''# ============================================================
# WEBHOOK DE EMAIL (compat — substitui webhook_render antigo)
# ============================================================'''
    
    tg_webhook = '''# ============================================================
# WEBHOOK DO TELEGRAM (Recebe Fotos e Textos)
# ============================================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

@app.post("/webhook/telegram")
async def receive_telegram(update: dict):
    if not TELEGRAM_BOT_TOKEN:
        return {"status": "error", "message": "Token do Telegram nao configurado no Render."}
    
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    if not chat_id:
        return {"status": "ignored"}
        
    def reply(text: str):
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10
        )

    # --- MODO 1: FOTO (Auto-Categorização de Gastos) ---
    if "photo" in message:
        reply("📸 Analisando comprovante e categorizando...")
        file_id = message["photo"][-1]["file_id"]
        
        # Baixa a imagem do Telegram
        r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}", timeout=10)
        file_path = r.json().get("result", {}).get("file_path")
        
        if file_path:
            img_bytes = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}", timeout=10).content
            
            from services.ai import ask_gemini_vision
            prompt = """Extraia os dados deste comprovante e retorne APENAS um JSON válido, sem markdown:
            {"amount": 0.0, "description": "Nome do Local", "category": "Alimentação/Transporte/Lazer/Outros"}
            Se não for um comprovante, retorne {"error": "not_a_receipt"}."""
            
            res = ask_gemini_vision(img_bytes, prompt)
            m = re.search(r'\\{.*\\}', res, re.DOTALL)
            
            if m:
                try:
                    data = json.loads(m.group(0))
                    if "error" in data:
                        reply("⚠️ Não consegui identificar um comprovante nessa imagem.")
                    else:
                        execute(
                            "INSERT INTO expenses (expense_date, description, amount, category) VALUES (?, ?, ?, ?)",
                            (date.today().isoformat(), data.get("description", "Desconhecido"), data.get("amount", 0.0), data.get("category", "Outros"))
                        )
                        reply(f"✅ Gasto registrado: *{data.get('description')}* \\nValor: R$ {data.get('amount'):.2f} \\nCategoria: {data.get('category')}")
                except Exception as e:
                    reply(f"⚠️ Erro ao processar JSON: {e}")
            else:
                reply("⚠️ A IA não conseguiu ler o comprovante.")
        else:
            reply("⚠️ Falha ao baixar a imagem do Telegram.")

    # --- MODO 2: TEXTO (Memória do Diário / RAG) ---
    elif "text" in message:
        text = message["text"]
        
        if text.startswith("/start"):
            reply("🥋 Bem-vindo ao Dojo Digital. Envie uma foto de comprovante ou digite sua dúvida para consultar o diário.")
            return {"status": "ok"}
            
        reply("🧠 Consultando as memórias do seu diário...")
        entries = query_all("SELECT entry_date, content FROM journal_entries ORDER BY entry_date DESC LIMIT 20")
        
        if not entries:
            reply("Ainda não tenho registros no seu diário para consultar.")
            return {"status": "ok"}
            
        ctx = "\\n".join([f"[{e['entry_date']}] {e['content']}" for e in entries])
        
        from services.ai import ask_gemini
        prompt = f"""Atue como meu Mentor Samurai. Baseado APENAS nestes registros recentes do meu diário:
{ctx}

Responda à minha pergunta: "{text}"
Se a resposta não estiver nos registros, diga que não encontrou. Seja direto e empático."""
        
        res = ask_gemini(prompt)
        reply(res)
        
    return {"status": "ok"}

# ============================================================
# WEBHOOK DE EMAIL (compat — substitui webhook_render antigo)
# ============================================================'''
    
    if marker_webhook in txt:
        txt = txt.replace(marker_webhook, tg_webhook, 1)
    
    write_validated(p, txt)

# ============================================================
# 3. HOME.PY — Interface de Gamificação
# ============================================================
def fix_home_gamification() -> None:
    p = BASE / "ui" / "pages" / "00_Home.py"
    txt = read(p)

    if "Patente" in txt:
        print("[SKIP] 00_Home.py — Gamificação já aplicada.")
        return

    old_title = 'st.title("🏯 Dojo")'
    new_title = '''st.title("🏯 Dojo")

# --- GAMIFICAÇÃO ---
stats = query_one("SELECT xp FROM user_stats WHERE id = 1") or {"xp": 0}
xp_total = stats["xp"] if stats else 0
nivel = (xp_total // 100) + 1
ranks = {1: "Ronin", 2: "Ashigaru", 3: "Samurai", 4: "Hatamoto", 5: "Daimyo"}
rank_atual = ranks.get(nivel, "Lenda")

st.markdown(f"""
<div class="samurai-card" style="display: flex; justify-content: space-between; align-items: center; border-left-color: #F9A825;">
    <div>
        <div class="titulo">Patente</div>
        <div class="valor">Nível {nivel} - {rank_atual}</div>
    </div>
    <div style="text-align: right;">
        <div class="titulo">Experiência</div>
        <div class="valor">{xp_total} XP</div>
    </div>
</div>
""", unsafe_allow_html=True)'''

    if old_title in txt:
        txt = txt.replace(old_title, new_title, 1)
        write_validated(p, txt)

# ============================================================
# 4. SYNC GIT
# ============================================================
def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    
    problemas = scan_stage_secrets()
    if problemas:
        print("\n[ABORTA] SEGREDOS DETECTADOS:")
        for p_ in problemas: print(f"  X {p_}")
        _git_run_safe(["reset"])
        sys.exit(1)
    print("[OK] Varredura de segredos: limpa")

    msg = "feat(v2.0): gamificacao (XP), Vision (comprovantes) e RAG (diario) no Telegram"
    _git_run_safe(["commit", "-m", msg])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído! O Render vai atualizar automaticamente.")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

# ============================================================
# MAIN
# ============================================================
def aplicar() -> None:
    print("=" * 60)
    print("V2.0 FULL — GAMIFICACAO + VISION + RAG")
    print("=" * 60)

    etapas = [
        ("Criar tabela de XP (schema.py)", fix_schema_gamification),
        ("Configurar API e Webhook (api_samurai.py)", fix_api_telegram_and_gamification),
        ("Exibir Nível na Home (00_Home.py)", fix_home_gamification),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\n⚠️ ULTIMO PASSO MANUAL (OBRIGATÓRIO):")
    print("Como o Telegram precisa saber para onde enviar as fotos,")
    print("voce precisa registrar o Webhook. Cole isto no seu PowerShell:")
    print("\ncurl.exe -F \"url=https://samurai-webhook.onrender.com/webhook/telegram\" https://api.telegram.org/bot<SEU_NOVO_TOKEN_AQUI>/setWebhook")
    print("\n(Substitua <SEU_NOVO_TOKEN_AQUI> pelo token do BotFather antes de rodar).")
    print("Se retornar {\"ok\":true}, está tudo pronto!")

if __name__ == "__main__":
    aplicar()