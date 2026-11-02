"""Dojo — resumo do dia, hábitos pendentes e energia."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date

import streamlit as st

from core.database import query_all, query_one, execute

today_iso = date.today().isoformat()

st.title("🏯 Dojo")

# --- GAMIFICAÇÃO ---
try:
    stats = query_one("SELECT xp FROM user_stats WHERE id = 1") or {"xp": 0}
except Exception:
    execute("CREATE TABLE IF NOT EXISTS user_stats (id INTEGER PRIMARY KEY, xp INTEGER NOT NULL DEFAULT 0, level INTEGER NOT NULL DEFAULT 1)")
    execute("INSERT INTO user_stats (id, xp, level) VALUES (1, 0, 1)")
    stats = {"xp": 0}
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
""", unsafe_allow_html=True)
DIAS_SEMANA = {
    "Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"
}
dia_ingles = date.today().strftime('%A')
dia_pt = DIAS_SEMANA.get(dia_ingles, dia_ingles)
st.caption(f"Hoje é {dia_pt}, {date.today().strftime('%d/%m/%Y')}")

checkin = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

col1, col2, col3 = st.columns(3)
if checkin:
    with col1:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Energia</div>
                <div class="valor">{checkin['energy']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Sono</div>
                <div class="valor">{checkin['sleep_hours']}h</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Estresse</div>
                <div class="valor">{checkin['stress']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("⚡ Nenhum check-in hoje. Vá em **Consistência** e registre sua energia.")

st.subheader("🎯 Hábitos pendentes hoje")

rows = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

pendentes = [r for r in rows if not r["done"]]
concluidos = [r for r in rows if r["done"]]

if not pendentes:
    st.success("🥋 Todos os hábitos foram cumpridos. Disciplina exemplar.")
else:
    for r in pendentes:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">{r['pillar']}</div>
                <div class="valor" style="font-size:1.1rem;">{r['name']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if concluidos:
    st.divider()
    st.caption(f"✅ {len(concluidos)} hábito(s) já cumprido(s) hoje")

st.divider()
if st.button("📝 Fazer check-in diário agora", use_container_width=True):
    st.switch_page("ui/pages/07_Consistencia.py")
