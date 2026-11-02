"""
criar_projeto_samurai.py — V4.2 (Base de Conhecimento e Quizzes do Manual)

ENTREGAS:
1. DB: Cria a tabela 'manuals' para armazenar o texto extraído dos PDFs.
2. UI (14_Carreira.py): Adiciona a área de upload de PDFs e a extração de texto.
3. UI: Adiciona o "Desafio Técnico do Manual" (A IA gera a pergunta, você tenta responder e ela corrige).

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

def _git_run_safe(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)

def read(p: Path) -> str: return p.read_text(encoding="utf-8")
def write_validated(p: Path, content: str) -> None:
    if p.suffix == ".py":
        try: ast.parse(content, filename=str(p))
        except SyntaxError as e:
            print(f"[ABORTA] Sintaxe quebrada em {p}: {e}"); sys.exit(1)
    p.write_text(content, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")

# ============================================================
# 1. DB SCHEMA (Manuais)
# ============================================================
def fix_schema_manuals() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)
    if "CREATE TABLE IF NOT EXISTS manuals" in txt:
        print("[SKIP] schema.py — tabela manuals já existe.")
        return
    
    marker = '"""CREATE TABLE IF NOT EXISTS career_missions (id INTEGER PRIMARY KEY AUTOINCREMENT, mission_date TEXT NOT NULL, task TEXT NOT NULL, completed INTEGER DEFAULT 0);""",'
    nova_linha = marker + '\n        """CREATE TABLE IF NOT EXISTS manuals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, content TEXT NOT NULL, uploaded_at TEXT NOT NULL DEFAULT (datetime(\'now\')));""",'
    
    if marker in txt:
        txt = txt.replace(marker, nova_linha, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] schema.py — marcador de career_missions não encontrado.")

# ============================================================
# 2. UI CARREIRA (Upload e Quiz)
# ============================================================
def fix_career_manuals() -> None:
    p = BASE / "ui" / "pages" / "14_Carreira.py"
    txt = read(p)

    if "Desafio Técnico do Manual" in txt:
        print("[SKIP] 14_Carreira.py — manuais já integrados.")
        return

    # Substituir o conteúdo inteiro da página para organizar as seções
    novo_conteudo = '''import streamlit as st
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

tab_missoes, tab_manuais = st.tabs(["🎯 Missões Diárias", "📚 Base de Conhecimento (Manuais)"])

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
    manuais = query_all("SELECT id, title, uploaded_at FROM manuals ORDER BY uploaded_at DESC")
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
                m = re.search(r'\\{.*\\}', res, re.DOTALL)
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
        st.info(f"**Manual:** {desafio['manual']}\\n\\n**Pergunta:** {desafio['pergunta']}")
        
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
'''
    p.write_text(novo_conteudo, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: upload de manuais e desafios tecnicos baseados em RAG"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V4.2 — MANUAIS E DESAFIOS TÉCNICOS")
    print("=" * 60)

    etapas = [
        ("Criar tabela de manuais (schema.py)", fix_schema_manuals),
        ("Atualizar página de carreira (14_Carreira.py)", fix_career_manuals),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nComo usar:")
    print("1. Espere o Streamlit atualizar.")
    print("2. Vá na aba '💼 Carreira' -> '📚 Base de Conhecimento (Manuais)'.")
    print("3. Envie o PDF de um equipamento ou procedimento.")
    print("4. Volte para a aba '🎯 Missões Diárias' e clique em 'Gerar Missões' (ele vai incluir o manual).")
    print("5. Clique em '🎲 Gerar Pergunta do Manual'. A IA vai ler o PDF e te desafiar!")

if __name__ == "__main__":
    aplicar()