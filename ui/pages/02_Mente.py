import streamlit as st
import sys
import re
import tempfile
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

# Abas para organizar
tab_leitura, tab_youtube = st.tabs(["📚 Livros (PDF)", "📺 Resumo de Vídeos (YouTube)"])

with tab_leitura:
    # --- IMPORTAR PDF DO TERABOX ---
    with st.expander("📚 Importar Livro do Terabox (PDF -> Texto)", expanded=False):
        link_pdf = st.text_input("Link do PDF no Terabox:")
        palavras_por_dia = st.number_input("Meta de leitura diária (palavras)", min_value=200, max_value=5000, value=1000, step=100)

        if link_pdf and st.button("Processar PDF do Terabox", use_container_width=True):
            with st.spinner("Baixando e processando PDF..."):
                try:
                    from TeraboxDL import TeraboxDL
                    cookie = st.secrets.get("TERABOX_COOKIE", "")
                    if not cookie:
                        st.error("Cookie do Terabox não configurado nos Secrets.")
                        st.stop()

                    terabox = TeraboxDL(cookie)
                    file_info = terabox.get_file_info(link_pdf)
                    if "error" in file_info:
                        st.error(f"Erro: {file_info['error']}")
                        st.stop()

                    with tempfile.TemporaryDirectory() as tmpdir:
                        result = terabox.download(file_info, save_path=tmpdir)
                        if "error" in result:
                            st.error(f"Erro: {result['error']}")
                            st.stop()
                        
                        doc = fitz.open(result["file_path"])
                        full_text = " ".join([page.get_text("text") for page in doc])
                        doc.close()
                        
                        full_text = re.sub(r'\s+', ' ', full_text)
                        palavras = full_text.split()

                        if len(palavras) < 100:
                            st.error("PDF sem texto suficiente.")
                        else:
                            book_title = file_info["file_name"].replace(".pdf", "")
                            execute("DELETE FROM book_chunks WHERE book_title = ?", (book_title,))
                            
                            chunks = [" ".join(palavras[i:i + palavras_por_dia]) for i in range(0, len(palavras), palavras_por_dia)]
                            for idx, texto_chunk in enumerate(chunks):
                                execute("INSERT INTO book_chunks (book_title, chunk_index, text_content) VALUES (?, ?, ?)", (book_title, idx, texto_chunk))
                            
                            st.success(f"[OK] '{book_title}' importado! {len(chunks)} dias gerados.")
                            st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

    st.divider()

    # --- LEITURA DO DIA ---
    livro_ativo = query_one("SELECT book_title FROM book_chunks WHERE completed = 0 ORDER BY id ASC LIMIT 1")
    if livro_ativo:
        book_title = livro_ativo["book_title"]
        chunk = query_one("SELECT * FROM book_chunks WHERE book_title = ? AND completed = 0 ORDER BY chunk_index ASC LIMIT 1", (book_title,))
        
        if chunk:
            total_chunks = query_one("SELECT COUNT(*) AS c FROM book_chunks WHERE book_title = ?", (book_title,))["c"]
            st.subheader(f"📖 {book_title}")
            st.caption(f"Leitura {chunk['chunk_index'] + 1} de {total_chunks}")
            
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; max-height: 500px; overflow-y: auto;">
                <div style="color: #F2F2F2; line-height: 1.8;">{chunk['text_content']}</div>
            </div>""", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Concluir Leitura", use_container_width=True):
                    execute("UPDATE book_chunks SET completed = 1 WHERE id = ?", (chunk["id"],))
                    st.rerun()
            with col2:
                if st.button("🪄 Resumo com IA", use_container_width=True):
                    with st.spinner("Resumindo..."):
                        st.session_state["resumo_pdf"] = ask_gemini(f"Resuma: \n\n{chunk['text_content']}")
            
            if st.session_state.get("resumo_pdf"):
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;">
                    <div class="titulo">Resumo do Mentor</div>
                    <div style="color: #F2F2F2;">{st.session_state['resumo_pdf']}</div>
                </div>""", unsafe_allow_html=True)
    else:
        st.info("📖 Nenhum livro em andamento.")

# ==============================================================================
# NOVA ABA: RESUMO DE YOUTUBE
# ==============================================================================
with tab_youtube:
    st.header("Resumo de Vídeos do YouTube")
    st.write("Cole o link de um vídeo (ex: canais de geopolítica, militar, filosofia) e a IA extrairá a transcrição e criará um texto para leitura diária.")
    
    video_url = st.text_input("URL do Vídeo:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("📺 Extrair Leitura do Vídeo", use_container_width=True):
        if not video_url:
            st.warning("Cole uma URL válida.")
        else:
            with st.spinner("Baixando transcrição e preparando leitura..."):
                try:
                    from youtube_transcript_api import YouTubeTranscriptApi
                    # Extrai o ID do vídeo
                    video_id = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url).group(1)
                    
                    # Tenta pegar transcrição em PT ou EN
                    try:
                        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
                    except:
                        st.error("Este vídeo não possui legendas/transcrição disponíveis.")
                        st.stop()
                        
                    texto_video = " ".join([t['text'] for t in transcript])
                    
                    # Limita o tamanho para não estourar tokens da API
                    texto_video = texto_video[:15000] 
                    
                    prompt = f"""Atue como um analista de conteúdo.
                    Abaixo está a transcrição de um vídeo. Transforme isso em um artigo/leitura executiva.
                    Destaque os principais pontos, ideias e conclusões em tópicos. Seja direto e informativo.
                    
                    Transcrição:
                    {texto_video}
                    """
                    resumo_youtube = ask_gemini(prompt)
                    st.session_state["resumo_youtube"] = resumo_youtube
                    
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")
                    
    if st.session_state.get("resumo_youtube"):
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #FF0000;">
            <div class="titulo">Resumo do Vídeo</div>
            <div style="color: #F2F2F2; white-space: pre-wrap; line-height: 1.6;">{st.session_state['resumo_youtube']}</div>
        </div>""", unsafe_allow_html=True)
