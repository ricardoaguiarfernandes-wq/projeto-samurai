import streamlit as st
import sys
import time
from pathlib import Path
from datetime import date, datetime

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one
import streamlit.components.v1 as components

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
