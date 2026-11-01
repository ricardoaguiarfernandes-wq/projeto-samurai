"""
melhoria.py — Aplica melhorias no Projeto Samurai de forma segura.
Nesta versão: 
1. Adiciona Inglês (Destra) na página da Bíblia.
2. Cria a página 12_Filosofia.py (Inspirada no COF).
3. Atualiza o menu no app.py.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

# =============================================================================
# CONFIG
# =============================================================================
BASE = Path(__file__).resolve().parent
WINDOW_TITLE   = "Projeto Samurai"
INICIAR_BAT    = BASE / "INICIAR.bat"

PADROES_SECRETOS = [
    re.compile(r"AQ\.Ab8RN6[A-Za-z0-9_\-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"postgresql://[^:\s]+:[^@\s]+@"),
]
ARQUIVOS_PROIBIDOS = {"config.json", ".env", "secrets.toml"}
PREFIXO_MD_GERADO = "PROJETO_SAMURAI"

# =============================================================================
# CONTEÚDO DOS ARQUIVOS
# =============================================================================

# 1. Nova versão da Bíblia com Módulo de Inglês
NOVO_CONTEUDO_BIBLIA = '''import streamlit as st
import sys
from pathlib import Path
from gtts import gTTS
import io

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db
from services.ai import ask_gemini

init_db()

st.title("📖 Bíblia & Inglês")
st.caption("Plano de leitura em 1 ano + Aprendizado de Inglês Cristão")

proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")

if not proximo:
    st.success("🎉 Parabéns! Você concluiu a leitura da Bíblia em 1 ano!")
else:
    day = proximo["day"]
    st.subheader(f"Dia {day} de 365")

    plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
    if plano:
        versiculos = query_all(
            "SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id",
            (plano["start_verse_id"], plano["end_verse_id"])
        )

        if versiculos:
            primeiro = versiculos[0]
            ultimo = versiculos[-1]
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

            # === MELHORIA: INGLÊS DESTRA ===
            st.divider()
            st.subheader("🇺🇸 Aprender Inglês com a Palavra")
            st.write("Expanda seu vocabulário usando este versículo como base.")
            
            if st.button("🪄 Traduzir e Explicar em Inglês", use_container_width=True):
                with st.spinner("O Mentor está preparando sua aula de inglês..."):
                    prompt = f"""Atue como um professor de inglês cristão (metodologia Destra for the Nations).
Baseado no versículo: "{texto_bruto}"
Forneça:
1. A tradução oficial para o inglês.
2. Três palavras-chave em inglês que aparecem no versículo (com pronúncia aproximada e significado).
3. Uma explicação gramatical simples sobre a estrutura da frase em inglês.
4. Uma mini-frase motivacional em inglês para o usuário praticar a leitura.
Seja didático e encorajador."""
                    aula_en = ask_gemini(prompt)
                    st.session_state["aula_ingles"] = aula_en

            if st.session_state.get("aula_ingles"):
                st.markdown(
                    f"""<div class="samurai-card" style="border-left-color: #2196F3;">
                        <div class="titulo" style="color: #2196F3;">Class is in session</div>
                        <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{st.session_state['aula_ingles']}</div>
                    </div>""", unsafe_allow_html=True
                )

            # --- BOTÕES DE AÇÃO ---
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Concluir Leitura", use_container_width=True):
                    execute("UPDATE reading_progress SET completed = 1 WHERE day = ?", (day,))
                    st.rerun()
            with col2:
                if st.button("🔊 Ouvir Áudio", use_container_width=True):
                    with st.spinner("Gerando áudio..."):
                        tts = gTTS(text=texto_bruto, lang='pt', slow=False)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        st.audio(fp.getvalue(), format="audio/mp3")

            if st.session_state.get("aula_ingles"):
                # Não é necessário repetir o botão de áudio
                pass
'''

# 2. Nova página de Filosofia (COF)
NOVO_CONTEUDO_FILOSOFIA = '''import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db
from core.database import execute
from services.ai import ask_gemini

init_db()

st.title("🏛️ Filosofia & Sabedoria")
st.caption("Desenvolvimento do raciocínio, visão interdisciplinar e as aulas do COF.")

# --- DESAFIO DO DIA ---
st.subheader("🧠 Desafio Intelectual do Dia")

PROMPTS_COF = [
    "O que é a verdadeira ignorância: não saber, ou saber e não aplicar?",
    "Como você pode diferenciar uma opinião de um conhecimento real em sua vida hoje?",
    "Qual foi a última vez que você mudou de ideia? O que te fez mudar?",
    "O que a sua rotina atual diz sobre a sua visão de mundo?",
    "Por que buscamos distrações em vez de encarar a realidade?",
    "Qual a diferença entre saber o nome de uma coisa e entender como ela funciona?",
    "Como a ordem no seu ambiente físico reflete a ordem da sua mente?"
]

# Escolhe a frase baseada no dia do ano
prompt_do_dia = PROMPTS_COF[date.today().toordinal() % len(PROMPTS_COF)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000;">
        <div class="titulo">Reflexão de Hoje</div>
        <div class="valor" style="font-size: 1.2rem; font-weight: 500;">{prompt_do_dia}</div>
    </div>""", unsafe_allow_html=True
)

# --- MENTOR DE FILOSOFIA (IA) ---
st.divider()
st.subheader("🤖 Mentor Filosófico (Inspirado no COF)")
st.write("Debata com a IA. Ela usará o método socrático para testar suas ideias.")

with st.form("form_filosofia"):
    reflexao = st.text_area("Sua reflexão sobre o tema:", height=150, placeholder="Escreva sem medo de errar. A filosofia é o exercício do pensamento...")
    submitted = st.form_submit_button("Debater com o Mentor", use_container_width=True)

if submitted and reflexao.strip():
    with st.spinner("O Mentor está analisando seus argumentos..."):
        prompt_ia = f"""Atue como um mentor de filosofia no estilo interdisciplinar do Curso Online de Filosofia (COF). 
O tema do dia é: "{prompt_do_dia}"
O usuário respondeu com: "{reflexao}"

Sua tarefa:
1. Validar o esforço de raciocínio do usuário.
2. Apontar uma falha lógica, uma contradição ou um ponto cego no argumento dele (sem ser arrogante).
3. Fazer UMA pergunta socrática profunda que force o usuário a pensar além da superficialidade.
4. Terminar com uma citação curta (real ou adaptada) de um filósofo clássico.

Seja rigoroso, direto, mas acolhedor. O objetivo é o amadurecimento intelectual."""
        
        resposta_ia = ask_gemini(prompt_ia)
        
        st.markdown(
            f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
                <div class="titulo">A Resposta do Mestre</div>
                <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{resposta_ia}</div>
            </div>""", unsafe_allow_html=True
        )

# --- OUTROS MATERIAIS (COF) ---
st.divider()
st.subheader("📚 Estudos Complementares")
st.markdown("""
Aqui você pode construir uma base sólida de conhecimento interdisciplinar:
*   **Leitura:** Procure ler 15 minutos por dia de um livro clássico (filosofia, teologia ou literatura).
*   **Retenção:** Anote o que leu. Escrever força a mente a organizar o caos.
*   **Conexões:** Tente ligar o que você leu com um problema real da sua vida.
""")
'''

# =============================================================================
# HELPERS (IDÊNTICOS AO ANTERIOR)
# =============================================================================
def _run(cmd, timeout=120):
    try:
        r = subprocess.run(
            cmd, cwd=BASE, capture_output=True, text=True, 
            encoding="utf-8", errors="replace", timeout=timeout
        )
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return 1, str(e)

def _verificar_stage():
    _, out = _run(["git", "diff", "--cached", "--name-only"])
    staged = [l for l in out.splitlines() if l.strip()]
    problemas = []
    for rel in staged:
        nome = Path(rel).name
        if nome in ARQUIVOS_PROIBIDOS:
            problemas.append(f"  - {rel} (arquivo sensivel)")
            continue
        if nome.startswith(PREFIXO_MD_GERADO) and nome.endswith(".md"):
            try:
                conteudo = (BASE / rel).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                conteudo = ""
            for pat in PADROES_SECRETOS:
                if pat.search(conteudo):
                    problemas.append(f"  - {rel} (contem segredo)")
                    break
    if problemas:
        raise RuntimeError("🚨 PUSH BLOQUEADO — segredos no stage:\n" + "\n".join(problemas))

# =============================================================================
# EXECUÇÃO
# =============================================================================
def aplicar_melhoria():
    print("=" * 60)
    print("⚔️  APLICANDO MELHORIA: INGLÊS (BÍBLIA) + FILOSOFIA (COF)")
    print("=" * 60)

    # 1. Arquivo Bíblia (09_Biblia.py)
    arquivo_biblia = BASE / "ui" / "pages" / "09_Biblia.py"
    if arquivo_biblia.exists() and "Aprender Inglês com a Palavra" in arquivo_biblia.read_text(encoding="utf-8"):
        print("[SKIP] Módulo de Inglês na Bíblia já existe.")
    else:
        try:
            ast.parse(NOVO_CONTEUDO_BIBLIA)
            arquivo_biblia.write_text(NOVO_CONTEUDO_BIBLIA, encoding="utf-8")
            print("[OK] Arquivo atualizado: 09_Biblia.py (Inglês adicionado)")
        except SyntaxError as e:
            print(f"[ERRO] Sintaxe inválida em 09_Biblia.py: {e}")
            sys.exit(1)

    # 2. Novo Arquivo Filosofia (12_Filosofia.py)
    arquivo_filosofia = BASE / "ui" / "pages" / "12_Filosofia.py"
    if arquivo_filosofia.exists():
        print("[SKIP] Página de Filosofia já existe.")
    else:
        try:
            ast.parse(NOVO_CONTEUDO_FILOSOFIA)
            arquivo_filosofia.write_text(NOVO_CONTEUDO_FILOSOFIA, encoding="utf-8")
            print("[OK] Arquivo criado: 12_Filosofia.py")
        except SyntaxError as e:
            print(f"[ERRO] Sintaxe inválida em 12_Filosofia.py: {e}")
            sys.exit(1)

    # 3. Atualizar app.py para incluir a Filosofia no menu
    arquivo_app = BASE / "app.py"
    texto_app = arquivo_app.read_text(encoding="utf-8")
    
    if "12_Filosofia.py" not in texto_app:
        # Adiciona a definição da página
        texto_app = texto_app.replace(
            'alimentacao = st.Page("ui/pages/11_Alimentacao.py", title="🍏 Alimentação")',
            'alimentacao = st.Page("ui/pages/11_Alimentacao.py", title="🍏 Alimentação")\nfilosofia = st.Page("ui/pages/12_Filosofia.py", title="🏛️ Filosofia")'
        )
        # Adiciona no menu de navegação
        texto_app = texto_app.replace(
            '"🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento, religiao, biblia, newsletter, alimentacao],',
            '"🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento, religiao, biblia, newsletter, alimentacao, filosofia],'
        )
        
        try:
            ast.parse(texto_app)
            arquivo_app.write_text(texto_app, encoding="utf-8")
            print("[OK] Arquivo atualizado: app.py (Menu Filosofia)")
        except SyntaxError as e:
            print(f"[ERRO] Sintaxe inválida no app.py: {e}")
            sys.exit(1)
    else:
        print("[SKIP] Filosofia já está no menu do app.py.")

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

    code, out = _run(["git", "commit", "-m", "Feat: Adiciona Ingles na Biblia e nova aba de Filosofia (COF)"])
    if code != 0 and "nothing to commit" not in out:
        print(f"[ERRO] Commit falhou: {out}")
        sys.exit(1)
    
    print("[OK] Commit realizado.")
    _run(["git", "pull", "origin", "main", "--rebase", "--no-edit"])
    
    code, out = _run(["git", "push", "origin", "main"])
    if code != 0:
        print(f"[ERRO] Push falhou: {out}")
        sys.exit(1)
    
    print("[OK] Push para GitHub concluido. Streamlit Cloud vai atualizar em instantes.")
    print("=" * 60)

if __name__ == "__main__":
    aplicar_melhoria()