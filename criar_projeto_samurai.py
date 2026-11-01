"""
melhoria.py — Aplica melhorias no Projeto Samurai.
Nesta versão: 
- Corrige plano vazio na Bíblia.
- Adiciona Devocional Diário Automático.
- Adiciona gerenciamento de Louvores.
- Expande Blocos de Palavras-Chave.
- Adiciona extrator de resumos do YouTube na Mente.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

# =============================================================================
# CONFIG
# =============================================================================
BASE = Path(__file__).resolve().parent
WINDOW_TITLE   = "Projeto Samurai"
PADROES_SECRETOS = [
    re.compile(r"AQ\.Ab8RN6[A-Za-z0-9_\-]{20,}"),
    re.compile(r"postgresql://[^:\s]+:[^@\s]+@"),
]
ARQUIVOS_PROIBIDOS = {"config.json", ".env", "secrets.toml"}
PREFIXO_MD_GERADO = "PROJETO_SAMURAI"

# =============================================================================
# CONTEÚDO DA BÍBLIA (Atualizado)
# =============================================================================
NOVO_CONTEUDO_BIBLIA = '''import streamlit as st
import sys
from pathlib import Path
from gtts import gTTS
import io
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db, setup_biblia
from services.ai import ask_gemini

init_db()

st.title("📖 Bíblia, Inglês & Filosofia")

# Inicializa o plano caso esteja vazio
count_prog = query_one("SELECT COUNT(*) AS c FROM reading_progress")["c"]
if count_prog == 0:
    with st.spinner("Iniciando o plano de leitura..."):
        for day in range(1, 366):
            execute("INSERT INTO reading_progress (day, completed) VALUES (?, 0)", (day,))
    st.rerun()

tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Plano Anual", 
    "🇺🇸 Devocional Bilíngue", 
    "🎵 Inglês com Louvores", 
    "🔑 Palavras-Chave (1.500)"
])

# ==============================================================================
# ABA 1: PLANO ANUAL DE LEITURA
# ==============================================================================
with tab1:
    proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")
    
    if not proximo:
        st.success("🎉 Parabéns! Você concluiu a leitura da Bíblia em 1 ano!")
    else:
        day = proximo["day"]
        st.subheader(f"Dia {day} de 365")

        plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
        
        # CORREÇÃO: Se o plano estiver vazio na nuvem, recria na hora
        if not plano:
            st.warning("O plano de leitura não foi gerado corretamente (provavelmente por timeout).")
            if st.button("🔄 Gerar Plano de Leitura Agora", use_container_width=True):
                with st.spinner("Baixando a Bíblia e gerando o plano (pode levar 1-2 min)..."):
                    setup_biblia()
                st.success("Plano gerado com sucesso!")
                st.rerun()
        else:
            versiculos = query_all(
                "SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id",
                (plano["start_verse_id"], plano["end_verse_id"])
            )

            if versiculos:
                primeiro = versiculos[0]
                ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']}"
                st.markdown(f"**Leitura de hoje:** {ref}")

                texto_limpo, texto_bruto = "", ""
                for v in versiculos:
                    safe_text = str(v['text']).replace("{", "{{").replace("}", "}}")
                    texto_limpo += f"**{v['verse']}** {safe_text}  \\n"
                    texto_bruto += f"{v['verse']} {v['text']} "

                st.markdown(
                    f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 300px; overflow-y: auto;">
                        <div style="color: #F2F2F2; font-size: 1rem; line-height: 1.8;">{texto_limpo}</div>
                    </div>""", unsafe_allow_html=True
                )

                st.divider()
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Concluir Leitura", use_container_width=True):
                        execute("UPDATE reading_progress SET completed = 1 WHERE day = ?", (day,))
                        st.rerun()
                with col2:
                    if st.button("🔊 Ouvir Áudio (PT)", use_container_width=True):
                        with st.spinner("Gerando áudio..."):
                            tts = gTTS(text=texto_bruto, lang='pt', slow=False)
                            fp = io.BytesIO()
                            tts.write_to_fp(fp)
                            fp.seek(0)
                            st.audio(fp.getvalue(), format="audio/mp3")

# ==============================================================================
# ABA 2: DEVOCIONAL BILÍNGUE (AUTOMÁTICO)
# ==============================================================================
with tab2:
    st.header("Devocional Diário Automático")
    st.write("Um novo devocional gerado todos os dias para fortalecer sua fé.")
    
    temas = ["Amor ao Próximo", "Integridade e Caráter", "Fé em Tempos Difíceis", "Sabedoria e Decisões", "Gratidão e Contentamento"]
    # Escolhe o tema com base no dia do ano
    tema_hoje = temas[date.today().toordinal() % len(temas)]
    
    st.info(f"**Tema de Hoje:** {tema_hoje}")
    
    @st.cache_data(ttl=86400, show_spinner=False) # Cache de 24h para não gastar API à toa
    def gerar_devocional(tema):
        prompt = f"""Atue como um mentor cristão bilíngue. Crie um devocional curto sobre o tema "{tema}".
        Estrutura: 
        1. Versículo Base (PT/EN)
        2. Reflexão (PT) sobre viver e influenciar com valores bíblicos.
        3. English Practice: 3 palavras do versículo e uma frase de aplicação em inglês."""
        return ask_gemini(prompt)

    if st.button("🪄 Gerar Devocional de Hoje", use_container_width=True):
        with st.spinner("Preparando devocional..."):
            devocional = gerar_devocional(tema_hoje)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;">
                <div class="titulo">Devocional: {tema_hoje}</div>
                <div style="color: #F2F2F2; white-space: pre-wrap;">{devocional}</div>
            </div>""", unsafe_allow_html=True)

# ==============================================================================
# ABA 3: INGLÊS COM LOUVORES (ADICIONAR MÚSICAS)
# ==============================================================================
with tab3:
    st.header("Aprenda Inglês com Louvores")
    
    # Gerenciamento de músicas no session_state
    if "louvores" not in st.session_state:
        st.session_state["louvores"] = ["Because He Lives", "How Great Thou Art", "I Speak Jesus", "Holy Forever"]
        
    with st.expander("➕ Adicionar Novo Louvor"):
        nova_musica = st.text_input("Nome da música:")
        if st.button("Adicionar à Lista") and nova_musica:
            st.session_state["louvores"].append(nova_musica)
            st.rerun()
            
    musica = st.selectbox("Escolha um louvor para estudar:", st.session_state["louvores"])
    
    if st.button("🎵 Analisar Louvor com IA", use_container_width=True):
        with st.spinner("Analisando a letra..."):
            prompt = f"Atue como professor de inglês e teólogo. Analise o louvor '{musica}'. Forneça: 1. Refrão em inglês; 2. 4 palavras-chave; 3. Teologia da música; 4. Explicação gramatical."
            analise = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;">
                <div class="titulo">Aula Musical: {musica}</div>
                <div style="color: #F2F2F2; white-space: pre-wrap;">{analise}</div>
            </div>""", unsafe_allow_html=True)

# ==============================================================================
# ABA 4: PLANO DE PALAVRAS-CHAVE (EXPANDIDO)
# ==============================================================================
with tab4:
    st.header("Plano de Palavras-Chave (Inglês)")
    st.write("Leia cerca de 1.500 versículos focados nas 50 palavras mais repetidas da Bíblia.")
    
    blocos = {
        1: "Bloco 1: Fé e Amor (Faith, Love, Hope)",
        2: "Bloco 2: Graça e Paz (Grace, Peace, Joy)",
        3: "Bloco 3: Sabedoria e Luz (Wisdom, Light, Truth)",
        4: "Bloco 4: Força e Coragem (Strength, Courage, Power)",
        5: "Bloco 5: Misericórdia e Perdão (Mercy, Forgiveness, Redemption)"
    }
    
    bloco_escolhido = st.radio("Selecione o bloco de estudo:", list(blocos.values()))
    
    if st.button("📖 Estudar Versículos do Bloco", use_container_width=True):
        with st.spinner("Buscando versículos..."):
            prompt = f"Atue como guia bilíngue. Gere 3 versículos famosos em inglês (e PT) contendo palavras do bloco '{bloco_escolhido}'. Inclua referência, texto EN, tradução PT e uma pergunta reflexiva."
            estudo = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000;">
                <div class="titulo">{bloco_escolhido}</div>
                <div style="color: #F2F2F2; white-space: pre-wrap;">{estudo}</div>
            </div>""", unsafe_allow_html=True)
'''

# =============================================================================
# CONTEÚDO DA MENTE (Atualizado com YouTube)
# =============================================================================
NOVO_CONTEUDO_MENTE = '''import streamlit as st
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
                        
                        full_text = re.sub(r'\\s+', ' ', full_text)
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
                        st.session_state["resumo_pdf"] = ask_gemini(f"Resuma: \\n\\n{chunk['text_content']}")
            
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
'''

# =============================================================================
# HELPERS DE SINCRONIZAÇÃO
# =============================================================================
def _run(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return 1, str(e)

def _verificar_stage():
    _, out = _run(["git", "diff", "--cached", "--name-only"])
    for rel in [l for l in out.splitlines() if l.strip()]:
        if Path(rel).name in ARQUIVOS_PROIBIDOS:
            raise RuntimeError(f"🚨 Segredo detectado: {rel}")

# =============================================================================
# EXECUÇÃO
# =============================================================================
def aplicar_melhoria():
    print("=" * 60)
    print("⚔️  APLICANDO MELHORIA: NOVAS FUNCIONALIDADES E YOUTUBE")
    print("=" * 60)

    # 1. Atualizar requirements.txt
    req_file = BASE / "requirements.txt"
    req_txt = req_file.read_text(encoding="utf-8")
    if "youtube-transcript-api" not in req_txt:
        req_txt += "\nyoutube-transcript-api>=0.6.2\n"
        req_file.write_text(req_txt, encoding="utf-8")
        print("[OK] requirements.txt atualizado com youtube-transcript-api.")

    # 2. Atualizar 09_Biblia.py
    arq_biblia = BASE / "ui" / "pages" / "09_Biblia.py"
    try:
        ast.parse(NOVO_CONTEUDO_BIBLIA)
        arq_biblia.write_text(NOVO_CONTEUDO_BIBLIA, encoding="utf-8")
        print("[OK] 09_Biblia.py atualizado (Melhorias e Correções).")
    except SyntaxError as e:
        print(f"[ERRO] Sintaxe em 09_Biblia.py: {e}")
        sys.exit(1)

    # 3. Atualizar 02_Mente.py
    arq_mente = BASE / "ui" / "pages" / "02_Mente.py"
    try:
        ast.parse(NOVO_CONTEUDO_MENTE)
        arq_mente.write_text(NOVO_CONTEUDO_MENTE, encoding="utf-8")
        print("[OK] 02_Mente.py atualizado (Integração YouTube).")
    except SyntaxError as e:
        print(f"[ERRO] Sintaxe em 02_Mente.py: {e}")
        sys.exit(1)

    # 4. Sincronização com GitHub
    print("\n☁️  SINCRONIZANDO COM O SERVIDOR (GitHub)")
    _run(["git", "add", "-A"])
    _run(["git", "rm", "--cached", "PROJETO_SAMURAI*.md"])
    
    try:
        _verificar_stage()
    except RuntimeError as e:
        _run(["git", "reset"])
        print(e)
        sys.exit(1)

    code, out = _run(["git", "commit", "-m", "Feat: Melhorias na Biblia (Devocional, Louvores) e Extrator YouTube"])
    if code != 0 and "nothing to commit" not in out:
        print(f"[ERRO] Commit falhou: {out}")
        sys.exit(1)
    
    print("[OK] Commit realizado.")
    _run(["git", "pull", "origin", "main", "--rebase", "--no-edit"])
    
    code, out = _run(["git", "push", "origin", "main"])
    if code != 0:
        print(f"[ERRO] Push falhou: {out}")
        sys.exit(1)
    
    print("[OK] Push concluído. Streamlit atualizará em instantes.")
    print("=" * 60)

if __name__ == "__main__":
    aplicar_melhoria()