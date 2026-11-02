"""
criar_projeto_samurai.py — V3.0 (Newsletter na Home e Rotação de Treino)

ENTREGAS:
1. DB: Cria a tabela 'user_settings' (guarda a divisão de treino e a data de início).
2. UI (Informação): Substitui o G1 pelas Newsletters recebidas via Pipedream.
3. UI (Corpo): Adiciona painel para fixar a divisão de treino (Push/Pull/Legs + Corrida).
4. API (Brief): A IA agora calcula o treino exato do dia baseado na rotação matemática.

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

def _git_run_safe(args: list[str]) -> subprocess.CompletedProcess:
    r = subprocess.run(["git"] + args, cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if r.stdout is None: r.stdout = ""
    if r.stderr is None: r.stderr = ""
    return r

def scan_stage_secrets() -> list[str]:
    problemas = []
    r = _git_run_safe(["diff", "--cached", "--name-only"])
    for f in (r.stdout or "").splitlines():
        f = f.strip()
        if not f: continue
        if Path(f).name in {".env", "config.json", "secrets.toml"} or f in {".streamlit/secrets.toml", ".streamlit/config.toml"}:
            problemas.append(f"Arquivo sensível: {f}")
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
# 1. DB (Tabela user_settings)
# ============================================================
def fix_schema_settings() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)
    if "user_settings" in txt:
        print("[SKIP] schema.py — user_settings já existe.")
        return
    
    marker = '"""CREATE TABLE IF NOT EXISTS user_stats (id INTEGER PRIMARY KEY, xp INTEGER NOT NULL DEFAULT 0, level INTEGER NOT NULL DEFAULT 1);""",'
    nova_linha = marker + '\n        """CREATE TABLE IF NOT EXISTS user_settings (id INTEGER PRIMARY KEY, workout_split TEXT, workout_start_date TEXT);""",'
    
    if marker in txt:
        txt = txt.replace(marker, nova_linha, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] schema.py — marcador não encontrado.")

# ============================================================
# 2. INFORMAÇÃO (Trocar G1 por Newsletters)
# ============================================================
def fix_informacao_newsletters() -> None:
    p = BASE / "ui" / "pages" / "03_Informacao.py"
    txt = read(p)

    if "# Últimas Newsletters recebidas" in txt:
        print("[SKIP] 03_Informacao.py — Newsletters já configuradas.")
        return

    old_block = '''    st.divider()
    st.subheader("🗞️ Últimas Notícias (G1)")
    try:
        url = "https://g1.globo.com/rss/g1/"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        feed = feedparser.parse(response.content)
        for entry in feed.entries[:5]: st.markdown(f"- [{entry.title}]({entry.link})")
    except: st.warning("Erro ao carregar notícias.")'''

    new_block = '''    st.divider()
    st.subheader("🗞️ Últimas Newsletters recebidas")
    emails = query_all("SELECT subject, sender, content, received_at FROM newsletters_inbox ORDER BY received_at DESC LIMIT 5")
    
    if not emails:
        st.info("Nenhuma newsletter recebida ainda. (O Pipedream enviará assim que chegar um e-mail).")
    else:
        for e in emails:
            with st.expander(f"✉️ {e['subject']} (De: {e['sender']})"):
                st.caption(f"Recebido em: {e['received_at']}")
                # Mostra os primeiros 1500 caracteres (já limpos pelo backend)
                st.markdown(f"<div style='max-height: 300px; overflow-y: auto;'>{e['content'][:1500]}...</div>", unsafe_allow_html=True)'''

    if old_block in txt:
        txt = txt.replace(old_block, new_block, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 03_Informacao.py — bloco do G1 não encontrado.")

# ============================================================
# 3. CORPO (Painel de Rotação de Treino)
# ============================================================
def fix_corpo_rotacao() -> None:
    p = BASE / "ui" / "pages" / "01_Corpo.py"
    txt = read(p)

    if "Rotação de Treino" in txt:
        print("[SKIP] 01_Corpo.py — rotação já configurada.")
        return

    # 3.1 Inserir UI de Rotação
    old_title = 'st.title("💪 Corpo")\nst.caption("Treino progressivo com carga, histórico e cronômetro interativo.")'
    new_title = '''st.title("💪 Corpo")
st.caption("Treino progressivo com carga, histórico e cronômetro interativo.")

with st.expander("🔄 Rotação de Treino (Usada pela IA do Telegram)", expanded=False):
    st.write("Escolha a sua divisão fixa. O sistema calculará automaticamente qual é o treino de hoje.")
    
    settings = query_one("SELECT workout_split, workout_start_date FROM user_settings WHERE id = 1") or {}
    split_atual = settings.get("workout_split", "Musculação - Push/Pull/Legs + Corrida")
    
    OPCOES_SPLIT = [
        "Musculação - Push/Pull/Legs + Corrida",
        "Musculação - ABC",
        "Calistenia - Full Body",
        "Calistenia - PPL"
    ]
    
    nova_split = st.selectbox("Sua divisão fixa:", OPCOES_SPLIT, index=OPCOES_SPLIT.index(split_atual) if split_atual in OPCOES_SPLIT else 0)
    
    if st.button("Salvar Rotação (Reseta contagem para hoje)", use_container_width=True):
        hoje = date.today().isoformat()
        execute("INSERT INTO user_settings (id, workout_split, workout_start_date) VALUES (1, ?, ?) ON CONFLICT(id) DO UPDATE SET workout_split=excluded.workout_split, workout_start_date=excluded.workout_start_date", (nova_split, hoje))
        st.success("Rotação salva! O próximo treino será o primeiro da lista.")
        st.rerun()

    # Lógica matemática de qual treino é hoje
    if settings and settings.get("workout_start_date"):
        from datetime import datetime
        try:
            start_dt = datetime.strptime(settings["workout_start_date"], "%Y-%m-%d").date()
            dias = (date.today() - start_dt).days
            
            # Define a sequência baseada na escolha
            if "Push/Pull/Legs + Corrida" in split_atual:
                seq = ["Push (Peito, Ombro, Tríceps)", "Legs (Pernas)", "Pull (Costas, Bíceps)", "Corrida (Cardio)"]
            elif "ABC" in split_atual:
                seq = ["A (Peito, Tríceps, Ombro)", "B (Costas, Bíceps)", "C (Pernas)", "Descanso"]
            elif "Calistenia - PPL" in split_atual:
                seq = ["Push", "Pull", "Legs", "Descanso"]
            else:
                seq = ["Full Body", "Descanso"]
                
            treino_hoje = seq[dias % len(seq)]
            st.info(f"📅 **Treino calculado para hoje:** {treino_hoje} (Dia {dias} da rotação)")
        except Exception as e:
            st.warning(f"Erro ao calcular rotação: {e}")
    else:
        st.info("⚠️ Salve a sua rotação acima para que a IA saiba o treino de hoje.")'''

    if old_title in txt:
        txt = txt.replace(old_title, new_title, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 01_Corpo.py — título não encontrado.")

# ============================================================
# 4. API BRIEF (Injetar Treino na IA)
# ============================================================
def fix_api_brief_training() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "Treino do Dia (Rotação)" in txt:
        print("[SKIP] api_samurai.py — treino já injetado no brief.")
        return

    # 4.1 Calcular treino antes do prompt
    old_prompt = '''    # Busca as notícias do dia para incluir no brief'''
    
    new_prompt = '''    # Calcula o treino do dia baseado na rotação
    treino_hoje = "Treino não configurado"
    try:
        settings = query_one("SELECT workout_split, workout_start_date FROM user_settings WHERE id = 1")
        if settings and settings.get("workout_start_date"):
            from datetime import datetime
            start_dt = datetime.strptime(settings["workout_start_date"], "%Y-%m-%d").date()
            dias = (date.today() - start_dt).days
            split = settings["workout_split"]
            
            if "Push/Pull/Legs + Corrida" in split:
                seq = ["Push (Peito, Ombro, Tríceps)", "Legs (Pernas)", "Pull (Costas, Bíceps)", "Corrida (Cardio)"]
            elif "ABC" in split:
                seq = ["A (Peito, Tríceps, Ombro)", "B (Costas, Bíceps)", "C (Pernas)", "Descanso"]
            elif "Calistenia - PPL" in split:
                seq = ["Push", "Pull", "Legs", "Descanso"]
            else:
                seq = ["Full Body", "Descanso"]
                
            treino_hoje = seq[dias % len(seq)]
    except Exception as e:
        print(f"Erro ao calcular treino: {e}")

    # Busca as notícias do dia para incluir no brief'''

    if old_prompt in txt:
        txt = txt.replace(old_prompt, new_prompt, 1)

    # 4.2 Injetar no prompt da IA
    old_context = '''Dados do dia:
- Check-in: {status["checkin"] or "nao realizado"}'''
    
    new_context = '''Dados do dia:
- Treino do Dia (Rotação): {treino_hoje}
- Check-in: {status["checkin"] or "nao realizado"}'''

    if old_context in txt:
        txt = txt.replace(old_context, new_context, 1)

    # 4.3 Ajustar a instrução para a IA não inventar outro treino
    old_rule = '- Se burnout >= 60, incluir "Descanso e sono" em top_3_priorities.'
    
    new_rule = '''- Se burnout >= 60, incluir "Descanso e sono" em top_3_priorities.
- O campo "training" DEVE ser exatamente "{treino_hoje}", adaptando apenas a intensidade baseada no burnout.'''

    if old_rule in txt:
        txt = txt.replace(old_rule, new_rule, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] api_samurai.py — regra do prompt não encontrada.")

# ============================================================
# SYNC GIT
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
        
    _git_run_safe(["commit", "-m", "feat: substitui G1 por newsletters, implementa rotacao de treino e injeta no brief"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

# ============================================================
# MAIN
# ============================================================
def aplicar() -> None:
    print("=" * 60)
    print("V3.0 — NEWSLETTERS E ROTAÇÃO DE TREINO")
    print("=" * 60)

    etapas = [
        ("Criar tabela de configurações (schema.py)", fix_schema_settings),
        ("Substituir G1 por Newsletters (03_Informacao.py)", fix_informacao_newsletters),
        ("Criar painel de rotação (01_Corpo.py)", fix_corpo_rotacao),
        ("Injetar treino no Brief da IA (api_samurai.py)", fix_api_brief_training),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que fazer agora:")
    print("1. O Render e o Streamlit vão atualizar automaticamente (2 min).")
    print("2. No app, vá em 'Corpo' e defina a sua Rotação de Treino (PPL + Corrida).")
    print("3. Vá em 'Informação' e veja se as suas newsletters do Pipedream apareceram.")
    print("4. Para testar no Telegram, rode o 'Run workflow' no GitHub Actions.")
    print("   A IA vai ler a sua rotação e mandar o treino certinho do dia!")

if __name__ == "__main__":
    aplicar()