import streamlit as st
import sys
import re
import tempfile
import os
from pathlib import Path
import fitz  # PyMuPDF

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("🧠 Mente")
st.caption("Leitura guiada, evolução e resumo de conteúdos.")

tab_leitura, tab_youtube = st.tabs(["📚 Livros (PDF)", "📺 Resumo de Vídeos (YouTube)"])

with tab_leitura:
    # --- (O código da aba de livros permanece o mesmo) ---
    st.write("Aba de livros (inalterada).")

with tab_youtube:
    st.header("Resumo de Vídeos do YouTube")
    st.write("Cole o link de um vídeo. Tentaremos pegar as legendas; se não houver, faremos a transcrição do áudio.")

    video_url = st.text_input("URL do Vídeo:", placeholder="https://www.youtube.com/watch?v=...")

    if st.button("📺 Extrair Leitura do Vídeo", use_container_width=True):
        if not video_url:
            st.warning("Cole uma URL válida.")
        else:
            with st.spinner("Processando vídeo... Isso pode levar alguns minutos se precisarmos transcrever o áudio."):
                try:
                    # 1. Tenta extrair ID do vídeo
                    video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url).group(1)

                    # 2. Tenta obter legendas
                    texto_video = ""
                    try:
                        from youtube_transcript_api import YouTubeTranscriptApi
                        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
                        texto_video = " ".join([t['text'] for t in transcript])
                        st.toast("Legendas encontradas! Usando transcrição rápida.")
                    except Exception:
                        st.toast("Nenhuma legenda encontrada. Iniciando transcrição por áudio (Whisper)...")
                        # 3. Fallback: Baixa áudio com yt-dlp e transcreve com faster-whisper
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

                            # Carrega o modelo Whisper (o modelo "small" é um bom equilíbrio)
                            model = WhisperModel("small", device="cpu", compute_type="int8")
                            segments, info = model.transcribe(audio_path, beam_size=5, language="pt")
                            texto_video = " ".join([segment.text for segment in segments])
                            st.toast("Transcrição por áudio concluída!")

                    # 4. Gera o resumo com a IA
                    if texto_video:
                        texto_video = texto_video[:15000]  # Limita para não estourar tokens
                        prompt = f"Atue como um analista de conteúdo. Transforme a transcrição abaixo em um artigo/leitura executiva, destacando os principais pontos em tópicos. Transcrição:\n\n{texto_video}"
                        resumo_youtube = ask_gemini(prompt)
                        st.session_state["resumo_youtube"] = resumo_youtube
                    else:
                        st.error("Não foi possível obter o texto do vídeo.")

                except Exception as e:
                    st.error(f"Erro ao processar: {e}")

    if st.session_state.get("resumo_youtube"):
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #FF0000;">
            <div class="titulo">Resumo do Vídeo</div>
            <div style="color: #F2F2F2; white-space: pre-wrap; line-height: 1.6;">{st.session_state['resumo_youtube']}</div>
        </div>""", unsafe_allow_html=True)
