import streamlit as st
import sys
from pathlib import Path
from datetime import date
import pandas as pd
import plotly.express as px

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("💪 Corpo")
st.caption("Treino calistênico progressivo.")
hoje = date.today().isoformat()

divisao = st.selectbox("Divisão de Treino:", ["Full Body (Corpo Inteiro)", "PPL (Push/Pull/Legs)", "Upper/Lower (Superiores/Inferiores)"])

if divisao == "Full Body (Corpo Inteiro)":
    EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]
elif divisao == "PPL (Push/Pull/Legs)":
    dia_semana = date.today().weekday()
    if dia_semana in [0, 3]: EXERCICIOS = ["Flexão de Braço", "Desenvolvimento", "Tríceps"]
    elif dia_semana in [1, 4]: EXERCICIOS = ["Barra Fixa", "Remada", "Rosca Direta"]
    else: EXERCICIOS = ["Agachamento", "Afundo", "Panturrilha"]
else:
    dia_semana = date.today().weekday()
    if dia_semana in [0, 3]: EXERCICIOS = ["Barra Fixa", "Flexão de Braço", "Remada"]
    else: EXERCICIOS = ["Agachamento", "Afundo", "Prancha (segundos)"]

st.subheader(f"🥋 Treino de Hoje: {divisao}")
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        col1, col2 = st.columns([2, 1])
        with col1: st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}")
            novos_valores[ex] = {"reps": reps, "sets": sets}
    if st.form_submit_button("💾 Salvar Treino", use_container_width=True):
        for ex, val in novos_valores.items():
            if val["reps"] > 0:
                execute("INSERT INTO exercise_logs (log_date, exercise_name, reps, sets) VALUES (?, ?, ?, ?) ON CONFLICT(log_date, exercise_name) DO UPDATE SET reps = excluded.reps, sets = excluded.sets", (hoje, ex, val["reps"], val["sets"]))
        st.rerun()

st.divider()
st.subheader("⏱️ Cronômetro de Descanso (2:30)")
import streamlit.components.v1 as components
components.html("""<div style="text-align: center; color: #F2F2F2;"><button onclick="startTimer()" style="padding: 10px 20px; background: #8B0000; color: white; border: none; border-radius: 5px; cursor: pointer;">Iniciar Descanso</button><h1 id="timer" style="font-size: 54px; color: #8B0000;">02:30</h1></div><script>let timeLeft=150;let timerId;function startTimer(){if(timerId)clearInterval(timerId);timeLeft=150;updateDisplay();timerId=setInterval(()=>{timeLeft--;if(timeLeft<0){clearInterval(timerId);alert("Descanso finalizado!");timeLeft=150;}updateDisplay();},1000);}function updateDisplay(){let m=Math.floor(timeLeft/60);let s=timeLeft%60;document.getElementById("timer").innerText=m+":"+(s<10?"0":"")+s;}</script>""", height=180)

st.divider()
st.subheader("🤖 Treinador de IA")
if st.button("🪄 Gerar Ficha de Treino para Hoje", use_container_width=True):
    with st.spinner("Analisando..."):
        hist = query_all("SELECT log_date, exercise_name, reps FROM exercise_logs ORDER BY log_date DESC LIMIT 15")
        ctx = "".join([f"- {h['log_date']}: {h['exercise_name']} - {h['reps']} reps\n" for h in hist])
        prompt = f"Atue como treinador. Aluno ectomorfo (1,86m, 70kg). Divisão atual: {divisao}. Histórico:\n{ctx}\nSugira o treino de hoje focando em progressão."
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)
