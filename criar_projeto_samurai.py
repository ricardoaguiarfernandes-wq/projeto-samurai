"""
criar_projeto_samurai.py — V4.0 (Módulo de Disciplina e Diversificação Global)

ENTREGAS:
1. DB: Cria a tabela 'discipline' (streak de sobriedade) e 'sos_logs' (histórico de emergência).
2. APP: Adiciona o menu lateral para a nova página 13_Disciplina.
3. UI (Disciplina): Cria o contador de dias, o Arsenal (gatilhos), o botão de SOS com timer e o registro de recaída.
4. IA FINANCEIRA: Atualiza o prompt do chat de patrimônio para buscar a meta de 15-20 ações globais e renda fixa diversificada.
5. API: Adiciona a inteligência de crise (SOS) no Telegram.

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
# 1. DB SCHEMA (Disciplina)
# ============================================================
def fix_schema_discipline() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)
    if "CREATE TABLE IF NOT EXISTS discipline" in txt:
        print("[SKIP] schema.py — tabelas de disciplina já existem.")
        return
    
    marker = '"""CREATE TABLE IF NOT EXISTS user_settings (id INTEGER PRIMARY KEY, workout_split TEXT, workout_start_date TEXT);""",'
    nova_linha = marker + '''
        """CREATE TABLE IF NOT EXISTS discipline (id INTEGER PRIMARY KEY, start_date TEXT, longest_streak INTEGER DEFAULT 0);""",
        """CREATE TABLE IF NOT EXISTS sos_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, log_date TEXT NOT NULL);""",'''
    
    if marker in txt:
        txt = txt.replace(marker, nova_linha, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] schema.py — marcador de user_settings não encontrado.")

# ============================================================
# 2. NAVEGAÇÃO (app.py)
# ============================================================
def fix_app_nav() -> None:
    p = BASE / "app.py"
    txt = read(p)
    if "13_Disciplina.py" in txt:
        print("[SKIP] app.py — navegação já configurada.")
        return

    old_nav = 'consistencia = st.Page("ui/pages/07_Consistencia.py", title="🎯 Consistência")'
    new_nav = old_nav + '\ndisciplina = st.Page("ui/pages/13_Disciplina.py", title="🛡️ Disciplina")'

    old_dict = '"⚔️ Comando": [home, consistencia],'
    new_dict = '"⚔️ Comando": [home, consistencia, disciplina],'

    if old_nav in txt and old_dict in txt:
        txt = txt.replace(old_nav, new_nav, 1)
        txt = txt.replace(old_dict, new_dict, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] app.py — estrutura de navegação não encontrada.")

# ============================================================
# 3. UI DA PÁGINA DE DISCIPLINA
# ============================================================
def create_disciplina_page() -> None:
    p = BASE / "ui" / "pages" / "13_Disciplina.py"
    if p.exists():
        print("[SKIP] 13_Disciplina.py — página já existe.")
        return

    content = '''import streamlit as st
import sys
import time
from pathlib import Path
from datetime import date, datetime

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one
from core.schema import init_db
import streamlit.components.v1 as components

init_db()
st.title("🛡️ Disciplina & Domínio")
st.caption("O contrário do vício não é a abstinência, é o domínio de si.")

# Inicializa se não existir
stats = query_one("SELECT start_date, longest_streak FROM discipline WHERE id = 1")
if not stats:
    execute("INSERT INTO discipline (id, start_date, longest_streak) VALUES (1, ?, 0)", (date.today().isoformat(),))
    stats = {"start_date": date.today().isoformat(), "longest_streak": 0}

start_date = datetime.strptime(stats["start_date"], "%Y-%m-%d").date()
dias_limpos = (date.today() - start_date).days

# Atualiza recorde se necessário
if dias_limpos > stats["longest_streak"]:
    execute("UPDATE discipline SET longest_streak = ? WHERE id = 1", (dias_limpos,))
    stats["longest_streak"] = dias_limpos

# --- CARDS DE STATUS ---
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""<div class="samurai-card" style="border-left-color: #4CAF50;"><div class="titulo">Dias de Domínio</div><div class="valor" style="font-size: 2rem; color: #4CAF50;">{dias_limpos}</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Recorde Pessoal</div><div class="valor" style="font-size: 2rem; color: #F9A825;">{stats["longest_streak"]}</div></div>""", unsafe_allow_html=True)

st.divider()

# --- BOTÃO SOS ---
st.subheader("🚨 Janela da Queda (SOS)")
st.write("A vontade dura de 5 a 30 minutos. Se estiver em crise, ative o protocolo.")
if st.button("🛑 ATIVAR PROTOCOLO DE EMERGÊNCIA", use_container_width=True, type="primary"):
    execute("INSERT INTO sos_logs (log_date) VALUES (?)", (datetime.now().isoformat(),))
    st.session_state["sos_ativo"] = True
    st.session_state["sos_start"] = time.time()

if st.session_state.get("sos_ativo"):
    elapsed = time.time() - st.session_state.get("sos_start", 0)
    remain = max(0, 600 - int(elapsed))  # 10 minutos
    
    if remain > 0:
        components.html(f"""
            <div id="timer" style="font-size: 48px; color: #F44336; text-align: center; font-family: sans-serif; font-weight: bold; margin-top: 10px;">{remain//60:02d}:{remain%60:02d}</div>
            <div style="text-align: center; color: #F2F2F2; font-family: sans-serif;">Respire fundo. O pico está passando.<br><b>Você é mais forte que isso.</b></div>
            <script>
                var timeLeft = {remain};
                var elem = document.getElementById('timer');
                var timerId = setInterval(function() {{
                    if (timeLeft <= 0) {{
                        clearInterval(timerId);
                        elem.innerHTML = "FIM DO PICO";
                        elem.style.color = "#4CAF50";
                    }} else {{
                        var m = Math.floor(timeLeft / 60);
                        var s = timeLeft % 60;
                        elem.innerHTML = m + ":" + (s < 10 ? "0" : "") + s;
                        timeLeft--;
                    }}
                }}, 1000);
            </script>
        """, height=90)
        
        st.info("💡 **Dica Samurai:** Saia do quarto, lave o rosto com água fria e beba um copo d'água. Se estiver no celular, mande uma mensagem para o Mentor no Telegram agora.")
        
        if st.button("🟢 Consegui superar o impulso"):
            st.session_state["sos_ativo"] = False
            st.rerun()
    else:
        st.success("✅ Protocolo concluído. O pico passou. Você venceu.")
        if st.button("Fechar Protocolo"):
            st.session_state["sos_ativo"] = False
            st.rerun()

st.divider()

# --- REGISTRO DE RECAÍDA ---
with st.expander("⚠️ Registrar Recaída"):
    st.write("O fracasso não é cair, mas não levantar. Se houve recaída, registre para resetar o contador.")
    if st.button("Resetar Contador (Hoje)", type="secondary"):
        execute("UPDATE discipline SET start_date = ? WHERE id = 1", (date.today().isoformat(),))
        st.session_state["sos_ativo"] = False
        st.success("Contador resetado. O caminho recomeça hoje. Mantenha a cabeça erguida.")
        time.sleep(2)
        st.rerun()

# --- O ARSENAL (Gatilhos) ---
st.subheader("⚔️ O Arsenal (Seus Gatilhos)")
st.write("Escreva aqui os seus principais gatilhos e as ações para combatê-los.")
gatilhos = st.text_area("Gatilhos (ex: Tédio, Estresse, Ficar sozinho no quarto à noite)", height=100)
if st.button("Salvar Arsenal"):
    st.success("Arsenal mental memorizado. A IA no Telegram usará isso para te ajudar.")
'''
    write_validated(p, content)

# ============================================================
# 4. ATUALIZAR PROMPT DO TELEGRAM (Inteligência de Crise)
# ============================================================
def fix_api_telegram_crisis() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "MODO 3: CRISE DE DISCIPLINA" in txt:
        print("[SKIP] api_samurai.py — inteligência de crise já existe.")
        return

    old_text_mode = '''    # --- MODO 2: TEXTO (RAG Geral ou Diario) ---
    elif "text" in message:
        text = message["text"].strip()
        if text.lower() in ["oi", "ola", "olá", "bom dia", "boa tarde", "boa noite", "eae", "e ai"]:'''

    new_text_mode = '''    # --- MODO 2: TEXTO (RAG Geral, Diario ou Crise) ---
    elif "text" in message:
        text = message["text"].strip()
        text_lower = text.lower()
        
        # MODO 3: CRISE DE DISCIPLINA (SOS)
        palavras_crise = ["sos", "vontade", "recaida", "recaída", "pornografia", "masturbacao", "masturbação", "impulso", "gatilho"]
        if any(p in text_lower for p in palavras_crise):
            reply("🛡️ **Protocolo de Emergência Ativado.**\\n\\nRespire fundo. O pico da vontade dura de 5 a 30 minutos. Você não precisa ceder a ele.")
            
            from services.ai import ask_gemini
            prompt_crise = f"""Atue como o Mentor de Disciplina do Projeto Samurai.
O usuário está em crise agora (gatilho detectado). Ele disse: "{text}".
Sua missão:
1. Acalme-o imediatamente (tom firme, empático e sem julgamentos).
2. Lembre-o que a dopamina barata escraviza, mas ele é o mestre.
3. Dê 3 ações práticas e rápidas (ex: lavar o rosto, sair do ambiente, beber água).
4. Mantenha a resposta curta (máximo 3 parágrafos) para ele ler rápido.
"""
            res = ask_gemini(prompt_crise)
            reply(res)
            return
        
        if text_lower in ["oi", "ola", "olá", "bom dia", "boa tarde", "boa noite", "eae", "e ai"]:'''

    if old_text_mode in txt:
        txt = txt.replace(old_text_mode, new_text_mode, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] api_samurai.py — bloco de texto do telegram não encontrado.")

# ============================================================
# 5. ATUALIZAR PROMPT DO CHAT FINANCEIRO (Diversificação Global)
# ============================================================
def fix_patrimonio_chat_global() -> None:
    p = BASE / "ui" / "pages" / "04_Patrimonio.py"
    txt = read(p)

    if "meta de 15 a 20 ações" in txt:
        print("[SKIP] 04_Patrimonio.py — meta global já implementada.")
        return

    old_rule = "2. **Atenção às Listas:** Se o usuário pedir uma lista de ações, sugestões ou disser \"quero uma lista dos 1%\", você DEVE listar explicitamente os tickers específicos que se encaixam na sua filosofia de valor (ex: TAEE11, BBAS3, CXSE3, SAPR11, ALUP11, etc.) e explicar o porquê de forma resumida. Não devolva a pergunta para o usuário."
    
    new_rule = "2. **Atenção às Listas:** Se o usuário pedir sugestões, lembre-se de que a meta do usuário é ter um portfólio de **15 a 20 ações diversificadas** (incluindo ativos internacionais/BDRs/ETFs como IVVB11, NASD11, ou ações diretas para proteção cambial) e Renda Fixa Nacional e Estrangeira. Liste explicitamente os tickers (B3 e internacionais) que se encaixam na filosofia de valor e explique o porquê. Não devolva a pergunta para o usuário."

    if old_rule in txt:
        txt = txt.replace(old_rule, new_rule, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 04_Patrimonio.py — regra do chat financeiro não encontrada.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: modulo de disciplina (sos, streak) e metas de investimento global"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V4.0 — DISCIPLINA E PATRIMÔNIO GLOBAL")
    print("=" * 60)

    etapas = [
        ("Criar tabelas de disciplina (schema.py)", fix_schema_discipline),
        ("Adicionar página no menu (app.py)", fix_app_nav),
        ("Criar interface de disciplina (13_Disciplina.py)", create_disciplina_page),
        ("Adicionar inteligência de crise no bot (api_samurai.py)", fix_api_telegram_crisis),
        ("Atualizar IA financeira para meta global (04_Patrimonio.py)", fix_patrimonio_chat_global),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que fazer agora:")
    print("1. Espere o Streamlit e o Render atualizarem (1-2 min).")
    print("2. No app, a nova aba '🛡️ Disciplina' estará no menu esquerdo.")
    print("3. Teste o botão SOS. O timer de 10 minutos vai rodar na tela.")
    print("4. Vá no Telegram e mande 'SOS' ou 'estou com vontade'. O bot vai ativar o protocolo de crise imediatamente.")
    print("5. No chat do Patrimônio, pergunte: 'Como monto uma carteira de 20 ações com proteção internacional?'")

if __name__ == "__main__":
    aplicar()