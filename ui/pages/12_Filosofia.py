import streamlit as st
import sys
import re
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one
from services.ai import ask_gemini

BASE_DIR = Path(__file__).resolve().parents[2]
ASSETS_DIR = BASE_DIR / "assets"

st.title("🏛️ Filosofia & Sabedoria")

tab_video, tab_debate, tab_gp, tab_gpres = st.tabs([
    "🎬 Aula em Vídeo", 
    "🧠 Debate Socrático", 
    "🕵️ Grimório Proibido", 
    "👑 Grimório da Presença"
])

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

def show_book_tab(filename, book_name):
    filepath = ASSETS_DIR / filename
    if not filepath.exists():
        st.error(f"Arquivo {filename} não encontrado na pasta assets. Rode o script de melhoria novamente.")
        return

    text = filepath.read_text(encoding="utf-8")
    # Divide o texto por "CAPÍTULO" ou "PARTE" ou marcadores de início
    chapters = re.split(r'(?i)\n\s*(?:CAPÍTULO|PARTE|PRÓLOGO|C A P Í T U L O)\s+[IVXLCDM\d]+', text)
    chapters = [c.strip() for c in chapters if len(c.strip()) > 100]
    
    if not chapters:
        st.info("Nenhum capítulo formatado encontrado no texto.")
        return

    state_key = f"idx_{filename}"
    if state_key not in st.session_state:
        st.session_state[state_key] = 0

    idx = st.session_state[state_key]
    if idx >= len(chapters):
        idx = 0
        st.session_state[state_key] = 0

    st.subheader(f"📖 {book_name} — Módulo {idx+1} de {len(chapters)}")
    
    # Área de Leitura
    with st.expander("Ler o texto base deste módulo", expanded=True):
        # Exibe uma versão truncada para não travar a tela, o texto completo fica no contexto da IA
        display_text = chapters[idx][:3000] + "\n\n[...]*(O texto continua, use a IA para aprofundar)*" if len(chapters[idx]) > 3000 else chapters[idx]
        st.markdown(f"<div style='white-space: pre-wrap; line-height: 1.6;'>{display_text}</div>", unsafe_allow_html=True)

    # Navegação
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Módulo Anterior", key=f"prev_{filename}", use_container_width=True):
        st.session_state[state_key] = max(0, idx - 1)
        st.rerun()
    if col2.button("Próximo Módulo ➡️", key=f"next_{filename}", use_container_width=True):
        st.session_state[state_key] = min(len(chapters) - 1, idx + 1)
        st.rerun()

    st.divider()
    
    # Aula com IA
    st.write("#### 🎓 Aula do Mentor")
    if st.button("🧠 Gerar Aula Prática com IA", key=f"ia_{filename}", use_container_width=True):
        with st.spinner("O Mentor está preparando sua aula diária..."):
            prompt = f"""Atue como o mestre e mentor Felipe Alves, ensinando os conceitos dos seus livros.
O usuário está estudando o livro '{book_name}'.
Aqui está o trecho do módulo de hoje:
{chapters[idx][:6000]}

Sua missão:
1. Crie 3 tópicos de reflexão sobre o texto (explicando o conceito de forma clara).
2. Crie 1 exercício prático para o usuário aplicar HOJE na vida real (ex: "Hoje, observe a postura das pessoas no elevador", "Ao conversar com alguém, faça a pausa de 2 segundos antes de responder").
3. Dê uma frase de impacto final, estilo Samurai.
Seja direto, empolgante e prático.
"""
            resposta = ask_gemini(prompt)
            st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Aula: {book_name}</div><div style="white-space: pre-wrap;">{resposta}</div></div>', unsafe_allow_html=True)

with tab_gp:
    show_book_tab("grimorio_proibido.txt", "Grimório Proibido")

with tab_gpres:
    show_book_tab("grimorio_presenca.txt", "Grimório da Presença")
