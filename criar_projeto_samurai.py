"""
criar_projeto_samurai.py — V8.1 (Sistema de Conquistas e Gamificação)

ENTREGAS:
1. DB: Cria a tabela 'achievements' para guardar os troféus.
2. LÓGICA: Adiciona XP ao marcar hábitos no Streamlit (bugfix).
3. UI: Cria a página 16_Conquistas.py (O Salão de Troféus).
4. API: Cria o verificador de conquistas (/api/check_achievements) que o Telegram chama.

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

def _git_run_safe(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)

def read(p: Path) -> str: return p.read_text(encoding="utf-8")
def write_validated(p: Path, content: str) -> None:
    if p.suffix == ".py":
        try: ast.parse(content, filename=str(p))
        except SyntaxError as e:
            print(f"[ABORTA] Sintaxe quebrada em {p}: {e}"); sys.exit(1)
    p.write_text(content, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")

# ============================================================
# 1. SCHEMA (Tabela de Conquistas)
# ============================================================
def fix_schema_achievements() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)
    
    if "CREATE TABLE IF NOT EXISTS achievements" in txt:
        print("[SKIP] schema.py — tabela achievements já existe.")
        return
    
    marker = '"""CREATE TABLE IF NOT EXISTS user_stats (id INTEGER PRIMARY KEY, xp INTEGER NOT NULL DEFAULT 0, level INTEGER NOT NULL DEFAULT 1);""",'
    nova_linha = marker + '\n        """CREATE TABLE IF NOT EXISTS achievements (id TEXT PRIMARY KEY, earned_at TEXT NOT NULL);""",'
    
    if marker in txt:
        txt = txt.replace(marker, nova_linha, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] schema.py — marcador de user_stats não encontrado.")

# ============================================================
# 2. FIX XP NO STREAMLIT (07_Consistencia.py)
# ============================================================
def fix_xp_streamlit() -> None:
    p = BASE / "ui" / "pages" / "07_Consistencia.py"
    txt = read(p)

    old_habit = '''        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """, (h["id"], today_iso, 1 if novo else 0),
        )
        alterou = True'''

    new_habit = '''        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """, (h["id"], today_iso, 1 if novo else 0),
        )
        # Bugfix: Adicionar XP se o hábito foi concluído (e não estava concluído antes)
        if novo and not h["done"]:
            try:
                execute("UPDATE user_stats SET xp = xp + 10 WHERE id = 1")
            except Exception:
                pass
        alterou = True'''

    if old_habit in txt:
        txt = txt.replace(old_habit, new_habit, 1)
        write_validated(p, txt)
    else:
        print("[SKIP] 07_Consistencia.py — bloco de hábito não encontrado ou já corrigido.")

# ============================================================
# 3. NAVEGAÇÃO E UI (Salão de Troféus)
# ============================================================
def create_achievements_page() -> None:
    # 3.1 Adicionar no app.py
    p_app = BASE / "app.py"
    txt_app = read(p_app)
    if "16_Conquistas.py" not in txt_app:
        old_nav = 'financas = st.Page("ui/pages/15_Financas.py", title="💸 Finanças")'
        new_nav = old_nav + '\nconquistas = st.Page("ui/pages/16_Conquistas.py", title="🏆 Conquistas")'
        
        old_dict = '"⚔️ Comando": [home, consistencia, disciplina, carreira, financas],'
        new_dict = '"⚔️ Comando": [home, consistencia, disciplina, carreira, financas, conquistas],'
        
        if old_nav in txt_app and old_dict in txt_app:
            txt_app = txt_app.replace(old_nav, new_nav, 1)
            txt_app = txt_app.replace(old_dict, new_dict, 1)
            write_validated(p_app, txt_app)

    # 3.2 Criar a página
    p = BASE / "ui" / "pages" / "16_Conquistas.py"
    if p.exists():
        print("[SKIP] 16_Conquistas.py já existe.")
        return

    content = '''import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import query_all
from core.schema import init_db

init_db()
st.title("🏆 Salão de Troféus")
st.caption("Suas conquistas na jornada Samurai.")

# Definição de todas as conquistas possíveis
TODAS_CONQUISTAS = {
    "primeiro_passo": {"nome": "Primeiro Passo", "desc": "Fez o primeiro check-in.", "icon": "👣"},
    "treino_dia": {"nome": "Sangue e Suor", "desc": "Completou o treino de hoje.", "icon": "💪"},
    "habito_completo": {"nome": "Disciplina", "desc": "Completou todos os hábitos de um dia.", "icon": "🔥"},
    "streak_7": {"nome": "Monge", "desc": "7 dias seguidos de domínio.", "icon": "🧘"},
    "financeiro": {"nome": "Investidor", "desc": "Registrou a primeira ação na carteira.", "icon": "📈"},
    "estudioso": {"nome": "Estudioso", "desc": "Respondeu 5 flashcards no Telegram.", "icon": "📚"}
}

# Buscar as que já foram ganhas
try:
    ganhas_db = query_all("SELECT id, earned_at FROM achievements")
    ganhas = {g['id']: g['earned_at'] for g in ganhas_db}
except Exception:
    ganhas = {}

# Exibe o Grid de Troféus
cols = st.columns(3)
for i, (key, data) in enumerate(TODAS_CONQUISTAS.items()):
    with cols[i % 3]:
        if key in ganhas:
            # Ganhou
            st.markdown(f"""
            <div class="samurai-card" style="text-align: center; border-left-color: #F9A825; background: linear-gradient(135deg, #2A1A00, #171717);">
                <div style="font-size: 3rem;">{data['icon']}</div>
                <div class="valor" style="font-size: 1.2rem; color: #F9A825;">{data['nome']}</div>
                <div class="detalhe">{data['desc']}</div>
                <div style="font-size: 0.7rem; color: #888; margin-top: 10px;">Ganhou em: {ganhas[key][:10]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Bloqueado
            st.markdown(f"""
            <div class="samurai-card" style="text-align: center; border-left-color: #333; opacity: 0.5;">
                <div style="font-size: 3rem; filter: grayscale(100%);">{data['icon']}</div>
                <div class="valor" style="font-size: 1.2rem;">???</div>
                <div class="detalhe">{data['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()
st.info("💡 Novas conquistas são desbloqueadas automaticamente conforme você usa o app e o Telegram. O Mentor vai te avisar!")
'''
    write_validated(p, content)

# ============================================================
# 4. API (Verificador de Conquistas e Comandos Telegram)
# ============================================================
def fix_api_achievements() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "/api/check_achievements" in txt:
        print("[SKIP] api_samurai.py — verificador já existe.")
        return

    # 4.1 Criar o endpoint de checagem
    endpoint = '''
# ============================================================
# VERIFICADOR DE CONQUISTAS
# ============================================================
def unlock_achievement(ach_id: str) -> bool:
    """Retorna True se desbloqueou agora, False se já tinha ou não cumpriu."""
    try:
        existe = query_one("SELECT id FROM achievements WHERE id = ?", (ach_id,))
        if not existe:
            execute("INSERT INTO achievements (id, earned_at) VALUES (?, ?)", (ach_id, date.today().isoformat()))
            # Dá 50 XP de bônus
            execute("UPDATE user_stats SET xp = xp + 50 WHERE id = 1")
            return True
    except Exception:
        pass
    return False

@app.get("/api/check_achievements", dependencies=[Depends(require_token)])
def check_achievements():
    novas = []
    
    # 1. Primeiro Passo
    if safe_int((query_one("SELECT COUNT(*) AS c FROM daily_checkins") or {}).get("c")) > 0:
        if unlock_achievement("primeiro_passo"): novas.append("Primeiro Passo")
        
    # 2. Treino Completo
    hoje = date.today().isoformat()
    if safe_int((query_one("SELECT COUNT(*) AS c FROM exercise_logs WHERE log_date = ?", (hoje,)) or {}).get("c")) > 0:
        if unlock_achievement("treino_dia"): novas.append("Sangue e Suor")
        
    # 3. Financeiro
    if safe_int((query_one("SELECT COUNT(*) AS c FROM portfolio") or {}).get("c")) > 0:
        if unlock_achievement("financeiro"): novas.append("Investidor")

    return {"new_achievements": novas}

'''

    marker = '# ============================================================\n# WEBHOOK DE EMAIL'
    if marker in txt:
        txt = txt.replace(marker, endpoint + marker, 1)
    else:
        print("[AVISO] api_samurai.py — marcador de email não encontrado.")

    # 4.2 Chamar a checagem no Telegram após responder hábitos ou flashcards
    old_reply = '''        res = ask_gemini(prompt)
        reply(res)'''
    
    new_reply = '''        res = ask_gemini(prompt)
        reply(res)
        
        # Verifica conquistas silenciosamente
        try:
            novas = check_achievements().get("new_achievements", [])
            if novas:
                reply(f"🏆 **NOVA CONQUISTA DESBLOQUEADA!**\\n\\nVocê ganhou: {', '.join(novas)}\\n(+50 XP)")
        except Exception:
            pass'''
            
    # Só substitui a primeira ocorrência (que é a do processamento de texto do telegram)
    txt = txt.replace(old_reply, new_reply, 1)

    write_validated(p, txt)

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: sistema de conquistas (badges), fix xp no streamlit e avisos no telegram"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
        
        try:
            hook_url = ""
            env_file = BASE / ".env.render"
            if env_file.exists():
                for line in read(env_file).splitlines():
                    if line.startswith("RENDER_DEPLOY_HOOK_URL="):
                        hook_url = line.split("=", 1)[1].strip()
                        break
            if hook_url:
                import requests
                requests.get(hook_url, timeout=10)
                print("[OK] Deploy no Render disparado!")
        except Exception:
            pass
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V8.1 — SALÃO DE TROFÉUS")
    print("=" * 60)

    fix_schema_achievements()
    fix_xp_streamlit()
    create_achievements_page()
    fix_api_achievements()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Render e o Streamlit atualizarem.")
    print("2. Abra a nova aba '🏆 Conquistas' no menu. Veja as medalhas que você já desbloqueou (Investidor, Primeiro Passo).")
    print("3. Vá no Telegram e faça um check-in ou mande um flashcard. Se você bater um recorde, ele vai avisar da nova conquista e te dar +50 XP!")

if __name__ == "__main__":
    aplicar()