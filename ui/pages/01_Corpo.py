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
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()

# --- NOVO: GRÁFICO DE EVOLUÇÃO ---


st.divider()
st.subheader("⏱️ Cronômetro de Descanso (2:30)")
import streamlit.components.v1 as components
components.html(
    """
    <div style="text-align: center; font-family: sans-serif; color: #F2F2F2;">
        <button onclick="startTimer()" style="padding: 10px 20px; background: #8B0000; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold;">Iniciar Descanso</button>
        <h1 id="timer" style="font-size: 54px; margin: 15px 0; color: #8B0000;">02:30</h1>
    </div>
    <script>
        let timeLeft = 150;
        let timerId;
        function startTimer() {
            if(timerId) clearInterval(timerId);
            timeLeft = 150;
            updateDisplay();
            timerId = setInterval(() => {
                timeLeft--;
                if (timeLeft < 0) {
                    clearInterval(timerId);
                    alert("Descanso finalizado! Volte ao treino.");
                    timeLeft = 150;
                }
                updateDisplay();
            }, 1000);
        }
        function updateDisplay() {
            let m = Math.floor(timeLeft / 60);
            let s = timeLeft % 60;
            document.getElementById('timer').innerText = m + ":" + (s < 10 ? "0" : "") + s;
            if(timeLeft <= 10 && timeLeft > 0) {
                document.getElementById('timer').style.color = '#F44336';
            } else {
                document.getElementById('timer').style.color = '#8B0000';
            }
        }
    </script>
    """,
    height=180
)

st.divider()
st.subheader("🤖 Treinador de IA")
if st.button("🪄 Gerar Ficha de Treino para Hoje", use_container_width=True):
    with st.spinner("Analisando seu histórico..."):
        hist = query_all("SELECT log_date, exercise_name, reps FROM exercise_logs ORDER BY log_date DESC LIMIT 15")
        contexto = ""
        for h in hist:
            contexto += f"- {h['log_date']}: {h['exercise_name']} - {h['reps']} reps\n"
            
        prompt = f"""Atue como um treinador de calistenia experiente. O aluno é ECTOMORFO (1,86m, 70kg), focado em hipertrofia e ganho de peso. O descanso obrigatório entre séries é de 2,5 minutos (150 segundos) para recuperação total. 
Aqui está o histórico recente do usuário:\n{contexto}\n
Com base nisso, sugira a ficha de treino ideal para HOJE. Foque em progressão (aumentar reps ou séries) ou descanso ativo se houver sinais de overtraining.
Seja direto e motivador. Use tópicos."""
        
        ficha = ask_gemini(prompt)
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;">
            <div class="titulo">Ficha do Treinador</div>
            <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{ficha}</div>
        </div>""", unsafe_allow_html=True)

st.divider()
st.subheader("📈 Evolução de Repetições (Últimos 14 dias)")

historico = query_all("SELECT log_date, exercise_name, reps FROM exercise_logs ORDER BY log_date DESC LIMIT 50")

if historico:
    df = pd.DataFrame(historico)
    
    # Agrupa por data e exercício (somando os reps)
    df_agrupado = df.groupby(['log_date', 'exercise_name'])['reps'].sum().reset_index()
    
    fig = px.line(
        df_agrupado, 
        x='log_date', 
        y='reps', 
        color='exercise_name',
        markers=True,
        color_discrete_sequence=['#8B0000', '#F9A825', '#4CAF50', '#2196F3']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F2F2F2'),
        xaxis_title="Data",
        yaxis_title="Repetições",
        legend_title="Exercício"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Registre seus treinos para ver o gráfico de evolução.")
