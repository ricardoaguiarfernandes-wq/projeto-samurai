import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db

init_db()

st.title("📖 Bíblia")
st.caption("Plano de leitura em 1 ano — Almeida Corrigida Fiel (ACF)")

proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")

if not proximo:
    st.success("🎉 Parabéns! Você concluiu a leitura da Bíblia em 1 ano!")
    st.balloons()
else:
    day = proximo["day"]
    st.subheader(f"Dia {day} de 365")

    plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
    if plano:
        start_id = plano["start_verse_id"]
        end_id = plano["end_verse_id"]

        versiculos = query_all(
            "SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id",
            (start_id, end_id)
        )

        if versiculos:
            primeiro = versiculos[0]
            ultimo = versiculos[-1]
            
            if primeiro["book_name"] == ultimo["book_name"]:
                if primeiro["chapter"] == ultimo["chapter"]:
                    ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']}-{ultimo['verse']}"
                else:
                    ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']} a {ultimo['chapter']}:{ultimo['verse']}"
            else:
                ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']} a {ultimo['book_name']} {ultimo['chapter']}:{ultimo['verse']}"

            st.markdown(f"**Leitura de hoje:** {ref}")

            # Monta o texto formatado de forma segura (sem f-string)
            texto_limpo = ""
            for v in versiculos:
                # Escapa chaves para não quebrar o HTML/Markdown
                safe_text = str(v['text']).replace("{", "{{").replace("}", "}}")
                texto_limpo += f"**{v['verse']}** {safe_text}  \n"

            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 500px; overflow-y: auto;">
                    <div style="color: #F2F2F2; font-size: 1rem; line-height: 1.8;">
                        {texto_limpo}
                    </div>
                </div>""",
                unsafe_allow_html=True
            )

            if st.button("✅ Confirmar Leitura e Avançar", use_container_width=True):
                execute("UPDATE reading_progress SET completed = 1 WHERE day = ?", (day,))
                st.success(f"Leitura do Dia {day} concluída! Avançando...")
                st.rerun()
        else:
            st.error("Erro ao carregar os versículos. O plano pode estar corrompido.")
    else:
        st.error(f"Plano para o dia {day} não encontrado.")
