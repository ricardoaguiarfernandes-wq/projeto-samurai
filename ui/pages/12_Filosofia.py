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

def divide_em_30_dias(texto):
    """Divide o texto em exatamente 30 partes proporcionais, cortando nos espaços."""
    total_caracteres = len(texto)
    chars_por_dia = total_caracteres // 30
    partes = []
    inicio = 0
    
    for i in range(30):
        if i == 29: # O último dia pega todo o resto
            fim = total_caracteres
        else:
            fim = inicio + chars_por_dia
            # Avança até o próximo espaço para não cortar palavras
            while fim < total_caracteres and not texto[fim].isspace():
                fim += 1
                
        partes.append(texto[inicio:fim].strip())
        inicio = fim
        
    return partes

def show_book_tab(filename, book_name):
    filepath = ASSETS_DIR / filename
    if not filepath.exists():
        st.error(f"Arquivo {filename} não encontrado na pasta assets.")
        return

    text = filepath.read_text(encoding="utf-8")
    
    # Usa a nova divisão por volume de texto
    dias = divide_em_30_dias(text)
    
    state_key = f"idx_{filename}"
    if state_key not in st.session_state:
        st.session_state[state_key] = 0

    idx = st.session_state[state_key]
    if idx >= len(dias):
        idx = 0
        st.session_state[state_key] = 0

    st.subheader(f"📖 {book_name} — Dia {idx+1} de 30")
    
    # Área de Leitura
    with st.expander("Ler o texto base de hoje", expanded=True):
        display_text = dias[idx]
        st.markdown(f"<div style='white-space: pre-wrap; line-height: 1.6;'>{display_text}</div>", unsafe_allow_html=True)

    # Navegação
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Dia Anterior", key=f"prev_{filename}", use_container_width=True):
        st.session_state[state_key] = max(0, idx - 1)
        st.rerun()
    if col2.button("Próximo Dia ➡️", key=f"next_{filename}", use_container_width=True):
        st.session_state[state_key] = min(len(dias) - 1, idx + 1)
        st.rerun()

    st.divider()
    
    # Aula com IA
    st.write("#### 🎓 Aula do Mentor")
    if st.button("🧠 Gerar Aula Prática com IA", key=f"ia_{filename}", use_container_width=True):
        with st.spinner("O Mentor está preparando sua aula diária..."):
            prompt = f"""Atue como o mestre e mentor Felipe Alves, ensinando os conceitos dos seus livros.
O usuário está estudando o livro '{book_name}', no dia {idx+1} de 30.
Aqui está o trecho da leitura de hoje:
{dias[idx][:6000]}

Sua missão:
1. Crie 3 tópicos de reflexão sobre o texto (explicando o conceito de forma clara).
2. Crie 1 exercício prático para o usuário aplicar HOJE na vida real (ex: "Hoje, observe a postura das pessoas no elevador", "Ao conversar com alguém, faça a pausa de 2 segundos antes de responder").
3. Dê uma frase de impacto final, estilo Samurai.
Seja direto, empolgante e prático.
"""
            resposta = ask_gemini(prompt)
            st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Aula do Dia {idx+1}</div><div style="white-space: pre-wrap;">{resposta}</div></div>', unsafe_allow_html=True)

with tab_gp:
    show_book_tab("grimorio_proibido.txt", "Grimório Proibido")

with tab_gpres:
    show_book_tab("grimorio_presenca.txt", "Grimório da Presença")
