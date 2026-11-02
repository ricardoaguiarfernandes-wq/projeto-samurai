import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("🏛️ Filosofia & Sabedoria")

tab_video, tab_debate = st.tabs(["🎬 Aula em Vídeo", "🧠 Debate Socrático"])

with tab_video:
    st.header("Assistir Aula (COF ou outros)")
    video_link = st.text_input("Cole o link do vídeo (YouTube):", placeholder="https://www.youtube.com/watch?v=...")
    if video_link:
        try:
            st.video(video_link)
            if st.button("🧠 Resumir Aula com IA", use_container_width=True):
                with st.spinner("Preparando resumo..."):
                    prompt = f"Atue como professor de filosofia. Crie um resumo dos principais conceitos e 3 perguntas de reflexão sobre a aula contida no link: {video_link}"
                    st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)
        except:
            st.error("Link de vídeo inválido.")

with tab_debate:
    st.header("Desafio Intelectual do Dia")
    PROMPTS = ["O que é a verdadeira ignorância: não saber, ou saber e não aplicar?", "O que a sua rotina diz sobre a sua visão de mundo?", "Como a ordem no ambiente físico reflete a ordem da mente?"]
    prompt_hoje = PROMPTS[date.today().toordinal() % len(PROMPTS)]
    st.markdown(f"""<div class="samurai-card"><div class="titulo">Reflexão</div><div class="valor" style="font-size:1.2rem;">{prompt_hoje}</div></div>""", unsafe_allow_html=True)
    
    with st.form("form_fil"):
        refl = st.text_area("Sua resposta:")
        if st.form_submit_button("Debater com Mentor", use_container_width=True) and refl:
            with st.spinner("Analisando..."):
                prompt = f"Atue como mentor COF. Tema: '{prompt_hoje}'. Usuário disse: '{refl}'. Aponte uma falha lógica e faça 1 pergunta socrática."
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;"><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)
