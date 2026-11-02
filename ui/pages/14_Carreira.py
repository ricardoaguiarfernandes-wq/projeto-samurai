import streamlit as st
import sys
import json
import re
import random
from datetime import date
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("💼 Carreira & Profissão")
st.caption("Trilha de evolução: Estagiário de Survey ➔ Surveyor Junior.")

hoje = date.today().isoformat()

tab_missoes, tab_manuais, tab_flashcards = st.tabs(["🎯 Missões Diárias", "📚 Base de Conhecimento (Manuais)", "🧠 Flashcards (Revisão)"])

with tab_manuais:
    st.header("Biblioteca Técnica")
    st.write("Envie os manuais dos equipamentos, procedimentos e normas. A IA usará este material para testar seus conhecimentos.")
    
    uploaded_file = st.file_uploader("Upload de Manual (PDF)", type=["pdf"])
    if uploaded_file is not None:
        if st.button("📥 Processar e Salvar Manual", use_container_width=True):
            with st.spinner("Lendo e extraindo texto do PDF..."):
                try:
                    import fitz
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    
                    if text.strip():
                        execute(
                            "INSERT INTO manuals (title, content) VALUES (?, ?) ON CONFLICT(title) DO UPDATE SET content=excluded.content, uploaded_at=CURRENT_TIMESTAMP",
                            (uploaded_file.name, text)
                        )
                        st.success(f"Manual '{uploaded_file.name}' processado e salvo!")
                        st.rerun()
                    else:
                        st.warning("O PDF não contém texto legível (pode ser escaneado).")
                except Exception as e:
                    st.error(f"Erro ao ler PDF: {e}")

    st.divider()
    st.subheader("📚 Manuais Disponíveis")
    try:
        manuais = query_all("SELECT id, title, uploaded_at FROM manuals ORDER BY uploaded_at DESC")
    except Exception:
        from core.database import is_postgres
        if is_postgres():
            execute("CREATE TABLE IF NOT EXISTS manuals (id SERIAL PRIMARY KEY, title TEXT UNIQUE, content TEXT NOT NULL, uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        else:
            execute("CREATE TABLE IF NOT EXISTS manuals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, content TEXT NOT NULL, uploaded_at TEXT NOT NULL DEFAULT (datetime('now')))")
        manuais = []
    if not manuais:
        st.info("Nenhum manual cadastrado ainda.")
    else:
        for m in manuais:
            st.markdown(f"- **{m['title']}** (Enviado em: {m['uploaded_at'][:10]})")

with tab_missoes:
    # --- MISSÕES DIÁRIAS ---
    missoes = query_all("SELECT id, task, completed FROM career_missions WHERE mission_date = ?", (hoje,))

    if not missoes:
        st.info("🎯 Nenhuma missão definida para hoje.")
        if st.button("🧠 Gerar Missões de Hoje com IA", use_container_width=True):
            with st.spinner("Traçando estratégia para a sua efetivação..."):
                # Verifica se tem manual para incluir no contexto
                manuais = query_all("SELECT title FROM manuals")
                ctx_manual = "Temos manuais de: " + ", ".join([m['title'] for m in manuais]) if manuais else "Nenhum manual cadastrado."

                prompt = f"""Atue como um Gestor Sênior e Mentor da área de Survey.
O usuário é estagiário e tem a meta de ser efetivado como Surveyor Junior no início do próximo ano.
{ctx_manual}

Crie 3 missões diárias curtas, práticas e teóricas para o dia de hoje. O foco deve ser:
1. Habilidade Técnica (ex: leitura de dados, equipamentos, normas, softwares).
2. Postura Profissional (ex: comunicação com a equipe, proatividade, relatórios).
3. Visão de Negócio (ex: entender o impacto do survey no projeto).

Se houver manuais cadastrados, a missão 1 deve sugerir a leitura de um tópico específico do manual.
Sua resposta DEVE ser APENAS um JSON válido com a seguinte estrutura:
{{"missions": ["Missão 1...", "Missão 2...", "Missão 3..."]}}
"""
                res = ask_gemini(prompt)
                m = re.search(r'\{.*\}', res, re.DOTALL)
                if m:
                    try:
                        data = json.loads(m.group(0))
                        for task in data.get("missions", []):
                            execute("INSERT INTO career_missions (mission_date, task, completed) VALUES (?, ?, 0)", (hoje, task))
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao processar: {e}")
    else:
        st.subheader("📋 Missões de Hoje")
        alterou = False
        for m in missoes:
            novo = st.checkbox(m["task"], value=bool(m["completed"]), key=f"mission_{m['id']}")
            if novo != bool(m["completed"]):
                execute("UPDATE career_missions SET completed = ? WHERE id = ?", (1 if novo else 0, m["id"]))
                alterou = True
        if alterou:
            st.rerun()

        if all(m["completed"] for m in missoes):
            st.success("🏆 Todas as missões concluídas! O Surveyor Junior está cada vez mais perto.")

    st.divider()
    
    # --- DESAFIO TÉCNICO DO MANUAL ---
    st.subheader("🧠 Desafio Técnico do Manual")
    st.write("A IA vai testar seu conhecimento com base nos PDFs que você enviou.")
    
    if "desafio_manual" not in st.session_state:
        st.session_state["desafio_manual"] = None

    if st.button("🎲 Gerar Pergunta do Manual", use_container_width=True):
        manuais = query_all("SELECT title, content FROM manuals")
        if not manuais:
            st.warning("Envie um manual na aba ao lado primeiro.")
        else:
            with st.spinner("Lendo o manual e criando uma pergunta..."):
                # Pega um trecho aleatório de algum manual para não estourar o limite de tokens
                manual_escolhido = random.choice(manuais)
                texto_manual = manual_escolhido["content"]
                # Pega um chunk de 5000 caracteres
                if len(texto_manual) > 5000:
                    start_idx = random.randint(0, len(texto_manual) - 5000)
                    chunk = texto_manual[start_idx:start_idx+5000]
                else:
                    chunk = texto_manual

                prompt = f"""Baseado EXCLUSIVAMENTE no seguinte trecho do manual "{manual_escolhido['title']}":

{chunk}

Crie UMA pergunta técnica desafiadora para um estagiário de Survey. A pergunta deve exigir que ele consulte o manual para responder.
Regras:
1. NÃO forneça a resposta.
2. Retorne APENAS a pergunta.
"""
                pergunta = ask_gemini(prompt)
                st.session_state["desafio_manual"] = {
                    "pergunta": pergunta,
                    "contexto": chunk,
                    "manual": manual_escolhido["title"]
                }

    if st.session_state["desafio_manual"]:
        desafio = st.session_state["desafio_manual"]
        st.info(f"**Manual:** {desafio['manual']}\n\n**Pergunta:** {desafio['pergunta']}")
        
        resposta_user = st.text_area("Sua resposta (tente adivinhar ou descreva o que encontrou):")
        
        if st.button("✅ Corrigir Resposta com a IA"):
            if not resposta_user.strip():
                st.warning("Digite sua resposta primeiro.")
            else:
                with st.spinner("Avaliando com base no manual..."):
                    prompt_aval = f"""Atue como um Avaliador Sênior de Survey.
Baseado EXCLUSIVAMENTE neste trecho do manual:
{desafio['contexto']}

O usuário respondeu à pergunta "{desafio['pergunta']}" com:
"{resposta_user}"

Sua missão:
1. Diga se ele acertou, errou ou chegou perto.
2. Dê a resposta correta baseada no texto do manual.
3. Explique de forma didática.
Seja direto e motivador.
"""
                    avaliacao = ask_gemini(prompt_aval)
                    st.markdown(f'<div class="samurai-card" style="border-left-color: #4CAF50;"><div style="white-space: pre-wrap;">{avaliacao}</div></div>', unsafe_allow_html=True)
                    if st.button("Limpar Desafio"):
                        st.session_state["desafio_manual"] = None
                        st.rerun()

with tab_flashcards:
    st.header("Gerador de Flashcards")
    st.write("A IA vai ler os seus manuais e criar perguntas e respostas para você memorizar.")
    
    manuais_lista = query_all("SELECT title FROM manuals")
    if not manuais_lista:
        st.warning("Envie um manual na aba ao lado primeiro.")
    else:
        manual_escolhido = st.selectbox("Selecione o manual:", [m['title'] for m in manuais_lista])
        
        if st.button("🪄 Gerar Flashcards com IA", use_container_width=True):
            with st.spinner("Lendo o manual e gerando cartões..."):
                import random
                manual_data = query_one("SELECT content FROM manuals WHERE title = ?", (manual_escolhido,))
                texto_manual = manual_data['content']
                
                # Pega um chunk de 8000 caracteres para não estourar o limite
                if len(texto_manual) > 8000:
                    start_idx = random.randint(0, len(texto_manual) - 8000)
                    chunk = texto_manual[start_idx:start_idx+8000]
                else:
                    chunk = texto_manual
                    
                prompt = f"""Leia o trecho do manual técnico abaixo e crie EXATAMENTE 3 flashcards no formato JSON.
Cada flashcard deve ter uma pergunta desafiadora e uma resposta direta.

Retorne APENAS o JSON válido, sem markdown:
{{
  "flashcards": [
    {{"question": "Pergunta 1...", "answer": "Resposta 1..."}},
    {{"question": "Pergunta 2...", "answer": "Resposta 2..."}},
    {{"question": "Pergunta 3...", "answer": "Resposta 3..."}}
  ]
}}

TEXTO DO MANUAL:
{chunk}
"""
                res = ask_gemini(prompt)
                import re, json
                from datetime import date
                m = re.search(r'\{.*\}', res, re.DOTALL)
                if m:
                    try:
                        data = json.loads(m.group(0))
                        for card in data.get("flashcards", []):
                            execute(
                                "INSERT INTO flashcards (question, answer, next_review) VALUES (?, ?, ?)",
                                (card["question"], card["answer"], date.today().isoformat())
                            )
                        st.success("Flashcards gerados com sucesso! Vá no Telegram e digite /flashcard.")
                    except Exception as e:
                        st.error(f"Erro ao processar JSON: {e}")
                else:
                    st.error("A IA não retornou o formato esperado.")

    st.divider()
    st.subheader("📅 Cartões Pendentes Hoje")
    from datetime import date
    pendentes = query_all("SELECT question FROM flashcards WHERE next_review <= ? AND last_asked = 0", (date.today().isoformat(),))
    if not pendentes:
        st.info("Nenhum cartão pendente para hoje. Ótimo trabalho!")
    else:
        for p_card in pendentes:
            st.markdown(f"- {p_card['question']}")
