import streamlit as st
import sys
import re
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("🧠 Mente")
tab_leitura, tab_youtube = st.tabs(["📚 Livros (PDF)", "📺 Resumo de Vídeos (YouTube)"])

with tab_leitura:
    st.write("Função de PDF mantida.")

with tab_youtube:
    st.header("Resumo de Vídeos do YouTube")
    video_url = st.text_input("URL do Vídeo:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("📺 Extrair Leitura do Vídeo", use_container_width=True):
        if not video_url:
            st.warning("Cole uma URL.")
        else:
            with st.spinner("Processando..."):
                try:
                    video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url).group(1)
                    try:
                        from youtube_transcript_api import YouTubeTranscriptApi
                        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
                        texto_video = " ".join([t['text'] for t in transcript])
                        st.toast("Legendas encontradas!")
                    except Exception:
                        st.error("Vídeo sem legendas. A transcrição por áudio (Whisper) requer instalação local. Rode o projeto no seu PC via INICIAR.bat para usar esse recurso.")
                        st.stop()
                        
                    prompt = f"Resuma em tópicos:\n{texto_video[:15000]}"
                    st.markdown(f"""<div class="samurai-card" style="border-left-color: #FF0000;"><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Erro: {e}")
