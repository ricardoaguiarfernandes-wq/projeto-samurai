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

            # Monta o texto formatado de forma segura
            texto_limpo = ""
            texto_bruto = ""
            for v in versiculos:
                safe_text = str(v['text']).replace("{", "{{").replace("}", "}}")
                texto_limpo += f"**{v['verse']}** {safe_text}  \n"
                texto_bruto += f"{v['verse']} {v['text']} "

            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 400px; overflow-y: auto;">
                    <div style="color: #F2F2F2; font-size: 1rem; line-height: 1.8;">
                        {texto_limpo}
                    </div>
                </div>""",
                unsafe_allow_html=True
            )

            # Botões de Ação
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Concluir Leitura", use_container_width=True):
                    execute("UPDATE reading_progress SET completed = 1 WHERE day = ?", (day,))
                    st.success("Leitura concluída! Avançando...")
                    st.rerun()
            with col2:
                if st.button("🔊 Ouvir Áudio", use_container_width=True):
                    with st.spinner("Gerando áudio..."):
                        tts = gTTS(text=texto_bruto, lang='pt', slow=False)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        st.session_state["audio_biblia"] = fp.getvalue()
            with col3:
                if st.button("🧠 Explicar com IA", use_container_width=True):
                    with st.spinner("O Mentor está analisando o texto..."):
                        prompt = f"Explique o seguinte trecho bíblico de forma simples, destacando o contexto histórico e uma aplicação prática para o dia a dia de um homem moderno focado em evolução:\n\n{texto_bruto}"
                        explicacao = ask_gemini(prompt)
                        st.session_state["explicacao_biblia"] = explicacao

            if st.session_state.get("audio_biblia"):
                st.audio(st.session_state["audio_biblia"], format="audio/mp3")

            if st.session_state.get("explicacao_biblia"):
                st.markdown(
                    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 15px;">
                        <div class="titulo">Visão do Mentor</div>
                        <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{st.session_state['explicacao_biblia']}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

            # Reflexão do Trecho
            st.divider()
            with st.form("form_reflexao_biblia"):
                st.markdown("**✍️ Sua Reflexão sobre o Trecho**")
                reflexao = st.text_area("O que esta leitura falou com você?", placeholder="Escreva aqui...")
                if st.form_submit_button("Salvar Reflexão", use_container_width=True):
                    if reflexao.strip():
                        execute(
                            "INSERT INTO journal_entries (entry_date, prompt, content) VALUES (?, ?, ?)",
                            (date.today().isoformat(), f"Reflexão Bíblica: {ref}", reflexao.strip())
                        )
                        st.success("Reflexão salva no seu diário!")
                    else:
                        st.error("Escreva algo antes de salvar.")

        else:
            st.error("Erro ao carregar os versículos. O plano pode estar corrompido.")
    else:
        st.error(f"Plano para o dia {day} não encontrado.")


# --- VERSÍCULO ALEATÓRIO ---
st.divider()
st.subheader("🎲 Versículo Aleatório")
st.write("Precisa de uma palavra extra? Sorteie um versículo de qualquer parte da Bíblia.")

if st.button("Sortear Versículo", use_container_width=True):
    with st.spinner("Buscando uma palavra..."):
        # Busca um versículo aleatório no banco (funciona no SQLite e no Postgres)
        v_aleatorio = query_one("SELECT book_name, chapter, verse, text FROM bible_verses ORDER BY RANDOM() LIMIT 1")
        if v_aleatorio:
            st.session_state["verso_aleatorio"] = v_aleatorio

if st.session_state.get("verso_aleatorio"):
    v_rand = st.session_state["verso_aleatorio"]
    ref_rand = f"{v_rand['book_name']} {v_rand['chapter']}:{v_rand['verse']}"
    
    st.markdown(
        f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
            <div class="titulo">{ref_rand}</div>
            <div class="valor" style="font-size: 1.1rem; font-style: italic; color: #F2F2F2;">"{v_rand['text']}"</div>
        </div>""",
        unsafe_allow_html=True,
    )
