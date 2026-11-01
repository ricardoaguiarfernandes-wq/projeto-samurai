import streamlit as st
import sys
from pathlib import Path
import re
import pymupdf as fitz  # PyMuPDF atualizado
import time

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db
from services.ai import ask_gemini, ask_gemini_vision

init_db()
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

# --- UPLOAD DE PDF ---
with st.expander("📚 Enviar Novo Livro (PDF)", expanded=False):
    uploaded_file = st.file_uploader("Selecione o PDF do livro", type=["pdf"])
    palavras_por_dia = st.number_input("Meta de leitura diária (palavras)", min_value=200, max_value=5000, value=1000, step=100)
    
    usar_ocr = st.checkbox("Usar OCR com IA (Recomendado se o texto sair embaralhado)", value=False, 
                           help="O app vai transformar as páginas em imagens e pedir para o Gemini ler. Demora um pouco mais, mas o texto fica perfeito.")
    
    if uploaded_file and st.button("Processar PDF e Criar Plano"):
        with st.spinner("Extraindo texto..."):
            try:
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                full_text = ""
                
                if usar_ocr:
                    st.warning("A IA está lendo cada página. O processo pausa 4 segundos entre páginas para não exceder o limite da API gratuita. Por favor, aguarde...")
                    progresso = st.progress(0)
                    total_paginas = len(doc)
                    
                    for i, page in enumerate(doc):
                        pix = page.get_pixmap(dpi=150)
                        img_bytes = pix.tobytes("jpeg")
                        
                        prompt = "Extraia exatamente o texto desta imagem, mantendo a pontuação e parágrafos. Não adicione comentários, retorne apenas o texto do livro."
                        texto_pagina = ask_gemini_vision(img_bytes, prompt)
                        
                        # Se houver erro na IA, avisa o usuário e para o loop
                        if "⚠️" in texto_pagina:
                            st.error(f"Falha na página {i+1}: {texto_pagina}")
                            break
                            
                        full_text += texto_pagina + " "
                        progresso.progress((i + 1) / total_paginas)
                        
                        # Pausa de 4 segundos para respeitar o rate limit (15 RPM do Gemini)
                        time.sleep(4) 
                else:
                    for page in doc:
                        extracted = page.get_text("text")
                        if extracted:
                            full_text += extracted + " "
                
                full_text = re.sub(r'\s+', ' ', full_text)
                palavras = full_text.split()
                
                if len(palavras) < 100:
                    st.error("O PDF não pôde ser lido. O limite da API pode ter sido atingido ou o PDF está protegido. Tente novamente mais tarde.")
                else:
                    book_title = uploaded_file.name.replace(".pdf", "")
                    execute("DELETE FROM book_chunks WHERE book_title = ?", (book_title,))
                    
                    chunks = []
                    for i in range(0, len(palavras), palavras_por_dia):
                        chunk_text = " ".join(palavras[i:i + palavras_por_dia])
                        chunks.append(chunk_text)
                    
                    for idx, texto_chunk in enumerate(chunks):
                        execute(
                            "INSERT INTO book_chunks (book_title, chunk_index, text_content) VALUES (?, ?, ?)",
                            (book_title, idx, texto_chunk)
                        )
                    
                    st.success(f"[OK] '{book_title}' processado! {len(chunks)} dias de leitura gerados.")
                    time.sleep(1)
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao ler o PDF: {e}")

st.divider()

# --- LEITURA DO DIA ---
livro_ativo = query_one("SELECT book_title FROM book_chunks WHERE completed = 0 ORDER BY id ASC LIMIT 1")

if livro_ativo:
    book_title = livro_ativo["book_title"]
    chunk = query_one(
        "SELECT * FROM book_chunks WHERE book_title = ? AND completed = 0 ORDER BY chunk_index ASC LIMIT 1",
        (book_title,)
    )
    
    if chunk:
        total_chunks = query_one("SELECT COUNT(*) AS c FROM book_chunks WHERE book_title = ?", (book_title,))["c"]
        st.subheader(f"📖 {book_title}")
        st.caption(f"Leitura {chunk['chunk_index'] + 1} de {total_chunks}")
        
        with st.container():
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #8B0000; max-height: 500px; overflow-y: auto;">
                    <div style="color: #F2F2F2; font-size: 1.05rem; line-height: 1.8; text-align: justify;">
                        {chunk['text_content']}
                    </div>
                </div>""",
                unsafe_allow_html=True
            )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✅ Concluir Leitura de Hoje", use_container_width=True):
                execute("UPDATE book_chunks SET completed = 1 WHERE id = ?", (chunk["id"],))
                st.session_state["resumo_pdf"] = ""
                st.rerun()
        with col2:
            if st.button("🪄 Resumo com IA", use_container_width=True):
                with st.spinner("O Mentor está resumindo o texto de hoje..."):
                    prompt = f"Resuma o seguinte trecho de um livro de forma inspiradora e direta, destacando os principais aprendizados:\n\n{chunk['text_content']}"
                    resumo = ask_gemini(prompt)
                    st.session_state["resumo_pdf"] = resumo
        
        if st.session_state.get("resumo_pdf"):
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
                    <div class="titulo">Resumo do Mentor</div>
                    <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6;">{st.session_state['resumo_pdf']}</div>
                </div>""",
                unsafe_allow_html=True
            )
else:
    st.info("📖 Nenhum livro em andamento. Envie um PDF na seção acima para começar.")
