import streamlit as st
import sys
import re
import tempfile
import os
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
    st.write("Faça o upload de um livro em PDF para extrair o texto e gerar um resumo com a IA.")
    uploaded_file = st.file_uploader("Envie seu PDF", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("📚 Extrair Texto e Resumir com IA", use_container_width=True):
            with st.spinner("Lendo e processando PDF (pode demorar um pouco)..."):
                try:
                    import fitz
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    
                    if text.strip():
                        prompt = f"Atue como um estudioso e mentor. Resuma os principais pontos do seguinte texto extraído de um livro:\n\n{text[:20000]}"
                        resumo = ask_gemini(prompt)
                        st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Resumo do Livro</div><div style="white-space: pre-wrap;">{resumo}</div></div>', unsafe_allow_html=True)
                    else:
                        st.warning("O PDF não contém texto legível (pode ser apenas imagens escaneadas).")
                except ImportError:
                    st.error("A biblioteca 'pymupdf' não está instalada. Rode: pip install pymupdf")
                except Exception as e:
                    st.error(f"Erro ao ler o PDF: {e}")

with tab_youtube:
    st.header("Resumo de Vídeos do YouTube")
    st.write("Cole o link do vídeo. O app tentará baixar a legenda; se não houver, ele fará a transcrição do áudio no seu PC.")
    
    video_url = st.text_input("URL do Vídeo:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("📺 Extrair Leitura do Vídeo", use_container_width=True):
        if not video_url:
            st.warning("Cole uma URL.")
        else:
            with st.spinner("Processando vídeo... (Se precisar transcrever o áudio, pode demorar alguns minutos)"):
                try:
                    video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url).group(1)
                    texto_video = ""
                    
                    # 1. Tenta as legendas normais
                    try:
                        from youtube_transcript_api import YouTubeTranscriptApi
                        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
                        texto_video = " ".join([t['text'] for t in transcript])
                        st.toast("Legendas encontradas! Resumo rápido.")
                    except Exception:
                        st.toast("Sem legendas. Iniciando transcrição por áudio (Whisper)...")
                        # 2. Tenta baixar o áudio e transcrever
                        try:
                            import yt_dlp
                            from faster_whisper import WhisperModel

                            with tempfile.TemporaryDirectory() as tmpdir:
                                ydl_opts = {
                                    'format': 'bestaudio/best',
                                    'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
                                    'quiet': True,
                                    'noplaylist': True,
                                }
                                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                    info = ydl.extract_info(video_url, download=True)
                                    audio_path = os.path.join(tmpdir, f"{info['id']}.{info['ext']}")

                                # Modelo "small" para não pesar o PC
                                model = WhisperModel("small", device="cpu", compute_type="int8")
                                segments, info = model.transcribe(audio_path, beam_size=5, language="pt")
                                texto_video = " ".join([segment.text for segment in segments])
                                st.toast("Transcrição concluída!")
                        except ImportError:
                            st.error("Bibliotecas 'yt-dlp' ou 'faster-whisper' não instaladas. Rode: pip install yt-dlp faster-whisper")
                            st.stop()
                        except Exception as e:
                            st.error(f"Erro na transcrição do áudio (O FFmpeg está instalado?): {e}")
                            st.stop()
                    
                    if texto_video:
                        prompt = f"Atue como um analista. Resuma a transcrição abaixo em tópicos:\n\n{texto_video[:15000]}"
                        resumo = ask_gemini(prompt)
                        st.markdown(f"""<div class="samurai-card" style="border-left-color: #FF0000;"><div class="titulo">Resumo do Vídeo</div><div style="white-space: pre-wrap;">{resumo}</div></div>""", unsafe_allow_html=True)
                    else:
                        st.error("Não foi possível obter o texto.")
                except Exception as e:
                    st.error(f"Erro ao processar link: {e}")
