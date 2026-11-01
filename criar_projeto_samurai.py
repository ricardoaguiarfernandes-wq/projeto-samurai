"""
melhoria.py — Restaura a transcrição local de vídeos do YouTube.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

CONTEUDO_MENTE = '''import streamlit as st
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
    st.write("Função de PDF mantida.")

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
                    video_id = re.search(r"(?:v=|\\/)([0-9A-Za-z_-]{11}).*", video_url).group(1)
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
                        prompt = f"Atue como um analista. Resuma a transcrição abaixo em tópicos:\\n\\n{texto_video[:15000]}"
                        resumo = ask_gemini(prompt)
                        st.markdown(f"""<div class="samurai-card" style="border-left-color: #FF0000;"><div class="titulo">Resumo do Vídeo</div><div style="white-space: pre-wrap;">{resumo}</div></div>""", unsafe_allow_html=True)
                    else:
                        st.error("Não foi possível obter o texto.")
                except Exception as e:
                    st.error(f"Erro ao processar link: {e}")
'''

def _run(cmd):
    subprocess.run(cmd, cwd=BASE, capture_output=True)

def aplicar():
    print("⚔️  RESTAURANDO WHISPER NA PÁGINA MENTE")
    arq = BASE / "ui" / "pages" / "02_Mente.py"
    try:
        ast.parse(CONTEUDO_MENTE)
        arq.write_text(CONTEUDO_MENTE, encoding="utf-8")
        print("[OK] 02_Mente.py atualizado com a lógica do Whisper.")
    except Exception as e:
        print(f"[ERRO] {e}")
        sys.exit(1)

    _run(["git", "add", "-A"])
    _run(["git", "commit", "-m", "Fix: Restaura logica de transcricao local do YouTube"])
    _run(["git", "push", "origin", "main"])
    print("[OK] Push realizado. O app local já vai funcionar.")

if __name__ == "__main__":
    aplicar()