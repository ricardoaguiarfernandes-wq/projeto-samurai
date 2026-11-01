import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

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
