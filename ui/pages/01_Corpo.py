import streamlit as st
import sys
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e histórico.")
hoje = date.today().isoformat()

divisao = st.selectbox("Divisão de Treino:", ["Full Body", "PPL (Push/Pull/Legs)", "Upper/Lower"])

if divisao == "Full Body":
    EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]
elif divisao == "PPL (Push/Pull/Legs)":
    dia = date.today().weekday()
    if dia in [0, 3]: EXERCICIOS = ["Flexão de Braço", "Desenvolvimento", "Tríceps"]
    elif dia in [1, 4]: EXERCICIOS = ["Barra Fixa", "Remada", "Rosca Direta"]
    else: EXERCICIOS = ["Agachamento", "Afundo", "Panturrilha"]
else:
    dia = date.today().weekday()
    if dia in [0, 3]: EXERCICIOS = ["Barra Fixa", "Flexão de Braço", "Remada"]
    else: EXERCICIOS = ["Agachamento", "Afundo", "Prancha (segundos)"]

st.subheader(f"🥋 Treino de Hoje: {divisao}")
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos = {}
    for ex in EXERCICIOS:
        val = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        col1, col2 = st.columns([2, 1])
        with col1: st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input("Segundos", min_value=0, value=int(val["reps"]), key=f"r_{ex}")
                sets = 1
            else:
                reps = st.number_input("Reps", min_value=0, value=int(val["reps"]), key=f"r_{ex}")
                sets = st.number_input("Séries", min_value=0, value=int(val["sets"]), key=f"s_{ex}")
            novos[ex] = {"reps": reps, "sets": sets}
    if st.form_submit_button("💾 Salvar Treino", use_container_width=True):
        for ex, v in novos.items():
            if v["reps"] > 0:
                execute("INSERT INTO exercise_logs (log_date, exercise_name, reps, sets) VALUES (?, ?, ?, ?) ON CONFLICT(log_date, exercise_name) DO UPDATE SET reps=excluded.reps, sets=excluded.sets", (hoje, ex, v["reps"], v["sets"]))
        st.rerun()

st.divider()
st.subheader("📈 Ficha do Aluno (Últimos 14 dias)")
hist = query_all("SELECT log_date, exercise_name, reps FROM exercise_logs ORDER BY log_date DESC LIMIT 50")
if hist:
    df = pd.DataFrame(hist)
    df_agrupado = df.groupby(['log_date', 'exercise_name'])['reps'].sum().reset_index()
    fig = px.line(df_agrupado, x='log_date', y='reps', color='exercise_name', markers=True, color_discrete_sequence=['#8B0000', '#F9A825', '#4CAF50', '#2196F3'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#F2F2F2'))
    st.plotly_chart(fig, use_container_width=True)
    
    if st.button("🤖 Analisar Evolução com IA", use_container_width=True):
        with st.spinner("Analisando progresso..."):
            ctx = df_agrupado.to_string(index=False)
            prompt = f"Atue como treinador de calistenia. Aluno ectomorfo (1,86m, 70kg). Aqui está o histórico:\n{ctx}\nCom base nisso, como está a evolução? O que devo aumentar (reps ou séries) no próximo treino? Seja direto."
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)
else:
    st.info("Sem histórico. Treine para gerar o gráfico.")
