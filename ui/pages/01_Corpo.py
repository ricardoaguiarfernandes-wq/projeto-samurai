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
st.caption("Treino calistênico progressivo com carga e histórico.")
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

# GERADOR DE IA
if st.button("🤖 Gerar Ficha de Treino com IA para Hoje", use_container_width=True):
    with st.spinner("O Treinador está analisando seu histórico e preparando a ficha..."):
        hist = query_all("SELECT log_date, exercise_name, reps FROM exercise_logs ORDER BY log_date DESC LIMIT 15")
        ctx = "".join([f"- {h['log_date']}: {h['exercise_name']} - {h['reps']} reps\n" for h in hist])
        prompt = f"Atue como treinador de calistenia. Aluno ectomorfo. Divisão: {divisao}. Histórico:\n{ctx}\nSugira a ficha de hoje focando em progressão. Seja direto."
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)

st.markdown("### Registrar Execução")
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos = {}
    for ex in EXERCICIOS:
        val = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        # Usando 3 colunas para ficar mais limpo
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: st.markdown(f"**{ex}**")
        with c2:
            if "Prancha" in ex:
                reps = st.number_input("Segundos", min_value=0, value=int(val["reps"]), key=f"r_{ex}")
                sets = 3 # Prancha fixo em 3 séries
                load = 0
            else:
                reps = st.number_input("Reps", min_value=0, value=int(val["reps"]), key=f"r_{ex}")
                sets = st.number_input("Séries", min_value=0, value=3, key=f"s_{ex}") # Padrão 3 séries
                load = st.number_input("Carga (kg)", min_value=0, value=0, key=f"c_{ex}") # Novo campo de carga
            novos[ex] = {"reps": reps, "sets": sets, "load": load}
            
    if st.form_submit_button("💾 Salvar Treino", use_container_width=True):
        for ex, v in novos.items():
            if v["reps"] > 0:
                # Como a tabela original não tem coluna 'load', salvamos a carga junto nos 'notes' para histórico
                execute("INSERT INTO exercise_logs (log_date, exercise_name, reps, sets, notes) VALUES (?, ?, ?, ?, ?) ON CONFLICT(log_date, exercise_name) DO UPDATE SET reps=excluded.reps, sets=excluded.sets, notes=excluded.notes", (hoje, ex, v["reps"], v["sets"], f"Carga: {v['load']}kg"))
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
else:
    st.info("Sem histórico.")
