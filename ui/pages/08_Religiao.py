import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db, setup_biblia
from services.ai import ask_gemini

init_db()

st.title("🕊️ Religião & Bíblia")
tab_biblia, tab_praticas = st.tabs(["📖 Leitura Bíblica Diária", "🙏 Práticas e Oração"])

with tab_biblia:
    count_prog = query_one("SELECT COUNT(*) AS c FROM reading_progress")["c"]
    if count_prog == 0:
        with st.spinner("Iniciando plano..."):
            setup_biblia()
        st.rerun()
        
    proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")
    if not proximo:
        st.success("🎉 Você concluiu a Bíblia!")
    else:
        day = proximo["day"]
        plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
        if plano:
            versiculos = query_all("SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id", (plano["start_verse_id"], plano["end_verse_id"]))
            if versiculos:
                ref = f"{versiculos[0]['book_name']} {versiculos[0]['chapter']}:{versiculos[0]['verse']}"
                st.subheader(f"Dia {day} de 365 - {ref}")
                texto = "".join([f"**{v['verse']}** {v['text']}\n" for v in versiculos])
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 300px; overflow-y: auto;"><div style="line-height: 1.8;">{texto}</div></div>""", unsafe_allow_html=True)
                if st.button("✅ Concluir Leitura", use_container_width=True):
                    execute("UPDATE reading_progress SET completed = 1 WHERE day = ?", (day,))
                    st.rerun()

with tab_praticas:
    st.subheader("🙏 Práticas Espirituais")
    habits = query_all("SELECT h.id, h.name, COALESCE(l.done, 0) AS done FROM habits h LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ? WHERE h.pillar = 'Religião' AND h.active = 1", (date.today().isoformat(),))
    for h in habits:
        if st.checkbox(h["name"], value=bool(h["done"])):
            execute("INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, 1) ON CONFLICT(habit_id, log_date) DO UPDATE SET done = 1", (h["id"], date.today().isoformat()))
    
    st.divider()
    st.subheader("🙏 Oração do Dia")
    if st.button("Gerar Oração com IA", use_container_width=True):
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;">{ask_gemini("Crie uma oração curta e poderosa para o dia de hoje.")}</div>""", unsafe_allow_html=True)
