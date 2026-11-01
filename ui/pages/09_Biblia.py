import streamlit as st
import sys
from pathlib import Path
from gtts import gTTS
import io

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db
from services.ai import ask_gemini

init_db()

st.title("📖 Bíblia & Inglês")
st.caption("Plano de leitura em 1 ano + Aprendizado de Inglês Cristão")

proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")

if not proximo:
    st.success("🎉 Parabéns! Você concluiu a leitura da Bíblia em 1 ano!")
else:
    day = proximo["day"]
    st.subheader(f"Dia {day} de 365")

    plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
    if plano:
        versiculos = query_all(
            "SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id",
            (plano["start_verse_id"], plano["end_verse_id"])
        )

        if versiculos:
            primeiro = versiculos[0]
            ultimo = versiculos[-1]
            ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']}"
            
            st.markdown(f"**Leitura de hoje:** {ref}")

            texto_limpo, texto_bruto = "", ""
            for v in versiculos:
                safe_text = str(v['text']).replace("{", "{{").replace("}", "}}")
                texto_limpo += f"**{v['verse']}** {safe_text}  \n"
                texto_bruto += f"{v['verse']} {v['text']} "

            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 300px; overflow-y: auto;">
                    <div style="color: #F2F2F2; font-size: 1rem; line-height: 1.8;">{texto_limpo}</div>
                </div>""", unsafe_allow_html=True
            )

            # === MELHORIA: INGLÊS DESTRA ===
            st.divider()
            st.subheader("🇺🇸 Aprender Inglês com a Palavra")
            st.write("Expanda seu vocabulário usando este versículo como base.")
            
            if st.button("🪄 Traduzir e Explicar em Inglês", use_container_width=True):
                with st.spinner("O Mentor está preparando sua aula de inglês..."):
                    prompt = f"""Atue como um professor de inglês cristão (metodologia Destra for the Nations).
Baseado no versículo: "{texto_bruto}"
Forneça:
1. A tradução oficial para o inglês.
2. Três palavras-chave em inglês que aparecem no versículo (com pronúncia aproximada e significado).
3. Uma explicação gramatical simples sobre a estrutura da frase em inglês.
4. Uma mini-frase motivacional em inglês para o usuário praticar a leitura.
Seja didático e encorajador."""
                    aula_en = ask_gemini(prompt)
                    st.session_state["aula_ingles"] = aula_en

            if st.session_state.get("aula_ingles"):
                st.markdown(
                    f"""<div class="samurai-card" style="border-left-color: #2196F3;">
                        <div class="titulo" style="color: #2196F3;">Class is in session</div>
                        <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{st.session_state['aula_ingles']}</div>
                    </div>""", unsafe_allow_html=True
                )

            # --- BOTÕES DE AÇÃO ---
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Concluir Leitura", use_container_width=True):
                    execute("UPDATE reading_progress SET completed = 1 WHERE day = ?", (day,))
                    st.rerun()
            with col2:
                if st.button("🔊 Ouvir Áudio", use_container_width=True):
                    with st.spinner("Gerando áudio..."):
                        tts = gTTS(text=texto_bruto, lang='pt', slow=False)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        st.audio(fp.getvalue(), format="audio/mp3")

            if st.session_state.get("aula_ingles"):
                # Não é necessário repetir o botão de áudio
                pass
