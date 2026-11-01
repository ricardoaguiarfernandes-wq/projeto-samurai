# ⚔️ Projeto Samurai — Mapa do Código

> Gerado automaticamente por `gerar_codigo.py`

> Raiz: `Projeto Samurai`

---


## `.streamlit/config.toml`

```toml
[theme]
base="dark"
primaryColor="#8B0000"
backgroundColor="#0B0B0B"
secondaryBackgroundColor="#171717"
textColor="#F2F2F2"
font="sans serif"

```


## `app.py`

```python
"""
Projeto Samurai — Sistema Operacional Pessoal.
Entry point Streamlit. Configura tema, navegação e injeta CSS.
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from core.schema import init_db

init_db()

st.set_page_config(
    page_title="Projeto Samurai ⚔️",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

SAMURAI_CSS = """
<style>
:root {
    --s-red:        #8B0000;
    --s-dark-red:   #5C0000;
    --s-black:      #0B0B0B;
    --s-gray:       #171717;
    --s-gray-soft:  #1F1F1F;
    --s-white:      #FFFFFF;
    --s-white-soft: #CCCCCC;
}

/* Força o fundo escuro no app */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--s-black) !important;
}

/* Força cor do texto em TODOS os elementos comuns e containers do Streamlit */
h1, h2, h3, h4, h5, h6, p, span, li, label, 
div[data-testid="stMarkdownContainer"] *, 
[data-testid="stWidgetLabel"] * {
    color: var(--s-white) !important;
}

/* Linha vermelha embaixo do H1 */
h1 {
    border-bottom: 2px solid var(--s-red) !important;
    padding-bottom: 8px !important;
    letter-spacing: .5px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--s-gray) !important;
    border-right: 1px solid var(--s-red) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--s-white) !important;
}

/* Cards Customizados */
.samurai-card {
    background-color: var(--s-gray-soft) !important;
    border-left: 4px solid var(--s-red) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
}
.samurai-card .titulo {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--s-white-soft) !important;
    margin-bottom: 6px !important;
    font-weight: 600 !important;
}
.samurai-card .valor {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--s-white) !important;
}
.samurai-card .detalhe {
    font-size: 0.85rem !important;
    color: var(--s-white-soft) !important;
    margin-top: 6px !important;
}

/* Botões */
.stButton > button, .stFormSubmitButton > button {
    background-color: var(--s-red) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-dark-red) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--s-dark-red) !important;
    border-color: var(--s-white) !important;
}

/* Barras de Progresso */
.stProgress > div > div > div > div {
    background-color: var(--s-red) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--s-gray) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-red) !important;
}

/* Divisores e Caixas de Info/Alerta */
hr { border-color: var(--s-red) !important; opacity: .5 !important; }
.stAlert { 
    background-color: var(--s-gray-soft) !important; 
    color: var(--s-white) !important; 
    border: 1px solid var(--s-red) !important; 
}
.stAlert * { color: var(--s-white) !important; }
</style>
"""

st.markdown(SAMURAI_CSS, unsafe_allow_html=True)


home = st.Page("ui/pages/00_Home.py", title="🏯 Dojo", default=True)
consistencia = st.Page("ui/pages/07_Consistencia.py", title="🎯 Consistência")
corpo = st.Page("ui/pages/01_Corpo.py", title="💪 Corpo")
mente = st.Page("ui/pages/02_Mente.py", title="🧠 Mente")
informacao = st.Page("ui/pages/03_Informacao.py", title="📰 Informação")
patrimonio = st.Page("ui/pages/04_Patrimonio.py", title="💎 Patrimônio")
descanso = st.Page("ui/pages/05_Descanso.py", title="🌿 Descanso & Lazer")
autoconhecimento = st.Page("ui/pages/06_Autoconhecimento.py", title="🪞 Autoconhecimento")
religiao = st.Page("ui/pages/08_Religiao.py", title="🕊️ Religião")
biblia = st.Page("ui/pages/09_Biblia.py", title="📖 Bíblia")

pg = st.navigation(
    {
        "⚔️ Comando": [home, consistencia],
        "🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento, religiao, biblia],
    }
)


# --- Configuração da IA na Sidebar ---
from services.ai import get_api_key

with st.sidebar:
    st.divider()
    st.markdown("### ⚙️ IA Configuração")
    key_atual = get_api_key()
    
    if key_atual and key_atual != "COLE_SUA_CHAVE_AQUI":
        st.success("IA Conectada 🟢")
    else:
        st.warning("IA Desconectada 🔴")
        nova_chave = st.text_input("Cole sua API Key do Gemini:", type="password", placeholder="AIzaSy...")
        if st.button("Salvar e Ativar IA", use_container_width=True):
            if nova_chave.strip():
                config_file = BASE_DIR / "config.json"
                config_file.write_text(json.dumps({"gemini_api_key": nova_chave.strip()}, indent=4), encoding="utf-8")
                st.success("Chave salva com sucesso!")
                import time
                time.sleep(1)
                st.rerun()

pg.run()


```


## `assets/.gitkeep`

```text

```


## `config.json`

```json
{
    "gemini_api_key": "AQ.Ab8RN6I_Bq6xAq5tGVYh87pnioxbyxprdwD0UqKdSw8gzkE5zw"
}

```


## `core/__init__.py`

```python
"""Núcleo do Projeto Samurai (banco, schema, utilitários)."""

```


## `core/database.py`

```python
"""
Conexão SQLite centralizada.
- WAL mode para leituras concorrentes.
- Lock em memória para evitar writes simultâneos (Streamlit é multithread).
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "samurai.db"

_lock = threading.RLock()


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão configurada. O caller é responsável por fechar."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def execute(sql: str, params: tuple = ()) -> int:
    """Executa um INSERT/UPDATE/DELETE. Retorna lastrowid."""
    with _lock:
        conn = get_connection()
        try:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()


def executemany(sql: str, seq_params: list[tuple]) -> None:
    with _lock:
        conn = get_connection()
        try:
            conn.executemany(sql, seq_params)
            conn.commit()
        finally:
            conn.close()


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _lock:
        conn = get_connection()
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with _lock:
        conn = get_connection()
        try:
            return conn.execute(sql, params).fetchone()
        finally:
            conn.close()

```


## `core/schema.py`

```python
"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    
    # Blocos de Leitura de PDFs (Mente)
    """
    CREATE TABLE IF NOT EXISTS book_chunks (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL,
        chunk_index  INTEGER NOT NULL,
        text_content TEXT    NOT NULL,
        completed    INTEGER NOT NULL DEFAULT 0,
        UNIQUE (book_title, chunk_index)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
    ("Oração", "Religião", "Momento de conexão com Deus."),
    ("Leitura Bíblica", "Religião", "Ler um trecho da Palavra."),
    ("Gratidão a Deus", "Religião", "Agradecer pelas bênçãos do dia."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    # Seed inteligente: insere apenas se o hábito ainda não existir
    for name, pillar, desc in SEED_HABITS:
        if not query_one("SELECT id FROM habits WHERE name = ?", (name,)):
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )

```


## `criar_projeto_samurai.py`

```python
import ast
import os
import sys
from pathlib import Path

BASE = Path(r"C:\Users\Ricardo Fernandes\Desktop\Projeto Samurai")

def aplicar_patch():
    print("=" * 60)
    print("⚔️  PATCH: LEITOR DE PDF VIA OCR DE IA (VISÃO COMPUTACIONAL)")
    print("=" * 60)

    if not BASE.exists():
        print(f"[ERRO] Pasta do projeto não encontrada: {BASE}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 1. Atualizar services/ai.py (Adicionar suporte a Imagens)
    # -----------------------------------------------------------------------
    ai_file = BASE / "services" / "ai.py"
    ai_txt = ai_file.read_text(encoding="utf-8")

    if "ask_gemini_vision" not in ai_txt:
        nova_funcao = '''
def ask_gemini_vision(image_bytes: bytes, prompt: str) -> str:
    api_key = get_api_key()
    if not api_key or api_key == "COLE_SUA_CHAVE_AQUI":
        return "⚠️ API Key não configurada."
    
    genai.configure(api_key=api_key)
    try:
        # Usamos o 1.5-flash para visão pois ele é excelente em OCR
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])
        return response.text
    except Exception as e:
        return f"⚠️ Erro na IA (Visão): {str(e)}"
'''
        ai_txt += nova_funcao
        try:
            ast.parse(ai_txt)
            ai_file.write_text(ai_txt, encoding="utf-8")
            print("[OK] Corrigido: services/ai.py (Suporte a Visão adicionado)")
        except SyntaxError as e:
            print(f"[ERRO] Falha na validação do ai.py: {e}")
            sys.exit(1)
    else:
        print("[SKIP] services/ai.py já possui suporte a Visão.")

    # -----------------------------------------------------------------------
    # 2. Sobrescrever 02_Mente.py com a opção de OCR
    # -----------------------------------------------------------------------
    mente_file = BASE / "ui" / "pages" / "02_Mente.py"
    novo_mente = '''import streamlit as st
import sys
from pathlib import Path
import re
import fitz  # PyMuPDF

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
    
    # A opção mágica para PDFs de editoras
    usar_ocr = st.checkbox("Usar OCR com IA (Recomendado se o texto sair embaralhado)", value=False, 
                           help="O app vai transformar as páginas em imagens e pedir para o Gemini ler. Demora um pouco mais, mas o texto fica perfeito.")
    
    if uploaded_file and st.button("Processar PDF e Criar Plano"):
        with st.spinner("Extraindo texto..."):
            try:
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                full_text = ""
                
                if usar_ocr:
                    st.warning("A IA está lendo cada página. Por favor, aguarde (pode levar alguns minutos)...")
                    progresso = st.progress(0)
                    total_paginas = len(doc)
                    
                    for i, page in enumerate(doc):
                        # Converte a página em imagem
                        pix = page.get_pixmap(dpi=150) # 150 DPI é suficiente para ler texto
                        img_bytes = pix.tobytes("jpeg")
                        
                        # Pede para a IA extrair o texto
                        prompt = "Extraia exatamente o texto desta imagem, mantendo a pontuação e parágrafos. Não adicione comentários, retorne apenas o texto do livro."
                        texto_pagina = ask_gemini_vision(img_bytes, prompt)
                        
                        # Remove mensagens de erro da IA caso ocorram
                        if "⚠️ Erro na IA" not in texto_pagina and "⚠️ API Key" not in texto_pagina:
                            full_text += texto_pagina + " "
                            
                        progresso.progress((i + 1) / total_paginas)
                else:
                    # Método tradicional (para PDFs normais)
                    for page in doc:
                        extracted = page.get_text("text")
                        if extracted:
                            full_text += extracted + " "
                
                # Limpeza básica
                full_text = re.sub(r'\\s+', ' ', full_text)
                palavras = full_text.split()
                
                if len(palavras) < 100:
                    st.error("O PDF não pôde ser lido. Verifique se a API Key está configurada ou se o PDF é válido.")
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
                    import time
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
                st.session_state["resumo_pdf"] = "" # Limpa o resumo anterior
                st.rerun()
        with col2:
            if st.button("🪄 Resumo com IA", use_container_width=True):
                with st.spinner("O Mentor está resumindo o texto de hoje..."):
                    prompt = f"Resuma o seguinte trecho de um livro de forma inspiradora e direta, destacando os principais aprendizados:\\n\\n{chunk['text_content']}"
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
'''
    try:
        ast.parse(novo_mente)
        mente_file.write_text(novo_mente, encoding="utf-8")
        print("[OK] Corrigido: ui/pages/02_Mente.py (Opção de OCR via IA adicionada)")
    except SyntaxError as e:
        print(f"[ERRO] Falha na validação de sintaxe da página Mente: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 3. Reiniciar o servidor
    # -----------------------------------------------------------------------
    print("\nReiniciando o servidor...")
    os.system('taskkill /F /FI "WINDOWTITLE eq Projeto Samurai" >nul 2>&1')
    os.startfile(BASE / "INICIAR.bat")
    print("[OK] Servidor reiniciado. Leitor OCR pronto!")

if __name__ == "__main__":
    aplicar_patch()
```


## `gerar_codigo.py`

```python
"""
Gera um arquivo Markdown com o mapa completo do projeto.
Ignora __pycache__, data, .venv, .git, .idea, .vscode, node_modules e binários.
Uso:  py -3 gerar_codigo.py
Saída: PROJETO_SAMURAI.md na raiz.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent
IGNORE_DIRS = {
    "__pycache__", "data", ".venv", "venv", ".git",
    ".idea", ".vscode", "node_modules", ".pytest_cache",
}
IGNORE_EXT = {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg"}
OUTPUT = BASE / "PROJETO_SAMURAI.md"

LANG_MAP = {
    ".py": "python", ".bat": "bat", ".txt": "text",
    ".md": "markdown", ".json": "json", ".toml": "toml",
    ".css": "css", ".html": "html", ".js": "javascript",
}


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in IGNORE_EXT:
        return True
    return False


def generate() -> None:
    linhas: list[str] = ["# ⚔️ Projeto Samurai — Mapa do Código\n"]
    linhas.append("> Gerado automaticamente por `gerar_codigo.py`\n")
    linhas.append(f"> Raiz: `{BASE.name}`\n\n---\n")

    arquivos = sorted(
        p for p in BASE.rglob("*")
        if p.is_file() and not is_ignored(p.relative_to(BASE))
    )

    for path in arquivos:
        rel = path.relative_to(BASE)
        lang = LANG_MAP.get(path.suffix.lower(), "text")
        linhas.append(f"\n## `{rel.as_posix()}`\n")
        try:
            conteudo = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            conteudo = "<<arquivo binário ou ilegível>>"
        linhas.append(f"```{lang}")
        linhas.append(conteudo)
        linhas.append("```\n")

    OUTPUT.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[OK] Mapa gerado: {OUTPUT}")
    print(f"[OK] {len(arquivos)} arquivo(s) incluído(s).")


if __name__ == "__main__":
    generate()

```


## `INICIAR.bat`

```bat
@echo off
title Projeto Samurai
cd /d "%~dp0"

echo ==================================================
echo    PROJETO SAMURAI - Iniciando ambiente
echo ==================================================
echo.

echo [1/3] Verificando dependencias...
py -3 -m pip install --quiet --upgrade pip
py -3 -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

echo [2/3] Iniciando Streamlit na porta 8501...
echo [3/3] O navegador abrira automaticamente.
echo.
echo (Para encerrar o servidor, feche esta janela ou pressione Ctrl+C)
echo.

py -3 -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo Servidor encerrado.
pause

```


## `PROJETO_SAMURAI.md`

```markdown
# ⚔️ Projeto Samurai — Mapa do Código

> Gerado automaticamente por `gerar_codigo.py`

> Raiz: `Projeto Samurai`

---


## `.streamlit/config.toml`

```toml
[theme]
base="dark"
primaryColor="#8B0000"
backgroundColor="#0B0B0B"
secondaryBackgroundColor="#171717"
textColor="#F2F2F2"
font="sans serif"

```


## `app.py`

```python
"""
Projeto Samurai — Sistema Operacional Pessoal.
Entry point Streamlit. Configura tema, navegação e injeta CSS.
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from core.schema import init_db

init_db()

st.set_page_config(
    page_title="Projeto Samurai ⚔️",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

SAMURAI_CSS = """
<style>
:root {
    --s-red:        #8B0000;
    --s-dark-red:   #5C0000;
    --s-black:      #0B0B0B;
    --s-gray:       #171717;
    --s-gray-soft:  #1F1F1F;
    --s-white:      #FFFFFF;
    --s-white-soft: #CCCCCC;
}

/* Força o fundo escuro no app */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--s-black) !important;
}

/* Força cor do texto em TODOS os elementos comuns e containers do Streamlit */
h1, h2, h3, h4, h5, h6, p, span, li, label, 
div[data-testid="stMarkdownContainer"] *, 
[data-testid="stWidgetLabel"] * {
    color: var(--s-white) !important;
}

/* Linha vermelha embaixo do H1 */
h1 {
    border-bottom: 2px solid var(--s-red) !important;
    padding-bottom: 8px !important;
    letter-spacing: .5px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--s-gray) !important;
    border-right: 1px solid var(--s-red) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--s-white) !important;
}

/* Cards Customizados */
.samurai-card {
    background-color: var(--s-gray-soft) !important;
    border-left: 4px solid var(--s-red) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
}
.samurai-card .titulo {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--s-white-soft) !important;
    margin-bottom: 6px !important;
    font-weight: 600 !important;
}
.samurai-card .valor {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--s-white) !important;
}
.samurai-card .detalhe {
    font-size: 0.85rem !important;
    color: var(--s-white-soft) !important;
    margin-top: 6px !important;
}

/* Botões */
.stButton > button, .stFormSubmitButton > button {
    background-color: var(--s-red) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-dark-red) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--s-dark-red) !important;
    border-color: var(--s-white) !important;
}

/* Barras de Progresso */
.stProgress > div > div > div > div {
    background-color: var(--s-red) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--s-gray) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-red) !important;
}

/* Divisores e Caixas de Info/Alerta */
hr { border-color: var(--s-red) !important; opacity: .5 !important; }
.stAlert { 
    background-color: var(--s-gray-soft) !important; 
    color: var(--s-white) !important; 
    border: 1px solid var(--s-red) !important; 
}
.stAlert * { color: var(--s-white) !important; }
</style>
"""

st.markdown(SAMURAI_CSS, unsafe_allow_html=True)


home = st.Page("ui/pages/00_Home.py", title="🏯 Dojo", default=True)
consistencia = st.Page("ui/pages/07_Consistencia.py", title="🎯 Consistência")
corpo = st.Page("ui/pages/01_Corpo.py", title="💪 Corpo")
mente = st.Page("ui/pages/02_Mente.py", title="🧠 Mente")
informacao = st.Page("ui/pages/03_Informacao.py", title="📰 Informação")
patrimonio = st.Page("ui/pages/04_Patrimonio.py", title="💎 Patrimônio")
descanso = st.Page("ui/pages/05_Descanso.py", title="🌿 Descanso & Lazer")
autoconhecimento = st.Page("ui/pages/06_Autoconhecimento.py", title="🪞 Autoconhecimento")
religiao = st.Page("ui/pages/08_Religiao.py", title="🕊️ Religião")
biblia = st.Page("ui/pages/09_Biblia.py", title="📖 Bíblia")

pg = st.navigation(
    {
        "⚔️ Comando": [home, consistencia],
        "🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento, religiao, biblia],
    }
)


# --- Configuração da IA na Sidebar ---
from services.ai import get_api_key

with st.sidebar:
    st.divider()
    st.markdown("### ⚙️ IA Configuração")
    key_atual = get_api_key()
    
    if key_atual and key_atual != "COLE_SUA_CHAVE_AQUI":
        st.success("IA Conectada 🟢")
    else:
        st.warning("IA Desconectada 🔴")
        nova_chave = st.text_input("Cole sua API Key do Gemini:", type="password", placeholder="AIzaSy...")
        if st.button("Salvar e Ativar IA", use_container_width=True):
            if nova_chave.strip():
                config_file = BASE_DIR / "config.json"
                config_file.write_text(json.dumps({"gemini_api_key": nova_chave.strip()}, indent=4), encoding="utf-8")
                st.success("Chave salva com sucesso!")
                import time
                time.sleep(1)
                st.rerun()

pg.run()


```


## `assets/.gitkeep`

```text

```


## `config.json`

```json
{
    "gemini_api_key": "AQ.Ab8RN6I_Bq6xAq5tGVYh87pnioxbyxprdwD0UqKdSw8gzkE5zw"
}

```


## `core/__init__.py`

```python
"""Núcleo do Projeto Samurai (banco, schema, utilitários)."""

```


## `core/database.py`

```python
"""
Conexão SQLite centralizada.
- WAL mode para leituras concorrentes.
- Lock em memória para evitar writes simultâneos (Streamlit é multithread).
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "samurai.db"

_lock = threading.RLock()


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão configurada. O caller é responsável por fechar."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def execute(sql: str, params: tuple = ()) -> int:
    """Executa um INSERT/UPDATE/DELETE. Retorna lastrowid."""
    with _lock:
        conn = get_connection()
        try:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()


def executemany(sql: str, seq_params: list[tuple]) -> None:
    with _lock:
        conn = get_connection()
        try:
            conn.executemany(sql, seq_params)
            conn.commit()
        finally:
            conn.close()


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _lock:
        conn = get_connection()
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with _lock:
        conn = get_connection()
        try:
            return conn.execute(sql, params).fetchone()
        finally:
            conn.close()

```


## `core/schema.py`

```python
"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    
    # Blocos de Leitura de PDFs (Mente)
    """
    CREATE TABLE IF NOT EXISTS book_chunks (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL,
        chunk_index  INTEGER NOT NULL,
        text_content TEXT    NOT NULL,
        completed    INTEGER NOT NULL DEFAULT 0,
        UNIQUE (book_title, chunk_index)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
    ("Oração", "Religião", "Momento de conexão com Deus."),
    ("Leitura Bíblica", "Religião", "Ler um trecho da Palavra."),
    ("Gratidão a Deus", "Religião", "Agradecer pelas bênçãos do dia."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    # Seed inteligente: insere apenas se o hábito ainda não existir
    for name, pillar, desc in SEED_HABITS:
        if not query_one("SELECT id FROM habits WHERE name = ?", (name,)):
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )

```


## `criar_projeto_samurai.py`

```python
import ast
import os
import sys
from pathlib import Path

BASE = Path(r"C:\Users\Ricardo Fernandes\Desktop\Projeto Samurai")

def aplicar_patch():
    print("=" * 60)
    print("⚔️  PATCH: CORREÇÃO DO LEITOR PDF E CRIAÇÃO DA BÍBLIA")
    print("=" * 60)

    if not BASE.exists():
        print(f"[ERRO] Pasta do projeto não encontrada: {BASE}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 1. Atualizar requirements.txt (Trocar pypdf por pymupdf)
    # -----------------------------------------------------------------------
    req_file = BASE / "requirements.txt"
    req_txt = req_file.read_text(encoding="utf-8")
    
    # Remove pypdf se existir
    req_txt = "\n".join([line for line in req_txt.splitlines() if "pypdf" not in line])
    
    # Adiciona pymupdf
    if "pymupdf" not in req_txt:
        req_txt += "\npymupdf>=1.24.0\n"
    
    req_file.write_text(req_txt, encoding="utf-8")
    print("[OK] Corrigido: requirements.txt (pymupdf adicionado)")

    # -----------------------------------------------------------------------
    # 2. Corrigir 02_Mente.py (Usar PyMuPDF para extrair texto)
    # -----------------------------------------------------------------------
    mente_file = BASE / "ui" / "pages" / "02_Mente.py"
    novo_mente = '''import streamlit as st
import sys
from pathlib import Path
import re
import fitz  # PyMuPDF

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

# --- UPLOAD DE PDF ---
with st.expander("📚 Enviar Novo Livro (PDF)"):
    uploaded_file = st.file_uploader("Selecione o PDF do livro", type=["pdf"])
    palavras_por_dia = st.number_input("Meta de leitura diária (palavras)", min_value=200, max_value=5000, value=1000, step=100)
    
    if uploaded_file and st.button("Processar PDF e Criar Plano"):
        with st.spinner("Extraindo texto e dividindo a leitura..."):
            try:
                # Usando PyMuPDF para extração muito mais precisa
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                full_text = ""
                for page in doc:
                    full_text += page.get_text("text") + " "
                
                # Limpeza básica
                full_text = re.sub(r'\\s+', ' ', full_text)
                palavras = full_text.split()
                
                if len(palavras) < 100:
                    st.error("O PDF parece conter pouco texto ou é composto por imagens (necessita OCR).")
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
        
        # Usamos st.write em vez de HTML puro para evitar quebras por caracteres especiais do livro
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
                st.rerun()
        with col2:
            if st.button("🪄 Resumo com IA", use_container_width=True):
                with st.spinner("O Mentor está resumindo o texto de hoje..."):
                    prompt = f"Resuma o seguinte trecho de um livro de forma inspiradora e direta, destacando os principais aprendizados:\\n\\n{chunk['text_content']}"
                    resumo = ask_gemini(prompt)
                    st.session_state["resumo_pdf"] = resumo
        
        if "resumo_pdf" in st.session_state:
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
                    <div class="titulo">Resumo do Mentor</div>
                    <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6;">{st.session_state['resumo_pdf']}</div>
                </div>""",
                unsafe_allow_html=True
            )
else:
    st.info("📖 Nenhum livro em andamento. Envie um PDF na seção acima para começar.")
'''
    try:
        ast.parse(novo_mente)
        mente_file.write_text(novo_mente, encoding="utf-8")
        print("[OK] Corrigido: ui/pages/02_Mente.py (Agora usa PyMuPDF)")
    except SyntaxError as e:
        print(f"[ERRO] Falha na validação da Mente: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 3. Criar 09_Biblia.py à prova de falhas de string
    # -----------------------------------------------------------------------
    biblia_file = BASE / "ui" / "pages" / "09_Biblia.py"
    
    # Usaremos concatenação normal em vez de f-strings gigantes para o texto bíblico
    biblia_codigo = '''import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db

init_db()

st.title("📖 Bíblia")
st.caption("Plano de leitura em 1 ano — Almeida Corrigida Fiel (ACF)")

proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")

if not proximo:
    st.success("🎉 Parabéns! Você concluiu a leitura da Bíblia em 1 ano!")
    st.balloons()
else:
    day = proximo["day"]
    st.subheader(f"Dia {day} de 365")

    plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
    if plano:
        start_id = plano["start_verse_id"]
        end_id = plano["end_verse_id"]

        versiculos = query_all(
            "SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id",
            (start_id, end_id)
        )

        if versiculos:
            primeiro = versiculos[0]
            ultimo = versiculos[-1]
            
            if primeiro["book_name"] == ultimo["book_name"]:
                if primeiro["chapter"] == ultimo["chapter"]:
                    ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']}-{ultimo['verse']}"
                else:
                    ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']} a {ultimo['chapter']}:{ultimo['verse']}"
            else:
                ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']} a {ultimo['book_name']} {ultimo['chapter']}:{ultimo['verse']}"

            st.markdown(f"**Leitura de hoje:** {ref}")

            # Monta o texto formatado de forma segura (sem f-string)
            texto_limpo = ""
            for v in versiculos:
                # Escapa chaves para não quebrar o HTML/Markdown
                safe_text = str(v['text']).replace("{", "{{").replace("}", "}}")
                texto_limpo += f"**{v['verse']}** {safe_text}  \\n"

            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 500px; overflow-y: auto;">
                    <div style="color: #F2F2F2; font-size: 1rem; line-height: 1.8;">
                        {texto_limpo}
                    </div>
                </div>""",
                unsafe_allow_html=True
            )

            if st.button("✅ Confirmar Leitura e Avançar", use_container_width=True):
                execute("UPDATE reading_progress SET completed = 1 WHERE day = ?", (day,))
                st.success(f"Leitura do Dia {day} concluída! Avançando...")
                st.rerun()
        else:
            st.error("Erro ao carregar os versículos. O plano pode estar corrompido.")
    else:
        st.error(f"Plano para o dia {day} não encontrado.")
'''
    
    try:
        ast.parse(biblia_codigo)
        biblia_file.write_text(biblia_codigo, encoding="utf-8")
        print("[OK] Criado: ui/pages/09_Biblia.py (Sintaxe corrigida)")
    except SyntaxError as e:
        print(f"[ERRO] Falha na criação da Bíblia: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 4. Garantir que o app.py tem a aba Bíblia e baixar os dados (se necessário)
    # -----------------------------------------------------------------------
    app_file = BASE / "app.py"
    app_txt = app_file.read_text(encoding="utf-8")

    if "09_Biblia.py" not in app_txt:
        app_txt = app_txt.replace(
            'religiao = st.Page("ui/pages/08_Religiao.py", title="🕊️ Religião")',
            'religiao = st.Page("ui/pages/08_Religiao.py", title="🕊️ Religião")\nbiblia = st.Page("ui/pages/09_Biblia.py", title="📖 Bíblia")'
        )
        app_txt = app_txt.replace(
            '"🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento, religiao],',
            '"🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento, religiao, biblia],'
        )
        app_file.write_text(app_txt, encoding="utf-8")
        print("[OK] Corrigido: app.py (Aba Bíblia incluída no menu)")

    # -----------------------------------------------------------------------
    # 5. Baixar e popular a Bíblia (caso o patch anterior tenha falhado)
    # -----------------------------------------------------------------------
    from core.database import query_one, execute
    
    # Adiciona a tabela se ela não existir
    execute("""
        CREATE TABLE IF NOT EXISTS bible_verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_name TEXT NOT NULL, book_abbrev TEXT, chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL, text TEXT NOT NULL, word_count INTEGER NOT NULL
        )
    """)
    execute("CREATE TABLE IF NOT EXISTS reading_plan (day INTEGER PRIMARY KEY, start_verse_id INTEGER, end_verse_id INTEGER)")
    execute("CREATE TABLE IF NOT EXISTS reading_progress (day INTEGER PRIMARY KEY, completed INTEGER DEFAULT 0)")

    count = query_one("SELECT COUNT(*) AS c FROM bible_verses")["c"]
    if count == 0:
        print("[INFO] Baixando o texto bíblico (ACF)...")
        import requests
        url = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/pt_acf.json"
        try:
            response = requests.get(url, timeout=30)
            data = response.json()
            
            for book in data:
                for chap_idx, chapter in enumerate(book["chapters"], start=1):
                    for verse_idx, verse_text in enumerate(chapter, start=1):
                        execute(
                            "INSERT INTO bible_verses (book_name, book_abbrev, chapter, verse, text, word_count) VALUES (?, ?, ?, ?, ?, ?)",
                            (book["name"], book["abbrev"], chap_idx, verse_idx, verse_text, len(verse_text.split()))
                        )
            print(f"[OK] {query_one('SELECT COUNT(*) AS c FROM bible_verses')['c']} versículos inseridos.")
        except Exception as e:
            print(f"[ERRO] Falha ao baixar a Bíblia: {e}")
            print("Inicie o app e verifique sua conexão para rodar o patch novamente.")

    count_plan = query_one("SELECT COUNT(*) AS c FROM reading_plan")["c"]
    if count_plan == 0:
        print("[INFO] Gerando o plano de leitura...")
        verses = query_all("SELECT id, word_count FROM bible_verses ORDER BY id")
        if verses:
            total_words = sum(v["word_count"] for v in verses)
            target = total_words / 365
            current_day = 1
            accumulated = 0
            start_id = verses[0]["id"]

            for i, v in enumerate(verses):
                accumulated += v["word_count"]
                if (accumulated >= target and current_day < 365) or i == len(verses) - 1:
                    execute("INSERT INTO reading_plan (day, start_verse_id, end_verse_id) VALUES (?, ?, ?)", (current_day, start_id, v["id"]))
                    current_day += 1
                    accumulated = 0
                    if i < len(verses) - 1: start_id = verses[i + 1]["id"]

            while current_day <= 365:
                execute("INSERT INTO reading_plan (day, start_verse_id, end_verse_id) VALUES (?, ?, ?)", (current_day, start_id, verses[-1]["id"]))
                current_day += 1
            print(f"[OK] Plano gerado com sucesso.")

    count_prog = query_one("SELECT COUNT(*) AS c FROM reading_progress")["c"]
    if count_prog == 0:
        for day in range(1, 366):
            execute("INSERT INTO reading_progress (day, completed) VALUES (?, 0)", (day,))
        print("[OK] Progresso inicializado.")

    # -----------------------------------------------------------------------
    # 6. Reiniciar o servidor
    # -----------------------------------------------------------------------
    print("\nReiniciando o servidor (instalando PyMuPDF)...")
    os.system('taskkill /F /FI "WINDOWTITLE eq Projeto Samurai" >nul 2>&1')
    os.startfile(BASE / "INICIAR.bat")
    print("[OK] Tudo pronto!")

if __name__ == "__main__":
    aplicar_patch()
```


## `gerar_codigo.py`

```python
"""
Gera um arquivo Markdown com o mapa completo do projeto.
Ignora __pycache__, data, .venv, .git, .idea, .vscode, node_modules e binários.
Uso:  py -3 gerar_codigo.py
Saída: PROJETO_SAMURAI.md na raiz.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent
IGNORE_DIRS = {
    "__pycache__", "data", ".venv", "venv", ".git",
    ".idea", ".vscode", "node_modules", ".pytest_cache",
}
IGNORE_EXT = {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg"}
OUTPUT = BASE / "PROJETO_SAMURAI.md"

LANG_MAP = {
    ".py": "python", ".bat": "bat", ".txt": "text",
    ".md": "markdown", ".json": "json", ".toml": "toml",
    ".css": "css", ".html": "html", ".js": "javascript",
}


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in IGNORE_EXT:
        return True
    return False


def generate() -> None:
    linhas: list[str] = ["# ⚔️ Projeto Samurai — Mapa do Código\n"]
    linhas.append("> Gerado automaticamente por `gerar_codigo.py`\n")
    linhas.append(f"> Raiz: `{BASE.name}`\n\n---\n")

    arquivos = sorted(
        p for p in BASE.rglob("*")
        if p.is_file() and not is_ignored(p.relative_to(BASE))
    )

    for path in arquivos:
        rel = path.relative_to(BASE)
        lang = LANG_MAP.get(path.suffix.lower(), "text")
        linhas.append(f"\n## `{rel.as_posix()}`\n")
        try:
            conteudo = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            conteudo = "<<arquivo binário ou ilegível>>"
        linhas.append(f"```{lang}")
        linhas.append(conteudo)
        linhas.append("```\n")

    OUTPUT.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[OK] Mapa gerado: {OUTPUT}")
    print(f"[OK] {len(arquivos)} arquivo(s) incluído(s).")


if __name__ == "__main__":
    generate()

```


## `INICIAR.bat`

```bat
@echo off
title Projeto Samurai
cd /d "%~dp0"

echo ==================================================
echo    PROJETO SAMURAI - Iniciando ambiente
echo ==================================================
echo.

echo [1/3] Verificando dependencias...
py -3 -m pip install --quiet --upgrade pip
py -3 -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

echo [2/3] Iniciando Streamlit na porta 8501...
echo [3/3] O navegador abrira automaticamente.
echo.
echo (Para encerrar o servidor, feche esta janela ou pressione Ctrl+C)
echo.

py -3 -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo Servidor encerrado.
pause

```


## `PROJETO_SAMURAI.md`

```markdown
# ⚔️ Projeto Samurai — Mapa do Código

> Gerado automaticamente por `gerar_codigo.py`

> Raiz: `Projeto Samurai`

---


## `.streamlit/config.toml`

```toml
[theme]
base="dark"
primaryColor="#8B0000"
backgroundColor="#0B0B0B"
secondaryBackgroundColor="#171717"
textColor="#F2F2F2"
font="sans serif"

```


## `app.py`

```python
"""
Projeto Samurai — Sistema Operacional Pessoal.
Entry point Streamlit. Configura tema, navegação e injeta CSS.
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from core.schema import init_db

init_db()

st.set_page_config(
    page_title="Projeto Samurai ⚔️",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

SAMURAI_CSS = """
<style>
:root {
    --s-red:        #8B0000;
    --s-dark-red:   #5C0000;
    --s-black:      #0B0B0B;
    --s-gray:       #171717;
    --s-gray-soft:  #1F1F1F;
    --s-white:      #FFFFFF;
    --s-white-soft: #CCCCCC;
}

/* Força o fundo escuro no app */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--s-black) !important;
}

/* Força cor do texto em TODOS os elementos comuns e containers do Streamlit */
h1, h2, h3, h4, h5, h6, p, span, li, label, 
div[data-testid="stMarkdownContainer"] *, 
[data-testid="stWidgetLabel"] * {
    color: var(--s-white) !important;
}

/* Linha vermelha embaixo do H1 */
h1 {
    border-bottom: 2px solid var(--s-red) !important;
    padding-bottom: 8px !important;
    letter-spacing: .5px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--s-gray) !important;
    border-right: 1px solid var(--s-red) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--s-white) !important;
}

/* Cards Customizados */
.samurai-card {
    background-color: var(--s-gray-soft) !important;
    border-left: 4px solid var(--s-red) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
}
.samurai-card .titulo {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--s-white-soft) !important;
    margin-bottom: 6px !important;
    font-weight: 600 !important;
}
.samurai-card .valor {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--s-white) !important;
}
.samurai-card .detalhe {
    font-size: 0.85rem !important;
    color: var(--s-white-soft) !important;
    margin-top: 6px !important;
}

/* Botões */
.stButton > button, .stFormSubmitButton > button {
    background-color: var(--s-red) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-dark-red) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--s-dark-red) !important;
    border-color: var(--s-white) !important;
}

/* Barras de Progresso */
.stProgress > div > div > div > div {
    background-color: var(--s-red) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--s-gray) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-red) !important;
}

/* Divisores e Caixas de Info/Alerta */
hr { border-color: var(--s-red) !important; opacity: .5 !important; }
.stAlert { 
    background-color: var(--s-gray-soft) !important; 
    color: var(--s-white) !important; 
    border: 1px solid var(--s-red) !important; 
}
.stAlert * { color: var(--s-white) !important; }
</style>
"""

st.markdown(SAMURAI_CSS, unsafe_allow_html=True)


home = st.Page("ui/pages/00_Home.py", title="🏯 Dojo", default=True)
consistencia = st.Page("ui/pages/07_Consistencia.py", title="🎯 Consistência")
corpo = st.Page("ui/pages/01_Corpo.py", title="💪 Corpo")
mente = st.Page("ui/pages/02_Mente.py", title="🧠 Mente")
informacao = st.Page("ui/pages/03_Informacao.py", title="📰 Informação")
patrimonio = st.Page("ui/pages/04_Patrimonio.py", title="💎 Patrimônio")
descanso = st.Page("ui/pages/05_Descanso.py", title="🌿 Descanso & Lazer")
autoconhecimento = st.Page("ui/pages/06_Autoconhecimento.py", title="🪞 Autoconhecimento")
religiao = st.Page("ui/pages/08_Religiao.py", title="🕊️ Religião")

pg = st.navigation(
    {
        "⚔️ Comando": [home, consistencia],
        "🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento, religiao],
    }
)


# --- Configuração da IA na Sidebar ---
from services.ai import get_api_key

with st.sidebar:
    st.divider()
    st.markdown("### ⚙️ IA Configuração")
    key_atual = get_api_key()
    
    if key_atual and key_atual != "COLE_SUA_CHAVE_AQUI":
        st.success("IA Conectada 🟢")
    else:
        st.warning("IA Desconectada 🔴")
        nova_chave = st.text_input("Cole sua API Key do Gemini:", type="password", placeholder="AIzaSy...")
        if st.button("Salvar e Ativar IA", use_container_width=True):
            if nova_chave.strip():
                config_file = BASE_DIR / "config.json"
                config_file.write_text(json.dumps({"gemini_api_key": nova_chave.strip()}, indent=4), encoding="utf-8")
                st.success("Chave salva com sucesso!")
                import time
                time.sleep(1)
                st.rerun()

pg.run()


```


## `assets/.gitkeep`

```text

```


## `config.json`

```json
{
    "gemini_api_key": "AQ.Ab8RN6I_Bq6xAq5tGVYh87pnioxbyxprdwD0UqKdSw8gzkE5zw"
}

```


## `core/__init__.py`

```python
"""Núcleo do Projeto Samurai (banco, schema, utilitários)."""

```


## `core/database.py`

```python
"""
Conexão SQLite centralizada.
- WAL mode para leituras concorrentes.
- Lock em memória para evitar writes simultâneos (Streamlit é multithread).
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "samurai.db"

_lock = threading.RLock()


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão configurada. O caller é responsável por fechar."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def execute(sql: str, params: tuple = ()) -> int:
    """Executa um INSERT/UPDATE/DELETE. Retorna lastrowid."""
    with _lock:
        conn = get_connection()
        try:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()


def executemany(sql: str, seq_params: list[tuple]) -> None:
    with _lock:
        conn = get_connection()
        try:
            conn.executemany(sql, seq_params)
            conn.commit()
        finally:
            conn.close()


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _lock:
        conn = get_connection()
        try:
            return conn.execute(sql, params).fetchall()
        finally:
            conn.close()


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with _lock:
        conn = get_connection()
        try:
            return conn.execute(sql, params).fetchone()
        finally:
            conn.close()

```


## `core/schema.py`

```python
"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    
    # Blocos de Leitura de PDFs (Mente)
    """
    CREATE TABLE IF NOT EXISTS book_chunks (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL,
        chunk_index  INTEGER NOT NULL,
        text_content TEXT    NOT NULL,
        completed    INTEGER NOT NULL DEFAULT 0,
        UNIQUE (book_title, chunk_index)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
    ("Oração", "Religião", "Momento de conexão com Deus."),
    ("Leitura Bíblica", "Religião", "Ler um trecho da Palavra."),
    ("Gratidão a Deus", "Religião", "Agradecer pelas bênçãos do dia."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    # Seed inteligente: insere apenas se o hábito ainda não existir
    for name, pillar, desc in SEED_HABITS:
        if not query_one("SELECT id FROM habits WHERE name = ?", (name,)):
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )

```


## `criar_projeto_samurai.py`

```python
import ast
import os
import sys
from pathlib import Path

BASE = Path(r"C:\Users\Ricardo Fernandes\Desktop\Projeto Samurai")

def aplicar_patch():
    print("=" * 60)
    print("⚔️  PATCH: CORREÇÃO DO LEITOR PDF E CRIAÇÃO DA BÍBLIA")
    print("=" * 60)

    if not BASE.exists():
        print(f"[ERRO] Pasta do projeto não encontrada: {BASE}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 1. Atualizar requirements.txt (Trocar pypdf por pymupdf)
    # -----------------------------------------------------------------------
    req_file = BASE / "requirements.txt"
    req_txt = req_file.read_text(encoding="utf-8")
    
    # Remove pypdf se existir
    req_txt = "\n".join([line for line in req_txt.splitlines() if "pypdf" not in line])
    
    # Adiciona pymupdf
    if "pymupdf" not in req_txt:
        req_txt += "\npymupdf>=1.24.0\n"
    
    req_file.write_text(req_txt, encoding="utf-8")
    print("[OK] Corrigido: requirements.txt (pymupdf adicionado)")

    # -----------------------------------------------------------------------
    # 2. Corrigir 02_Mente.py (Usar PyMuPDF para extrair texto)
    # -----------------------------------------------------------------------
    mente_file = BASE / "ui" / "pages" / "02_Mente.py"
    novo_mente = '''import streamlit as st
import sys
from pathlib import Path
import re
import fitz  # PyMuPDF

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

# --- UPLOAD DE PDF ---
with st.expander("📚 Enviar Novo Livro (PDF)"):
    uploaded_file = st.file_uploader("Selecione o PDF do livro", type=["pdf"])
    palavras_por_dia = st.number_input("Meta de leitura diária (palavras)", min_value=200, max_value=5000, value=1000, step=100)
    
    if uploaded_file and st.button("Processar PDF e Criar Plano"):
        with st.spinner("Extraindo texto e dividindo a leitura..."):
            try:
                # Usando PyMuPDF para extração muito mais precisa
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                full_text = ""
                for page in doc:
                    full_text += page.get_text("text") + " "
                
                # Limpeza básica
                full_text = re.sub(r'\\s+', ' ', full_text)
                palavras = full_text.split()
                
                if len(palavras) < 100:
                    st.error("O PDF parece conter pouco texto ou é composto por imagens (necessita OCR).")
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
        
        # Usamos st.write em vez de HTML puro para evitar quebras por caracteres especiais do livro
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
                st.rerun()
        with col2:
            if st.button("🪄 Resumo com IA", use_container_width=True):
                with st.spinner("O Mentor está resumindo o texto de hoje..."):
                    prompt = f"Resuma o seguinte trecho de um livro de forma inspiradora e direta, destacando os principais aprendizados:\\n\\n{chunk['text_content']}"
                    resumo = ask_gemini(prompt)
                    st.session_state["resumo_pdf"] = resumo
        
        if "resumo_pdf" in st.session_state:
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
                    <div class="titulo">Resumo do Mentor</div>
                    <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6;">{st.session_state['resumo_pdf']}</div>
                </div>""",
                unsafe_allow_html=True
            )
else:
    st.info("📖 Nenhum livro em andamento. Envie um PDF na seção acima para começar.")
'''
    try:
        ast.parse(novo_mente)
        mente_file.write_text(novo_mente, encoding="utf-8")
        print("[OK] Corrigido: ui/pages/02_Mente.py (Agora usa PyMuPDF)")
    except SyntaxError as e:
        print(f"[ERRO] Falha na validação da Mente: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 3. Criar 09_Biblia.py à prova de falhas de string
    # -----------------------------------------------------------------------
    biblia_file = BASE / "ui" / "pages" / "09_Biblia.py"
    
    # Usaremos concatenação normal em vez de f-strings gigantes para o texto bíblico
    biblia_codigo = '''import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db

init_db()

st.title("📖 Bíblia")
st.caption("Plano de leitura em 1 ano — Almeida Corrigida Fiel (ACF)")

proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")

if not proximo:
    st.success("🎉 Parabéns! Você concluiu a leitura da Bíblia em 1 ano!")
    st.balloons()
else:
    day = proximo["day"]
    st.subheader(f"Dia {day} de 365")

    plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
    if plano:
        start_id = plano["start_verse_id"]
        end_id = plano["end_verse_id"]

        versiculos = query_all(
            "SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id",
            (start_id, end_id)
        )

        if versiculos:
            primeiro = versiculos[0]
            ultimo = versiculos[-1]
            
            if primeiro["book_name"] == ultimo["book_name"]:
                if primeiro["chapter"] == ultimo["chapter"]:
                    ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']}-{ultimo['verse']}"
                else:
                    ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']} a {ultimo['chapter']}:{ultimo['verse']}"
            else:
                ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']} a {ultimo['book_name']} {ultimo['chapter']}:{ultimo['verse']}"

            st.markdown(f"**Leitura de hoje:** {ref}")

            # Monta o texto formatado de forma segura (sem f-string)
            texto_limpo = ""
            for v in versiculos:
                # Escapa chaves para não quebrar o HTML/Markdown
                safe_text = str(v['text']).replace("{", "{{").replace("}", "}}")
                texto_limpo += f"**{v['verse']}** {safe_text}  \\n"

            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 500px; overflow-y: auto;">
                    <div style="color: #F2F2F2; font-size: 1rem; line-height: 1.8;">
                        {texto_limpo}
                    </div>
                </div>""",
                unsafe_allow_html=True
            )

            if st.button("✅ Confirmar Leitura e Avançar", use_container_width=True):
                execute("UPDATE reading_progress SET completed = 1 WHERE day = ?", (day,))
                st.success(f"Leitura do Dia {day} concluída! Avançando...")
                st.rerun()
        else:
            st.error("Erro ao carregar os versículos. O plano pode estar corrompido.")
    else:
        st.error(f"Plano para o dia {day} não encontrado.")
'''
    
    try:
        ast.parse(biblia_codigo)
        biblia_file.write_text(biblia_codigo, encoding="utf-8")
        print("[OK] Criado: ui/pages/09_Biblia.py (Sintaxe corrigida)")
    except SyntaxError as e:
        print(f"[ERRO] Falha na criação da Bíblia: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 4. Garantir que o app.py tem a aba Bíblia e baixar os dados (se necessário)
    # -----------------------------------------------------------------------
    app_file = BASE / "app.py"
    app_txt = app_file.read_text(encoding="utf-8")

    if "09_Biblia.py" not in app_txt:
        app_txt = app_txt.replace(
            'religiao = st.Page("ui/pages/08_Religiao.py", title="🕊️ Religião")',
            'religiao = st.Page("ui/pages/08_Religiao.py", title="🕊️ Religião")\nbiblia = st.Page("ui/pages/09_Biblia.py", title="📖 Bíblia")'
        )
        app_txt = app_txt.replace(
            '"🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento, religiao],',
            '"🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento, religiao, biblia],'
        )
        app_file.write_text(app_txt, encoding="utf-8")
        print("[OK] Corrigido: app.py (Aba Bíblia incluída no menu)")

    # -----------------------------------------------------------------------
    # 5. Baixar e popular a Bíblia (caso o patch anterior tenha falhado)
    # -----------------------------------------------------------------------
    from core.database import query_one, execute
    
    # Adiciona a tabela se ela não existir
    execute("""
        CREATE TABLE IF NOT EXISTS bible_verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_name TEXT NOT NULL, book_abbrev TEXT, chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL, text TEXT NOT NULL, word_count INTEGER NOT NULL
        )
    """)
    execute("CREATE TABLE IF NOT EXISTS reading_plan (day INTEGER PRIMARY KEY, start_verse_id INTEGER, end_verse_id INTEGER)")
    execute("CREATE TABLE IF NOT EXISTS reading_progress (day INTEGER PRIMARY KEY, completed INTEGER DEFAULT 0)")

    count = query_one("SELECT COUNT(*) AS c FROM bible_verses")["c"]
    if count == 0:
        print("[INFO] Baixando o texto bíblico (ACF)...")
        import requests
        url = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/pt_acf.json"
        try:
            response = requests.get(url, timeout=30)
            data = response.json()
            
            for book in data:
                for chap_idx, chapter in enumerate(book["chapters"], start=1):
                    for verse_idx, verse_text in enumerate(chapter, start=1):
                        execute(
                            "INSERT INTO bible_verses (book_name, book_abbrev, chapter, verse, text, word_count) VALUES (?, ?, ?, ?, ?, ?)",
                            (book["name"], book["abbrev"], chap_idx, verse_idx, verse_text, len(verse_text.split()))
                        )
            print(f"[OK] {query_one('SELECT COUNT(*) AS c FROM bible_verses')['c']} versículos inseridos.")
        except Exception as e:
            print(f"[ERRO] Falha ao baixar a Bíblia: {e}")
            print("Inicie o app e verifique sua conexão para rodar o patch novamente.")

    count_plan = query_one("SELECT COUNT(*) AS c FROM reading_plan")["c"]
    if count_plan == 0:
        print("[INFO] Gerando o plano de leitura...")
        verses = query_all("SELECT id, word_count FROM bible_verses ORDER BY id")
        if verses:
            total_words = sum(v["word_count"] for v in verses)
            target = total_words / 365
            current_day = 1
            accumulated = 0
            start_id = verses[0]["id"]

            for i, v in enumerate(verses):
                accumulated += v["word_count"]
                if (accumulated >= target and current_day < 365) or i == len(verses) - 1:
                    execute("INSERT INTO reading_plan (day, start_verse_id, end_verse_id) VALUES (?, ?, ?)", (current_day, start_id, v["id"]))
                    current_day += 1
                    accumulated = 0
                    if i < len(verses) - 1: start_id = verses[i + 1]["id"]

            while current_day <= 365:
                execute("INSERT INTO reading_plan (day, start_verse_id, end_verse_id) VALUES (?, ?, ?)", (current_day, start_id, verses[-1]["id"]))
                current_day += 1
            print(f"[OK] Plano gerado com sucesso.")

    count_prog = query_one("SELECT COUNT(*) AS c FROM reading_progress")["c"]
    if count_prog == 0:
        for day in range(1, 366):
            execute("INSERT INTO reading_progress (day, completed) VALUES (?, 0)", (day,))
        print("[OK] Progresso inicializado.")

    # -----------------------------------------------------------------------
    # 6. Reiniciar o servidor
    # -----------------------------------------------------------------------
    print("\nReiniciando o servidor (instalando PyMuPDF)...")
    os.system('taskkill /F /FI "WINDOWTITLE eq Projeto Samurai" >nul 2>&1')
    os.startfile(BASE / "INICIAR.bat")
    print("[OK] Tudo pronto!")

if __name__ == "__main__":
    aplicar_patch()
```


## `gerar_codigo.py`

```python
"""
Gera um arquivo Markdown com o mapa completo do projeto.
Ignora __pycache__, data, .venv, .git, .idea, .vscode, node_modules e binários.
Uso:  py -3 gerar_codigo.py
Saída: PROJETO_SAMURAI.md na raiz.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent
IGNORE_DIRS = {
    "__pycache__", "data", ".venv", "venv", ".git",
    ".idea", ".vscode", "node_modules", ".pytest_cache",
}
IGNORE_EXT = {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg"}
OUTPUT = BASE / "PROJETO_SAMURAI.md"

LANG_MAP = {
    ".py": "python", ".bat": "bat", ".txt": "text",
    ".md": "markdown", ".json": "json", ".toml": "toml",
    ".css": "css", ".html": "html", ".js": "javascript",
}


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in IGNORE_EXT:
        return True
    return False


def generate() -> None:
    linhas: list[str] = ["# ⚔️ Projeto Samurai — Mapa do Código\n"]
    linhas.append("> Gerado automaticamente por `gerar_codigo.py`\n")
    linhas.append(f"> Raiz: `{BASE.name}`\n\n---\n")

    arquivos = sorted(
        p for p in BASE.rglob("*")
        if p.is_file() and not is_ignored(p.relative_to(BASE))
    )

    for path in arquivos:
        rel = path.relative_to(BASE)
        lang = LANG_MAP.get(path.suffix.lower(), "text")
        linhas.append(f"\n## `{rel.as_posix()}`\n")
        try:
            conteudo = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            conteudo = "<<arquivo binário ou ilegível>>"
        linhas.append(f"```{lang}")
        linhas.append(conteudo)
        linhas.append("```\n")

    OUTPUT.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[OK] Mapa gerado: {OUTPUT}")
    print(f"[OK] {len(arquivos)} arquivo(s) incluído(s).")


if __name__ == "__main__":
    generate()

```


## `INICIAR.bat`

```bat
@echo off
title Projeto Samurai
cd /d "%~dp0"

echo ==================================================
echo    PROJETO SAMURAI - Iniciando ambiente
echo ==================================================
echo.

echo [1/3] Verificando dependencias...
py -3 -m pip install --quiet --upgrade pip
py -3 -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

echo [2/3] Iniciando Streamlit na porta 8501...
echo [3/3] O navegador abrira automaticamente.
echo.
echo (Para encerrar o servidor, feche esta janela ou pressione Ctrl+C)
echo.

py -3 -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo Servidor encerrado.
pause

```


## `PROJETO_SAMURAI.md`

```markdown
# ⚔️ Projeto Samurai — Mapa do Código

> Gerado automaticamente por `gerar_codigo.py`

> Raiz: `Projeto Samurai`

---


## `.streamlit/config.toml`

```toml
[theme]
base="dark"
primaryColor="#8B0000"
backgroundColor="#0B0B0B"
secondaryBackgroundColor="#171717"
textColor="#F2F2F2"
font="sans serif"

```


## `app.py`

```python
"""
Projeto Samurai — Sistema Operacional Pessoal.
Entry point Streamlit. Configura tema, navegação e injeta CSS.
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from core.schema import init_db

init_db()

st.set_page_config(
    page_title="Projeto Samurai ⚔️",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

SAMURAI_CSS = """
<style>
:root {
    --s-red:        #8B0000;
    --s-dark-red:   #5C0000;
    --s-black:      #0B0B0B;
    --s-gray:       #171717;
    --s-gray-soft:  #1F1F1F;
    --s-white:      #FFFFFF;
    --s-white-soft: #CCCCCC;
}

/* Força o fundo escuro no app */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--s-black) !important;
}

/* Força cor do texto em TODOS os elementos comuns e containers do Streamlit */
h1, h2, h3, h4, h5, h6, p, span, li, label, 
div[data-testid="stMarkdownContainer"] *, 
[data-testid="stWidgetLabel"] * {
    color: var(--s-white) !important;
}

/* Linha vermelha embaixo do H1 */
h1 {
    border-bottom: 2px solid var(--s-red) !important;
    padding-bottom: 8px !important;
    letter-spacing: .5px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--s-gray) !important;
    border-right: 1px solid var(--s-red) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--s-white) !important;
}

/* Cards Customizados */
.samurai-card {
    background-color: var(--s-gray-soft) !important;
    border-left: 4px solid var(--s-red) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
}
.samurai-card .titulo {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--s-white-soft) !important;
    margin-bottom: 6px !important;
    font-weight: 600 !important;
}
.samurai-card .valor {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--s-white) !important;
}
.samurai-card .detalhe {
    font-size: 0.85rem !important;
    color: var(--s-white-soft) !important;
    margin-top: 6px !important;
}

/* Botões */
.stButton > button, .stFormSubmitButton > button {
    background-color: var(--s-red) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-dark-red) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--s-dark-red) !important;
    border-color: var(--s-white) !important;
}

/* Barras de Progresso */
.stProgress > div > div > div > div {
    background-color: var(--s-red) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--s-gray) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-red) !important;
}

/* Divisores e Caixas de Info/Alerta */
hr { border-color: var(--s-red) !important; opacity: .5 !important; }
.stAlert { 
    background-color: var(--s-gray-soft) !important; 
    color: var(--s-white) !important; 
    border: 1px solid var(--s-red) !important; 
}
.stAlert * { color: var(--s-white) !important; }
</style>
"""

st.markdown(SAMURAI_CSS, unsafe_allow_html=True)


home = st.Page("ui/pages/00_Home.py", title="🏯 Dojo", default=True)
consistencia = st.Page("ui/pages/07_Consistencia.py", title="🎯 Consistência")
corpo = st.Page("ui/pages/01_Corpo.py", title="💪 Corpo")
mente = st.Page("ui/pages/02_Mente.py", title="🧠 Mente")
informacao = st.Page("ui/pages/03_Informacao.py", title="📰 Informação")
patrimonio = st.Page("ui/pages/04_Patrimonio.py", title="💎 Patrimônio")
descanso = st.Page("ui/pages/05_Descanso.py", title="🌿 Descanso & Lazer")
autoconhecimento = st.Page("ui/pages/06_Autoconhecimento.py", title="🪞 Autoconhecimento")
religiao = st.Page("ui/pages/08_Religiao.py", title="🕊️ Religião")

pg = st.navigation(
    {
        "⚔️ Comando": [home, consistencia],
        "🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento, religiao],
    }
)


# --- Configuração da IA na Sidebar ---
from services.ai import get_api_key

with st.sidebar:
    st.divider()
    st.markdown("### ⚙️ IA Configuração")
    key_atual = get_api_key()
    
    if key_atual and key_atual != "COLE_SUA_CHAVE_AQUI":
        st.success("IA Conectada 🟢")
    else:
        st.warning("IA Desconectada 🔴")
        nova_chave = st.text_input("Cole sua API Key do Gemini:", type="password", placeholder="AIzaSy...")
        if st.button("Salvar e Ativar IA", use_container_width=True):
            if nova_chave.strip():
                config_file = BASE_DIR / "config.json"
                config_file.write_text(json.dumps({"gemini_api_key": nova_chave.strip()}, indent=4), encoding="utf-8")
                st.success("Chave salva com sucesso!")
                import time
                time.sleep(1)
                st.rerun()

pg.run()


```


## `assets/.gitkeep`

```text

```


## `config.json`

```json
{
    "gemini_api_key": "AQ.Ab8RN6I_Bq6xAq5tGVYh87pnioxbyxprdwD0UqKdSw8gzkE5zw"
}

```


## `core/__init__.py`

```python
"""Núcleo do Projeto Samurai (banco, schema, utilitários)."""

```


## `core/database.py`

```python
"""
Conexão SQLite centralizada.
- WAL mode para leituras concorrentes.
- Lock em memória para evitar writes simultâneos (Streamlit é multithread).
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "samurai.db"

_lock = threading.RLock()


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão configurada. O caller é responsável por fechar."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def execute(sql: str, params: tuple = ()) -> int:
    """Executa um INSERT/UPDATE/DELETE. Retorna lastrowid."""
    with _lock:
        with get_connection() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid


def executemany(sql: str, seq_params: list[tuple]) -> None:
    with _lock:
        with get_connection() as conn:
            conn.executemany(sql, seq_params)
            conn.commit()


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchall()


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchone()

```


## `core/schema.py`

```python
"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
    ("Oração", "Religião", "Momento de conexão com Deus."),
    ("Leitura Bíblica", "Religião", "Ler um trecho da Palavra."),
    ("Gratidão a Deus", "Religião", "Agradecer pelas bênçãos do dia."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    # Seed inteligente: insere apenas se o hábito ainda não existir
    for name, pillar, desc in SEED_HABITS:
        if not query_one("SELECT id FROM habits WHERE name = ?", (name,)):
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )

```


## `criar_projeto_samurai.py`

```python
import ast
import os
import sys
from pathlib import Path

BASE = Path(r"C:\Users\Ricardo Fernandes\Desktop\Projeto Samurai")

def aplicar_patch():
    print("=" * 60)
    print("⚔️  PATCH: ATUALIZAÇÃO DO MODELO GEMINI PARA 3.5 FLASH-LITE")
    print("=" * 60)

    if not BASE.exists():
        print(f"[ERRO] Pasta do projeto não encontrada: {BASE}")
        sys.exit(1)

    ai_file = BASE / "services" / "ai.py"
    ai_txt = ai_file.read_text(encoding="utf-8")

    # Substitui a linha do modelo antigo pelo novo
    linha_antiga = "model = genai.GenerativeModel('gemini-1.5-flash')"
    nova_linha = "model = genai.GenerativeModel('gemini-3.5-flash-lite')  # MODELO FIXADO - NÃO ALTERAR"

    if linha_antiga in ai_txt:
        ai_txt = ai_txt.replace(linha_antiga, nova_linha)
        print("[OK] Modelo atualizado para 'gemini-3.5-flash-lite'.")
    elif "gemini-3.5-flash-lite" in ai_txt:
        print("[SKIP] O modelo já está configurado como 'gemini-3.5-flash-lite'.")
    else:
        print("[AVISO] Linha do modelo não encontrada. Verifique manualmente o arquivo services/ai.py.")

    try:
        ast.parse(ai_txt)
        ai_file.write_text(ai_txt, encoding="utf-8")
        print("[OK] Arquivo services/ai.py validado e salvo.")
    except SyntaxError as e:
        print(f"[ERRO] Falha na validação de sintaxe: {e}")
        sys.exit(1)

    print("\nReiniciando o servidor...")
    os.system('taskkill /F /FI "WINDOWTITLE eq Projeto Samurai" >nul 2>&1')
    os.startfile(BASE / "INICIAR.bat")
    print("[OK] Servidor reiniciado. O Mentor Samurai agora usa o Gemini 3.5 Flash-Lite!")

if __name__ == "__main__":
    aplicar_patch()
```


## `gerar_codigo.py`

```python
"""
Gera um arquivo Markdown com o mapa completo do projeto.
Ignora __pycache__, data, .venv, .git, .idea, .vscode, node_modules e binários.
Uso:  py -3 gerar_codigo.py
Saída: PROJETO_SAMURAI.md na raiz.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent
IGNORE_DIRS = {
    "__pycache__", "data", ".venv", "venv", ".git",
    ".idea", ".vscode", "node_modules", ".pytest_cache",
}
IGNORE_EXT = {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg"}
OUTPUT = BASE / "PROJETO_SAMURAI.md"

LANG_MAP = {
    ".py": "python", ".bat": "bat", ".txt": "text",
    ".md": "markdown", ".json": "json", ".toml": "toml",
    ".css": "css", ".html": "html", ".js": "javascript",
}


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in IGNORE_EXT:
        return True
    return False


def generate() -> None:
    linhas: list[str] = ["# ⚔️ Projeto Samurai — Mapa do Código\n"]
    linhas.append("> Gerado automaticamente por `gerar_codigo.py`\n")
    linhas.append(f"> Raiz: `{BASE.name}`\n\n---\n")

    arquivos = sorted(
        p for p in BASE.rglob("*")
        if p.is_file() and not is_ignored(p.relative_to(BASE))
    )

    for path in arquivos:
        rel = path.relative_to(BASE)
        lang = LANG_MAP.get(path.suffix.lower(), "text")
        linhas.append(f"\n## `{rel.as_posix()}`\n")
        try:
            conteudo = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            conteudo = "<<arquivo binário ou ilegível>>"
        linhas.append(f"```{lang}")
        linhas.append(conteudo)
        linhas.append("```\n")

    OUTPUT.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[OK] Mapa gerado: {OUTPUT}")
    print(f"[OK] {len(arquivos)} arquivo(s) incluído(s).")


if __name__ == "__main__":
    generate()

```


## `INICIAR.bat`

```bat
@echo off
title Projeto Samurai
cd /d "%~dp0"

echo ==================================================
echo    PROJETO SAMURAI - Iniciando ambiente
echo ==================================================
echo.

echo [1/3] Verificando dependencias...
py -3 -m pip install --quiet --upgrade pip
py -3 -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

echo [2/3] Iniciando Streamlit na porta 8501...
echo [3/3] O navegador abrira automaticamente.
echo.
echo (Para encerrar o servidor, feche esta janela ou pressione Ctrl+C)
echo.

py -3 -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo Servidor encerrado.
pause

```


## `PROJETO_SAMURAI.md`

```markdown
# ⚔️ Projeto Samurai — Mapa do Código

> Gerado automaticamente por `gerar_codigo.py`

> Raiz: `Projeto Samurai`

---


## `.streamlit/config.toml`

```toml
[theme]
base="dark"
primaryColor="#8B0000"
backgroundColor="#0B0B0B"
secondaryBackgroundColor="#171717"
textColor="#F2F2F2"
font="sans serif"

```


## `app.py`

```python
"""
Projeto Samurai — Sistema Operacional Pessoal.
Entry point Streamlit. Configura tema, navegação e injeta CSS.
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from core.schema import init_db

init_db()

st.set_page_config(
    page_title="Projeto Samurai ⚔️",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

SAMURAI_CSS = """
<style>
:root {
    --s-red:        #8B0000;
    --s-dark-red:   #5C0000;
    --s-black:      #0B0B0B;
    --s-gray:       #171717;
    --s-gray-soft:  #1F1F1F;
    --s-white:      #FFFFFF;
    --s-white-soft: #CCCCCC;
}

/* Força o fundo escuro no app */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--s-black) !important;
}

/* Força cor do texto em TODOS os elementos comuns e containers do Streamlit */
h1, h2, h3, h4, h5, h6, p, span, li, label, 
div[data-testid="stMarkdownContainer"] *, 
[data-testid="stWidgetLabel"] * {
    color: var(--s-white) !important;
}

/* Linha vermelha embaixo do H1 */
h1 {
    border-bottom: 2px solid var(--s-red) !important;
    padding-bottom: 8px !important;
    letter-spacing: .5px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--s-gray) !important;
    border-right: 1px solid var(--s-red) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--s-white) !important;
}

/* Cards Customizados */
.samurai-card {
    background-color: var(--s-gray-soft) !important;
    border-left: 4px solid var(--s-red) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
}
.samurai-card .titulo {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--s-white-soft) !important;
    margin-bottom: 6px !important;
    font-weight: 600 !important;
}
.samurai-card .valor {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--s-white) !important;
}
.samurai-card .detalhe {
    font-size: 0.85rem !important;
    color: var(--s-white-soft) !important;
    margin-top: 6px !important;
}

/* Botões */
.stButton > button, .stFormSubmitButton > button {
    background-color: var(--s-red) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-dark-red) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--s-dark-red) !important;
    border-color: var(--s-white) !important;
}

/* Barras de Progresso */
.stProgress > div > div > div > div {
    background-color: var(--s-red) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--s-gray) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-red) !important;
}

/* Divisores e Caixas de Info/Alerta */
hr { border-color: var(--s-red) !important; opacity: .5 !important; }
.stAlert { 
    background-color: var(--s-gray-soft) !important; 
    color: var(--s-white) !important; 
    border: 1px solid var(--s-red) !important; 
}
.stAlert * { color: var(--s-white) !important; }
</style>
"""

st.markdown(SAMURAI_CSS, unsafe_allow_html=True)


home = st.Page("ui/pages/00_Home.py", title="🏯 Dojo", default=True)
consistencia = st.Page("ui/pages/07_Consistencia.py", title="🎯 Consistência")
corpo = st.Page("ui/pages/01_Corpo.py", title="💪 Corpo")
mente = st.Page("ui/pages/02_Mente.py", title="🧠 Mente")
informacao = st.Page("ui/pages/03_Informacao.py", title="📰 Informação")
patrimonio = st.Page("ui/pages/04_Patrimonio.py", title="💎 Patrimônio")
descanso = st.Page("ui/pages/05_Descanso.py", title="🌿 Descanso & Lazer")
autoconhecimento = st.Page("ui/pages/06_Autoconhecimento.py", title="🪞 Autoconhecimento")

pg = st.navigation(
    {
        "⚔️ Comando": [home, consistencia],
        "🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento],
    }
)

pg.run()

```


## `assets/.gitkeep`

```text

```


## `config.json`

```json
{
    "gemini_api_key": "COLE_SUA_CHAVE_AQUI"
}

```


## `core/__init__.py`

```python
"""Núcleo do Projeto Samurai (banco, schema, utilitários)."""

```


## `core/database.py`

```python
"""
Conexão SQLite centralizada.
- WAL mode para leituras concorrentes.
- Lock em memória para evitar writes simultâneos (Streamlit é multithread).
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "samurai.db"

_lock = threading.RLock()


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão configurada. O caller é responsável por fechar."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def execute(sql: str, params: tuple = ()) -> int:
    """Executa um INSERT/UPDATE/DELETE. Retorna lastrowid."""
    with _lock:
        with get_connection() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid


def executemany(sql: str, seq_params: list[tuple]) -> None:
    with _lock:
        with get_connection() as conn:
            conn.executemany(sql, seq_params)
            conn.commit()


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchall()


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchone()

```


## `core/schema.py`

```python
"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    if query_one("SELECT COUNT(*) AS c FROM habits")["c"] == 0:
        for name, pillar, desc in SEED_HABITS:
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )

```


## `criar_projeto_samurai.py`

```python
import ast
import os
import sys
from pathlib import Path

BASE = Path(r"C:\Users\Ricardo Fernandes\Desktop\Projeto Samurai")

def aplicar_patch():
    print("=" * 60)
    print("⚔️  PATCH SPRINT 4: INTEGRAÇÃO COM GOOGLE GEMINI (IA)")
    print("=" * 60)

    if not BASE.exists():
        print(f"[ERRO] Pasta do projeto não encontrada: {BASE}")
        sys.exit(1)

    arquivos = {}

    # -----------------------------------------------------------------------
    # 1. Atualizar requirements.txt
    # -----------------------------------------------------------------------
    req_file = BASE / "requirements.txt"
    req_txt = req_file.read_text(encoding="utf-8")
    if "google-generativeai" not in req_txt:
        req_txt += "google-generativeai>=0.5.0\n"
        req_file.write_text(req_txt, encoding="utf-8")
        print("[OK] Corrigido: requirements.txt")
    else:
        print("[SKIP] requirements.txt já está atualizado.")

    # -----------------------------------------------------------------------
    # 2. Criar config.json (Template da API Key)
    # -----------------------------------------------------------------------
    config_file = BASE / "config.json"
    if not config_file.exists():
        config_file.write_text('{\n    "gemini_api_key": "COLE_SUA_CHAVE_AQUI"\n}\n', encoding="utf-8")
        print("[OK] Criado: config.json (Insira sua API Key aqui)")
    else:
        print("[SKIP] config.json já existe.")

    # -----------------------------------------------------------------------
    # 3. Criar services/ai.py
    # -----------------------------------------------------------------------
    arquivos["services/ai.py"] = '''import google.generativeai as genai
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

def get_api_key() -> str:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("gemini_api_key", "")
        except Exception:
            pass
    return ""

def ask_gemini(prompt: str) -> str:
    api_key = get_api_key()
    if not api_key or api_key == "COLE_SUA_CHAVE_AQUI":
        return "⚠️ API Key não configurada. Abra o arquivo 'config.json' na raiz do projeto e insira sua chave do Gemini."
    
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Erro na IA: {str(e)}"
'''

    # -----------------------------------------------------------------------
    # 4. Atualizar 02_Mente.py
    # -----------------------------------------------------------------------
    arquivos["ui/pages/02_Mente.py"] = '''import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

livro = query_one("SELECT * FROM book_progress ORDER BY last_update DESC LIMIT 1")

col1, col2 = st.columns([2, 1])
with col1:
    if livro:
        st.markdown(f"**Livro atual:** {livro['book_title']}")
        pct = 0
        if livro['total_pages'] > 0:
            pct = min(1.0, livro['current_page'] / livro['total_pages'])
        st.progress(pct)
        st.caption(f"Página {livro['current_page']} de {livro['total_pages']} ({pct*100:.1f}%)")
    else:
        st.info("📖 Nenhum livro em andamento. Adicione um abaixo.")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Novo Livro", use_container_width=True):
        st.session_state["novo_livro"] = True

if not livro or st.session_state.get("novo_livro", False):
    with st.form("form_livro"):
        st.subheader("Adicionar Livro")
        titulo = st.text_input("Título do Livro")
        total_pag = st.number_input("Total de Páginas", min_value=1, value=100)
        
        if st.form_submit_button("Salvar Livro"):
            if titulo:
                execute(
                    """
                    INSERT INTO book_progress (book_title, total_pages) 
                    VALUES (?, ?)
                    ON CONFLICT(book_title) DO UPDATE SET total_pages = excluded.total_pages
                    """, (titulo, total_pag)
                )
                st.session_state["novo_livro"] = False
                st.rerun()
            else:
                st.error("O título é obrigatório.")

st.divider()
st.subheader("📖 Texto Exato do Dia")

if livro:
    if st.button("🪄 Gerar Leitura do Dia com IA", use_container_width=True):
        with st.spinner("O Mentor está lendo o livro e preparando sua lição..."):
            prompt_ia = f"Atue como um mentor samurai sábio. O usuário está lendo o livro '{livro['book_title']}'. Gere um texto curto e inspirador (cerca de 100 palavras) ou um resumo de um dos principais conceitos desse livro, como se fosse a leitura diária para forjar a mente."
            resumo_ia = ask_gemini(prompt_ia)
            st.session_state["resumo_ia"] = resumo_ia
    
    if "resumo_ia" in st.session_state:
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 15px;">
            <div class="titulo">Leitura Recomendada</div>
            <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{st.session_state['resumo_ia']}</div>
        </div>""", unsafe_allow_html=True)
else:
    st.info("Adicione um livro para gerar o texto do dia.")

with st.expander("✍️ Anotações da Leitura"):
    st.text_area("Seu resumo ou insights de hoje:", placeholder="Digite aqui o que você absorveu do capítulo...")

if livro:
    st.divider()
    with st.form("form_progresso"):
        st.subheader("Atualizar Progresso")
        nova_pag = st.number_input("Página atual", min_value=0, max_value=int(livro['total_pages']), value=int(livro['current_page']))
        
        if st.form_submit_button("Atualizar Página", use_container_width=True):
            execute(
                "UPDATE book_progress SET current_page = ?, last_update = datetime('now') WHERE id = ?",
                (nova_pag, livro['id'])
            )
            st.rerun()
'''

    # -----------------------------------------------------------------------
    # 5. Atualizar 06_Autoconhecimento.py
    # -----------------------------------------------------------------------
    arquivos["ui/pages/06_Autoconhecimento.py"] = '''import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()

st.title("🪞 Autoconhecimento")
st.caption("Diário reflexivo e meditação.")

PROMPTS = [
    "O que drenou minha energia hoje e por quê?",
    "Qual pequena vitória eu tive hoje?",
    "O que eu faria diferente se pudesse recomeçar o dia?",
    "Pelo que sou grato neste exato momento?",
    "Qual pensamento negativo eu posso deixar ir embora?",
    "Como eu tratei as pessoas ao meu redor hoje?",
    "O que aprendi sobre mim mesmo nesta semana?",
]

prompt_do_dia = PROMPTS[date.today().toordinal() % len(PROMPTS)]

st.subheader("📝 Diário Reflexivo")
st.markdown(f"**Prompt de hoje:** *{prompt_do_dia}*")

with st.form("form_journal"):
    texto = st.text_area("Sua reflexão:", height=150, placeholder="Escreva livremente...")
    submitted = st.form_submit_button("Salvar e Refletir com IA", use_container_width=True)

if submitted and texto.strip():
    with st.spinner("O Mentor Samurai está refletindo sobre suas palavras..."):
        prompt_ia = f"Atue como um mentor samurai sábio e empático. O usuário escreveu a seguinte reflexão sobre o prompt '{prompt_do_dia}':\n\n'{texto.strip()}'\n\nForneça uma resposta curta (máximo 2 parágrafos) validando os sentimentos dele e oferecendo uma perspectiva focada em disciplina, evolução e paz interior. Fale de forma direta e acolhedora."
        reflexao_ia = ask_gemini(prompt_ia)
        
        execute(
            "INSERT INTO journal_entries (entry_date, prompt, content, ai_reflection) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), prompt_do_dia, texto.strip(), reflexao_ia)
        )
    st.success("Reflexão salva e analisada.")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Meditação Curta")
st.markdown("""
**Respiração Box (5 minutos):**
1. Inspire contando até **4**.
2. Segure a respiração contando até **4**.
3. Expire lentamente contando até **4**.
4. Aguarde contando até **4**.
5. Repita por 5 minutos.
""")

st.divider()
st.subheader("📚 Histórico de Reflexões")

entries = query_all("SELECT * FROM journal_entries ORDER BY entry_date DESC, id DESC LIMIT 5")
if not entries:
    st.info("Nenhuma reflexão registrada ainda.")
else:
    for e in entries:
        with st.expander(f"📅 {e['entry_date']} — {e['prompt']}"):
            st.markdown(f"**Sua reflexão:**\n{e['content']}")
            if e['ai_reflection']:
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 10px; padding: 10px;">
                    <div style="color: #F2F2F2; font-size: 0.9rem; font-style: italic;">
                        <b>Mentor Samurai:</b><br>{e['ai_reflection']}
                    </div>
                </div>""", unsafe_allow_html=True)
'''

    # -----------------------------------------------------------------------
    # 6. Atualizar 07_Consistencia.py
    # -----------------------------------------------------------------------
    arquivos["ui/pages/07_Consistencia.py"] = '''"""Consistência — check-in diário, marcação de hábitos e score anti-burnout."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date, timedelta

import streamlit as st

from core.database import execute, query_all, query_one
from services.ai import ask_gemini

today = date.today()
today_iso = today.isoformat()

def calcular_burnout() -> tuple[float, dict]:
    week_ago = (today - timedelta(days=7)).isoformat()

    checkins = query_all("SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?", (week_ago,))
    total_habits = query_one("SELECT COUNT(*) AS c FROM habits WHERE active = 1")["c"] or 0
    logs = query_all("SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,))
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    total = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return total, {
        "avg_energy": avg_energy,
        "avg_stress": avg_stress,
        "avg_sleep": avg_sleep,
        "taxa": taxa,
    }

def classificar_burnout(score: float) -> tuple[str, str]:
    if score < 30:
        return "🟢 Baixo", "#2E7D32"
    if score < 60:
        return "🟡 Médio", "#F9A825"
    if score < 80:
        return "🟠 Alto", "#EF6C00"
    return "🔴 Crítico", "#C62828"

st.title("🎯 Consistência")
st.caption("Disciplina diária é o que forja o samurai.")

st.subheader("📝 Check-in do dia")
existente = query_one("SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,))
MOOD_OPTIONS = ["Ótimo", "Bom", "Neutro", "Cansado", "Estressado", "Ansioso"]
mood_default = (MOOD_OPTIONS.index(existente["mood"]) if existente and existente["mood"] in MOOD_OPTIONS else 2)

with st.form("form_checkin", clear_on_submit=False):
    energy = st.slider("Energia (1–10)", 1, 10, int(existente["energy"]) if existente else 6)
    sleep_hours = st.number_input("Horas de sono", min_value=0.0, max_value=16.0, step=0.5, value=float(existente["sleep_hours"]) if existente else 7.0)
    mood = st.selectbox("Humor", MOOD_OPTIONS, index=mood_default)
    stress = st.slider("Estresse (1–10)", 1, 10, int(existente["stress"]) if existente else 5)
    notes = st.text_area("Notas (opcional)", value=existente["notes"] if existente and existente["notes"] else "")
    submit = st.form_submit_button("💾 Salvar check-in", use_container_width=True)

if submit:
    execute(
        """
        INSERT INTO daily_checkins (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy = excluded.energy, sleep_hours = excluded.sleep_hours, mood = excluded.mood, stress = excluded.stress, notes = excluded.notes
        """,
        (today_iso, energy, sleep_hours, mood, stress, notes or None),
    )
    st.success("[OK] Check-in registrado.")
    st.rerun()

st.divider()
st.subheader("🥋 Hábitos de hoje")
habits = query_all(
    """
    SELECT h.id, h.name, h.pillar, COALESCE(l.done, 0) AS done
    FROM habits h LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1 ORDER BY h.pillar, h.name
    """, (today_iso,),
)
alterou = False
for h in habits:
    novo = st.checkbox(f"**{h['pillar']}** · {h['name']}", value=bool(h["done"]), key=f"habit_{h['id']}")
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """, (h["id"], today_iso, 1 if novo else 0),
        )
        alterou = True
if alterou: st.rerun()

st.divider()
st.subheader("🔥 Score Anti-Burnout (7 dias)")
score, metricas = calcular_burnout()
label, cor = classificar_burnout(score)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color:{cor};">
        <div class="titulo">Risco atual</div>
        <div class="valor" style="color:{cor};">{score:.0f}/100 — {label}</div>
        <div class="detalhe">
            Média energia: {metricas['avg_energy']:.1f} · Sono: {metricas['avg_sleep']:.1f}h · Estresse: {metricas['avg_stress']:.1f} · Hábitos: {metricas['taxa']*100:.0f}%
        </div>
    </div>""", unsafe_allow_html=True,
)
st.progress(min(1.0, score / 100.0))

if score >= 80:
    st.error("⚠️ Risco crítico. Priorize descanso hoje. Nenhum treino vale um colapso.")
elif score >= 60:
    st.warning("Atenção: sinais de sobrecarga. Reduza intensidade e priorize sono.")

st.divider()
st.subheader("🧠 Relatório do Mentor Samurai")
if st.button("📜 Gerar Análise Semanal com IA", use_container_width=True):
    with st.spinner("O Mentor está analisando seus dados da semana..."):
        prompt_ia = f"Atue como um mentor samurai sábio e direto. Aqui estão os dados da semana do usuário:\\n- Score de Burnout: {score:.0f}/100\\n- Média de Energia: {metricas['avg_energy']:.1f}\\n- Média de Sono: {metricas['avg_sleep']:.1f}h\\n- Média de Estresse: {metricas['avg_stress']:.1f}\\n- Taxa de conclusão de hábitos: {metricas['taxa']*100:.0f}%\\n\\nEscreva um relatório semanal curto (max 3 parágrafos), motivador e realista. Se o burnout estiver alto (>60), aconselhe descanso. Se estiver baixo, parabenize e incentive a manter a disciplina. Mantenha o tom sério, mas encorajador."
        relatorio_ia = ask_gemini(prompt_ia)
        
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 15px;">
            <div class="titulo">Visão do Mestre</div>
            <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{relatorio_ia}</div>
        </div>""", unsafe_allow_html=True)
'''

    # -----------------------------------------------------------------------
    # Execução da gravação
    # -----------------------------------------------------------------------
    for rel_path, conteudo in arquivos.items():
        file_path = BASE / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            ast.parse(conteudo)
        except SyntaxError as e:
            print(f"[ERRO] Falha na validação de sintaxe de {rel_path}: {e}")
            sys.exit(1)

        if file_path.exists() and file_path.read_text(encoding="utf-8") == conteudo:
            print(f"[SKIP] {rel_path} já está atualizado.")
            continue
        
        file_path.write_text(conteudo, encoding="utf-8")
        print(f"[OK] Corrigido: {rel_path}")

    # -----------------------------------------------------------------------
    # Reiniciar o servidor
    # -----------------------------------------------------------------------
    print("\nReiniciando o servidor (isso pode demorar um pouco para instalar a nova biblioteca)...")
    os.system('taskkill /F /FI "WINDOWTITLE eq Projeto Samurai" >nul 2>&1')
    os.startfile(BASE / "INICIAR.bat")
    print("[OK] Servidor reiniciado. Sprint 4 no ar!")

if __name__ == "__main__":
    aplicar_patch()
```


## `gerar_codigo.py`

```python
"""
Gera um arquivo Markdown com o mapa completo do projeto.
Ignora __pycache__, data, .venv, .git, .idea, .vscode, node_modules e binários.
Uso:  py -3 gerar_codigo.py
Saída: PROJETO_SAMURAI.md na raiz.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent
IGNORE_DIRS = {
    "__pycache__", "data", ".venv", "venv", ".git",
    ".idea", ".vscode", "node_modules", ".pytest_cache",
}
IGNORE_EXT = {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg"}
OUTPUT = BASE / "PROJETO_SAMURAI.md"

LANG_MAP = {
    ".py": "python", ".bat": "bat", ".txt": "text",
    ".md": "markdown", ".json": "json", ".toml": "toml",
    ".css": "css", ".html": "html", ".js": "javascript",
}


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in IGNORE_EXT:
        return True
    return False


def generate() -> None:
    linhas: list[str] = ["# ⚔️ Projeto Samurai — Mapa do Código\n"]
    linhas.append("> Gerado automaticamente por `gerar_codigo.py`\n")
    linhas.append(f"> Raiz: `{BASE.name}`\n\n---\n")

    arquivos = sorted(
        p for p in BASE.rglob("*")
        if p.is_file() and not is_ignored(p.relative_to(BASE))
    )

    for path in arquivos:
        rel = path.relative_to(BASE)
        lang = LANG_MAP.get(path.suffix.lower(), "text")
        linhas.append(f"\n## `{rel.as_posix()}`\n")
        try:
            conteudo = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            conteudo = "<<arquivo binário ou ilegível>>"
        linhas.append(f"```{lang}")
        linhas.append(conteudo)
        linhas.append("```\n")

    OUTPUT.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[OK] Mapa gerado: {OUTPUT}")
    print(f"[OK] {len(arquivos)} arquivo(s) incluído(s).")


if __name__ == "__main__":
    generate()

```


## `INICIAR.bat`

```bat
@echo off
title Projeto Samurai
cd /d "%~dp0"

echo ==================================================
echo    PROJETO SAMURAI - Iniciando ambiente
echo ==================================================
echo.

echo [1/3] Verificando dependencias...
py -3 -m pip install --quiet --upgrade pip
py -3 -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

echo [2/3] Iniciando Streamlit na porta 8501...
echo [3/3] O navegador abrira automaticamente.
echo.
echo (Para encerrar o servidor, feche esta janela ou pressione Ctrl+C)
echo.

py -3 -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo Servidor encerrado.
pause

```


## `PROJETO_SAMURAI.md`

```markdown
# ⚔️ Projeto Samurai — Mapa do Código

> Gerado automaticamente por `gerar_codigo.py`

> Raiz: `Projeto Samurai`

---


## `.streamlit/config.toml`

```toml
[theme]
base="dark"
primaryColor="#8B0000"
backgroundColor="#0B0B0B"
secondaryBackgroundColor="#171717"
textColor="#F2F2F2"
font="sans serif"

```


## `app.py`

```python
"""
Projeto Samurai — Sistema Operacional Pessoal.
Entry point Streamlit. Configura tema, navegação e injeta CSS.
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from core.schema import init_db

init_db()

st.set_page_config(
    page_title="Projeto Samurai ⚔️",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

SAMURAI_CSS = """
<style>
:root {
    --s-red:        #8B0000;
    --s-dark-red:   #5C0000;
    --s-black:      #0B0B0B;
    --s-gray:       #171717;
    --s-gray-soft:  #1F1F1F;
    --s-white:      #FFFFFF;
    --s-white-soft: #CCCCCC;
}

/* Força o fundo escuro no app */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--s-black) !important;
}

/* Força cor do texto em TODOS os elementos comuns e containers do Streamlit */
h1, h2, h3, h4, h5, h6, p, span, li, label, 
div[data-testid="stMarkdownContainer"] *, 
[data-testid="stWidgetLabel"] * {
    color: var(--s-white) !important;
}

/* Linha vermelha embaixo do H1 */
h1 {
    border-bottom: 2px solid var(--s-red) !important;
    padding-bottom: 8px !important;
    letter-spacing: .5px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--s-gray) !important;
    border-right: 1px solid var(--s-red) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--s-white) !important;
}

/* Cards Customizados */
.samurai-card {
    background-color: var(--s-gray-soft) !important;
    border-left: 4px solid var(--s-red) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
}
.samurai-card .titulo {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--s-white-soft) !important;
    margin-bottom: 6px !important;
    font-weight: 600 !important;
}
.samurai-card .valor {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--s-white) !important;
}
.samurai-card .detalhe {
    font-size: 0.85rem !important;
    color: var(--s-white-soft) !important;
    margin-top: 6px !important;
}

/* Botões */
.stButton > button, .stFormSubmitButton > button {
    background-color: var(--s-red) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-dark-red) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--s-dark-red) !important;
    border-color: var(--s-white) !important;
}

/* Barras de Progresso */
.stProgress > div > div > div > div {
    background-color: var(--s-red) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--s-gray) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-red) !important;
}

/* Divisores e Caixas de Info/Alerta */
hr { border-color: var(--s-red) !important; opacity: .5 !important; }
.stAlert { 
    background-color: var(--s-gray-soft) !important; 
    color: var(--s-white) !important; 
    border: 1px solid var(--s-red) !important; 
}
.stAlert * { color: var(--s-white) !important; }
</style>
"""

st.markdown(SAMURAI_CSS, unsafe_allow_html=True)


home = st.Page("ui/pages/00_Home.py", title="🏯 Dojo", default=True)
consistencia = st.Page("ui/pages/07_Consistencia.py", title="🎯 Consistência")
corpo = st.Page("ui/pages/01_Corpo.py", title="💪 Corpo")
mente = st.Page("ui/pages/02_Mente.py", title="🧠 Mente")
informacao = st.Page("ui/pages/03_Informacao.py", title="📰 Informação")
patrimonio = st.Page("ui/pages/04_Patrimonio.py", title="💎 Patrimônio")
descanso = st.Page("ui/pages/05_Descanso.py", title="🌿 Descanso & Lazer")
autoconhecimento = st.Page("ui/pages/06_Autoconhecimento.py", title="🪞 Autoconhecimento")

pg = st.navigation(
    {
        "⚔️ Comando": [home, consistencia],
        "🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento],
    }
)

pg.run()

```


## `assets/.gitkeep`

```text

```


## `core/__init__.py`

```python
"""Núcleo do Projeto Samurai (banco, schema, utilitários)."""

```


## `core/database.py`

```python
"""
Conexão SQLite centralizada.
- WAL mode para leituras concorrentes.
- Lock em memória para evitar writes simultâneos (Streamlit é multithread).
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "samurai.db"

_lock = threading.RLock()


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão configurada. O caller é responsável por fechar."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def execute(sql: str, params: tuple = ()) -> int:
    """Executa um INSERT/UPDATE/DELETE. Retorna lastrowid."""
    with _lock:
        with get_connection() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid


def executemany(sql: str, seq_params: list[tuple]) -> None:
    with _lock:
        with get_connection() as conn:
            conn.executemany(sql, seq_params)
            conn.commit()


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchall()


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchone()

```


## `core/schema.py`

```python
"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    if query_one("SELECT COUNT(*) AS c FROM habits")["c"] == 0:
        for name, pillar, desc in SEED_HABITS:
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )

```


## `criar_projeto_samurai.py`

```python
import ast
import os
import sys
from pathlib import Path

BASE = Path(r"C:\Users\Ricardo Fernandes\Desktop\Projeto Samurai")

def aplicar_patch():
    print("=" * 60)
    print("⚔️  PATCH SPRINT 3 - CORREÇÃO DO LEITOR DE NOTÍCIAS")
    print("=" * 60)

    if not BASE.exists():
        print(f"[ERRO] Pasta do projeto não encontrada: {BASE}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 1. Atualizar requirements.txt (Adicionar feedparser)
    # -----------------------------------------------------------------------
    req_file = BASE / "requirements.txt"
    req_txt = req_file.read_text(encoding="utf-8")
    if "feedparser" not in req_txt:
        req_txt += "feedparser>=6.0.10\n"
        req_file.write_text(req_txt, encoding="utf-8")
        print("[OK] Corrigido: requirements.txt (feedparser adicionado)")
    else:
        print("[SKIP] requirements.txt já possui feedparser.")

    # -----------------------------------------------------------------------
    # 2. Corrigir 03_Informacao.py
    # -----------------------------------------------------------------------
    info_file = BASE / "ui" / "pages" / "03_Informacao.py"
    
    novo_info = '''import streamlit as st
import sys
from pathlib import Path
import yfinance as yf
import requests
import feedparser

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db

init_db()

st.title("📰 Informação")
st.caption("Mundo, Brasil, Macaé, Legislativo e Finanças.")

# --- FINANÇAS ---
st.subheader("📈 Finanças (Tempo Real)")
col1, col2, col3 = st.columns(3)
tickers = {"Dólar": "BRL=X", "IBOVESPA": "^BVSP", "Bitcoin": "BTC-USD"}
cols = [col1, col2, col3]

for i, (nome, ticker) in enumerate(tickers.items()):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            preco = data['Close'].iloc[-1]
            with cols[i]:
                st.markdown(
                    f"""<div class="samurai-card">
                        <div class="titulo">{nome}</div>
                        <div class="valor">R$ {preco:,.2f}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    except Exception:
        with cols[i]:
            st.error(f"Erro ao carregar {nome}")

st.divider()

# --- NOTÍCIAS ---
st.subheader("🗞️ Últimas Notícias (G1)")
try:
    url = "https://g1.globo.com/rss/g1/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() # Levanta um erro se a requisição falhar
    
    feed = feedparser.parse(response.content)
    
    if feed.entries:
        for entry in feed.entries[:5]:
            st.markdown(f"- [{entry.title}]({entry.link})")
    else:
        st.warning("O feed de notícias está vazio no momento.")
except requests.exceptions.RequestException:
    st.warning("Não foi possível carregar as notícias (servidor do G1 fora do ar ou bloqueando a conexão).")
except Exception as e:
    st.warning("Erro inesperado ao carregar as notícias.")

st.divider()
st.subheader("⚖️ Legislativo")
st.info("🚧 Integração com APIs do Senado, Câmara, ALERJ e Câmara de Macaé será implementada na Sprint 4.")
'''

    # Validação de sintaxe
    try:
        ast.parse(novo_info)
    except SyntaxError as e:
        print(f"[ERRO] Falha na validação de sintaxe: {e}")
        sys.exit(1)

    # Escrevendo o arquivo
    if info_file.exists() and info_file.read_text(encoding="utf-8") == novo_info:
        print("[SKIP] 03_Informacao.py já está atualizado.")
    else:
        info_file.write_text(novo_info, encoding="utf-8")
        print("[OK] Corrigido: ui/pages/03_Informacao.py (requests + feedparser)")

    # -----------------------------------------------------------------------
    # 3. Reiniciar o servidor e instalar dependências
    # -----------------------------------------------------------------------
    print("\nReiniciando o servidor e instalando novas dependências...")
    os.system('taskkill /F /FI "WINDOWTITLE eq Projeto Samurai" >nul 2>&1')
    
    # O INICIAR.bat já roda o pip install, então ele vai instalar o feedparser automaticamente
    os.startfile(BASE / "INICIAR.bat")
    print("[OK] Servidor reiniciado. Notícias corrigidas!")

if __name__ == "__main__":
    aplicar_patch()
```


## `gerar_codigo.py`

```python
"""
Gera um arquivo Markdown com o mapa completo do projeto.
Ignora __pycache__, data, .venv, .git, .idea, .vscode, node_modules e binários.
Uso:  py -3 gerar_codigo.py
Saída: PROJETO_SAMURAI.md na raiz.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent
IGNORE_DIRS = {
    "__pycache__", "data", ".venv", "venv", ".git",
    ".idea", ".vscode", "node_modules", ".pytest_cache",
}
IGNORE_EXT = {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg"}
OUTPUT = BASE / "PROJETO_SAMURAI.md"

LANG_MAP = {
    ".py": "python", ".bat": "bat", ".txt": "text",
    ".md": "markdown", ".json": "json", ".toml": "toml",
    ".css": "css", ".html": "html", ".js": "javascript",
}


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in IGNORE_EXT:
        return True
    return False


def generate() -> None:
    linhas: list[str] = ["# ⚔️ Projeto Samurai — Mapa do Código\n"]
    linhas.append("> Gerado automaticamente por `gerar_codigo.py`\n")
    linhas.append(f"> Raiz: `{BASE.name}`\n\n---\n")

    arquivos = sorted(
        p for p in BASE.rglob("*")
        if p.is_file() and not is_ignored(p.relative_to(BASE))
    )

    for path in arquivos:
        rel = path.relative_to(BASE)
        lang = LANG_MAP.get(path.suffix.lower(), "text")
        linhas.append(f"\n## `{rel.as_posix()}`\n")
        try:
            conteudo = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            conteudo = "<<arquivo binário ou ilegível>>"
        linhas.append(f"```{lang}")
        linhas.append(conteudo)
        linhas.append("```\n")

    OUTPUT.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[OK] Mapa gerado: {OUTPUT}")
    print(f"[OK] {len(arquivos)} arquivo(s) incluído(s).")


if __name__ == "__main__":
    generate()

```


## `INICIAR.bat`

```bat
@echo off
title Projeto Samurai
cd /d "%~dp0"

echo ==================================================
echo    PROJETO SAMURAI - Iniciando ambiente
echo ==================================================
echo.

echo [1/3] Verificando dependencias...
py -3 -m pip install --quiet --upgrade pip
py -3 -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

echo [2/3] Iniciando Streamlit na porta 8501...
echo [3/3] O navegador abrira automaticamente.
echo.
echo (Para encerrar o servidor, feche esta janela ou pressione Ctrl+C)
echo.

py -3 -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo Servidor encerrado.
pause

```


## `PROJETO_SAMURAI.md`

```markdown
# ⚔️ Projeto Samurai — Mapa do Código

> Gerado automaticamente por `gerar_codigo.py`

> Raiz: `Projeto Samurai`

---


## `.streamlit/config.toml`

```toml
[theme]
base="dark"
primaryColor="#8B0000"
backgroundColor="#0B0B0B"
secondaryBackgroundColor="#171717"
textColor="#F2F2F2"
font="sans serif"

```


## `app.py`

```python
"""
Projeto Samurai — Sistema Operacional Pessoal.
Entry point Streamlit. Configura tema, navegação e injeta CSS.
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from core.schema import init_db

init_db()

st.set_page_config(
    page_title="Projeto Samurai ⚔️",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

SAMURAI_CSS = """
<style>
:root {
    --s-red:        #8B0000;
    --s-dark-red:   #5C0000;
    --s-black:      #0B0B0B;
    --s-gray:       #171717;
    --s-gray-soft:  #1F1F1F;
    --s-white:      #FFFFFF;
    --s-white-soft: #CCCCCC;
}

/* Força o fundo escuro no app */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--s-black) !important;
}

/* Força cor do texto em TODOS os elementos comuns e containers do Streamlit */
h1, h2, h3, h4, h5, h6, p, span, li, label, 
div[data-testid="stMarkdownContainer"] *, 
[data-testid="stWidgetLabel"] * {
    color: var(--s-white) !important;
}

/* Linha vermelha embaixo do H1 */
h1 {
    border-bottom: 2px solid var(--s-red) !important;
    padding-bottom: 8px !important;
    letter-spacing: .5px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--s-gray) !important;
    border-right: 1px solid var(--s-red) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--s-white) !important;
}

/* Cards Customizados */
.samurai-card {
    background-color: var(--s-gray-soft) !important;
    border-left: 4px solid var(--s-red) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
}
.samurai-card .titulo {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--s-white-soft) !important;
    margin-bottom: 6px !important;
    font-weight: 600 !important;
}
.samurai-card .valor {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--s-white) !important;
}
.samurai-card .detalhe {
    font-size: 0.85rem !important;
    color: var(--s-white-soft) !important;
    margin-top: 6px !important;
}

/* Botões */
.stButton > button, .stFormSubmitButton > button {
    background-color: var(--s-red) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-dark-red) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--s-dark-red) !important;
    border-color: var(--s-white) !important;
}

/* Barras de Progresso */
.stProgress > div > div > div > div {
    background-color: var(--s-red) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--s-gray) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-red) !important;
}

/* Divisores e Caixas de Info/Alerta */
hr { border-color: var(--s-red) !important; opacity: .5 !important; }
.stAlert { 
    background-color: var(--s-gray-soft) !important; 
    color: var(--s-white) !important; 
    border: 1px solid var(--s-red) !important; 
}
.stAlert * { color: var(--s-white) !important; }
</style>
"""

st.markdown(SAMURAI_CSS, unsafe_allow_html=True)


home = st.Page("ui/pages/00_Home.py", title="🏯 Dojo", default=True)
consistencia = st.Page("ui/pages/07_Consistencia.py", title="🎯 Consistência")
corpo = st.Page("ui/pages/01_Corpo.py", title="💪 Corpo")
mente = st.Page("ui/pages/02_Mente.py", title="🧠 Mente")
informacao = st.Page("ui/pages/03_Informacao.py", title="📰 Informação")
patrimonio = st.Page("ui/pages/04_Patrimonio.py", title="💎 Patrimônio")
descanso = st.Page("ui/pages/05_Descanso.py", title="🌿 Descanso & Lazer")
autoconhecimento = st.Page("ui/pages/06_Autoconhecimento.py", title="🪞 Autoconhecimento")

pg = st.navigation(
    {
        "⚔️ Comando": [home, consistencia],
        "🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento],
    }
)

pg.run()

```


## `assets/.gitkeep`

```text

```


## `core/__init__.py`

```python
"""Núcleo do Projeto Samurai (banco, schema, utilitários)."""

```


## `core/database.py`

```python
"""
Conexão SQLite centralizada.
- WAL mode para leituras concorrentes.
- Lock em memória para evitar writes simultâneos (Streamlit é multithread).
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "samurai.db"

_lock = threading.RLock()


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão configurada. O caller é responsável por fechar."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def execute(sql: str, params: tuple = ()) -> int:
    """Executa um INSERT/UPDATE/DELETE. Retorna lastrowid."""
    with _lock:
        with get_connection() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid


def executemany(sql: str, seq_params: list[tuple]) -> None:
    with _lock:
        with get_connection() as conn:
            conn.executemany(sql, seq_params)
            conn.commit()


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchall()


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchone()

```


## `core/schema.py`

```python
"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    if query_one("SELECT COUNT(*) AS c FROM habits")["c"] == 0:
        for name, pillar, desc in SEED_HABITS:
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )

```


## `criar_projeto_samurai.py`

```python
import ast
import os
import sys
from pathlib import Path

BASE = Path(r"C:\Users\Ricardo Fernandes\Desktop\Projeto Samurai")

def aplicar_patch():
    print("=" * 60)
    print("⚔️  PATCH SPRINT 3: INFORMAÇÃO, PATRIMÔNIO, DESCANSO, AUTOCONHECIMENTO")
    print("=" * 60)

    if not BASE.exists():
        print(f"[ERRO] Pasta do projeto não encontrada: {BASE}")
        sys.exit(1)

    arquivos = {}

    # -----------------------------------------------------------------------
    # 1. 03_Informacao.py
    # -----------------------------------------------------------------------
    arquivos["ui/pages/03_Informacao.py"] = '''import streamlit as st
import sys
from pathlib import Path
import yfinance as yf
import urllib.request
import xml.etree.ElementTree as ET

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db

init_db()

st.title("📰 Informação")
st.caption("Mundo, Brasil, Macaé, Legislativo e Finanças.")

# --- FINANÇAS ---
st.subheader("📈 Finanças (Tempo Real)")
col1, col2, col3 = st.columns(3)
tickers = {"Dólar": "BRL=X", "IBOVESPA": "^BVSP", "Bitcoin": "BTC-USD"}
cols = [col1, col2, col3]

for i, (nome, ticker) in enumerate(tickers.items()):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            preco = data['Close'].iloc[-1]
            with cols[i]:
                st.markdown(
                    f"""<div class="samurai-card">
                        <div class="titulo">{nome}</div>
                        <div class="valor">R$ {preco:,.2f}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    except Exception:
        with cols[i]:
            st.error(f"Erro ao carregar {nome}")

st.divider()

# --- NOTÍCIAS ---
st.subheader("🗞️ Últimas Notícias (G1)")
try:
    url = "https://g1.globo.com/rss/g1/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    tree = ET.fromstring(response.read())
    
    for item in tree.findall('.//item')[:5]:
        title = item.find('title').text
        link = item.find('link').text
        st.markdown(f"- [{title}]({link})")
except Exception as e:
    st.warning("Não foi possível carregar as notícias no momento (verifique a conexão).")

st.divider()
st.subheader("⚖️ Legislativo")
st.info("🚧 Integração com APIs do Senado, Câmara, ALERJ e Câmara de Macaé será implementada na Sprint 4.")
'''

    # -----------------------------------------------------------------------
    # 2. 04_Patrimonio.py
    # -----------------------------------------------------------------------
    arquivos["ui/pages/04_Patrimonio.py"] = '''import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("💎 Patrimônio")
st.caption("Ações, notícias e controle de gastos.")

# --- AÇÕES ---
st.subheader("📊 Ações e FIIs")
col1, col2 = st.columns([2, 1])
with col1:
    ticker_input = st.text_input("Digite o ticker (ex: PETR4.SA, VALE3.SA, HGLG11.SA):", value="PETR4.SA")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    buscar = st.button("Buscar Cotação", use_container_width=True)

if buscar or ticker_input:
    try:
        ticker = yf.Ticker(ticker_input)
        data = ticker.history(period="5d")
        if not data.empty:
            preco_atual = data['Close'].iloc[-1]
            variacao = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
            
            cor = "#4CAF50" if variacao >= 0 else "#F44336"
            
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: {cor};">
                    <div class="titulo">{ticker_input}</div>
                    <div class="valor">R$ {preco_atual:.2f}</div>
                    <div class="detalhe" style="color: {cor};">Variação (5d): {variacao:+.2f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )
            
            with st.expander("Ver Notícias do Ticker"):
                noticias = ticker.news
                if noticias:
                    for n in noticias[:3]:
                        st.markdown(f"- [{n['title']}]({n['link']})")
                else:
                    st.write("Nenhuma notícia recente encontrada.")
        else:
            st.error("Ticker não encontrado ou sem dados.")
    except Exception:
        st.error("Erro ao buscar dados. Verifique o ticker digitado.")

st.divider()

# --- GASTOS ---
st.subheader("💸 Registro de Gastos")

with st.form("form_gasto"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        descricao = st.text_input("Descrição")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
    with col3:
        categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Outros"])
    
    submitted = st.form_submit_button("Registrar Gasto", use_container_width=True)

if submitted:
    if descricao and valor > 0:
        execute(
            "INSERT INTO expenses (expense_date, description, amount, category) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), descricao, valor, categoria)
        )
        st.success("Gasto registrado!")
        st.rerun()
    else:
        st.error("Preencha a descrição e um valor maior que zero.")

# Listar gastos
gastos = query_all("SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 10")
if gastos:
    st.markdown("### Últimos Gastos")
    for g in gastos:
        st.markdown(
            f"""<div class="samurai-card" style="border-left-color: #171717; padding: 10px;">
                <div style="display: flex; justify-content: space-between; color: #CCC;">
                    <span>{g['description']}</span>
                    <span>R$ {g['amount']:.2f} ({g['category']})</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
'''

    # -----------------------------------------------------------------------
    # 3. 05_Descanso.py
    # -----------------------------------------------------------------------
    arquivos["ui/pages/05_Descanso.py"] = '''import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

st.title("🌿 Descanso & Lazer")
st.caption("Sugestões semanais para recarregar as energias.")

# Pegar a semana do ano para alternar as sugestões
semana_ano = date.today().isocalendar()[1]

MACAÉ = [
    {"local": "Praia dos Cavaleiros", "dica": "Caminhada na orla e um açaí no fim da tarde."},
    {"local": "Lagoa de Imboassica", "dica": "Passeio de caiaque ou pedalinho, ótimo para desacelerar."},
    {"local": "Pico do Frade", "dica": "Trilha leve com vista panorâmica da cidade. Leve água."},
    {"local": "Praia do Pecado", "dica": "Lugar mais reservado para ler um livro e relaxar."},
    {"local": "Parque Municipal da Lagoa", "dica": "Caminhada e contato com a natureza."},
]

ARREDORES = [
    {"local": "Búzios - Rua das Pedras", "dica": "Almoço, caminhada e fim de tarde na praia de Geribá."},
    {"local": "Cabo Frio - Praia do Forte", "dica": "Visitar as dunas e a Fortaleza de São Mateus."},
    {"local": "Arraial do Cabo - Pontal do Atalaia", "dica": "Levar água e preparar para o visual mais bonito da região."},
    {"local": "Lumiar (Nova Friburgo)", "dica": "Pousada, cachoeiras e gastronomia mineira."},
    {"local": "Rio das Ostras - Costazul", "dica": "Feira de artesanato e passeio na lagoa."},
]

sugestao_macae = MACAÉ[semana_ano % len(MACAÉ)]
sugestao_arredores = ARREDORES[semana_ano % len(ARREDORES)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão em Macaé</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_macae['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_macae['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão nos Arredores</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_arredores['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_arredores['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.info("💡 Lembre-se de usar o **Cartão Macaé** nos estabelecimentos parceiros da cidade.")
'''

    # -----------------------------------------------------------------------
    # 4. 06_Autoconhecimento.py
    # -----------------------------------------------------------------------
    arquivos["ui/pages/06_Autoconhecimento.py"] = '''import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("🪞 Autoconhecimento")
st.caption("Diário reflexivo e meditação.")

PROMPTS = [
    "O que drenou minha energia hoje e por quê?",
    "Qual pequena vitória eu tive hoje?",
    "O que eu faria diferente se pudesse recomeçar o dia?",
    "Pelo que sou grato neste exato momento?",
    "Qual pensamento negativo eu posso deixar ir embora?",
    "Como eu tratei as pessoas ao meu redor hoje?",
    "O que aprendi sobre mim mesmo nesta semana?",
]

# Define o prompt do dia baseado no dia do ano (para ser consistente durante o dia)
prompt_do_dia = PROMPTS[date.today().toordinal() % len(PROMPTS)]

st.subheader("📝 Diário Reflexivo")
st.markdown(f"**Prompt de hoje:** *{prompt_do_dia}*")

with st.form("form_journal"):
    texto = st.text_area("Sua reflexão:", height=150, placeholder="Escreva livremente...")
    submitted = st.form_submit_button("Salvar no Diário", use_container_width=True)

if submitted and texto.strip():
    execute(
        "INSERT INTO journal_entries (entry_date, prompt, content) VALUES (?, ?, ?)",
        (date.today().isoformat(), prompt_do_dia, texto.strip())
    )
    st.success("Reflexão salva.")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Meditação Curta")
st.markdown("""
**Respiração Box (5 minutos):**
1. Inspire contando até **4**.
2. Segure a respiração contando até **4**.
3. Expire lentamente contando até **4**.
4. Aguarde contando até **4**.
5. Repita por 5 minutos.
""")

st.divider()
st.subheader("📚 Histórico de Reflexões")

entries = query_all("SELECT * FROM journal_entries ORDER BY entry_date DESC, id DESC LIMIT 5")
if not entries:
    st.info("Nenhuma reflexão registrada ainda.")
else:
    for e in entries:
        with st.expander(f"📅 {e['entry_date']} — {e['prompt']}"):
            st.write(e['content'])
'''

    # -----------------------------------------------------------------------
    # Execução da gravação
    # -----------------------------------------------------------------------
    for rel_path, conteudo in arquivos.items():
        file_path = BASE / rel_path
        
        # Validação de sintaxe (Regra 3)
        try:
            ast.parse(conteudo)
        except SyntaxError as e:
            print(f"[ERRO] Falha na validação de sintaxe de {rel_path}: {e}")
            sys.exit(1)

        # Idempotência e Escrita
        if file_path.exists():
            existente = file_path.read_text(encoding="utf-8")
            if existente == conteudo:
                print(f"[SKIP] {rel_path} já está atualizado.")
                continue
        
        file_path.write_text(conteudo, encoding="utf-8")
        print(f"[OK] Corrigido: {rel_path}")

    # -----------------------------------------------------------------------
    # Reiniciar o servidor
    # -----------------------------------------------------------------------
    print("\nReiniciando o servidor...")
    os.system('taskkill /F /FI "WINDOWTITLE eq Projeto Samurai" >nul 2>&1')
    os.startfile(BASE / "INICIAR.bat")
    print("[OK] Servidor reiniciado. Sprint 3 concluída!")

if __name__ == "__main__":
    aplicar_patch()
```


## `gerar_codigo.py`

```python
"""
Gera um arquivo Markdown com o mapa completo do projeto.
Ignora __pycache__, data, .venv, .git, .idea, .vscode, node_modules e binários.
Uso:  py -3 gerar_codigo.py
Saída: PROJETO_SAMURAI.md na raiz.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent
IGNORE_DIRS = {
    "__pycache__", "data", ".venv", "venv", ".git",
    ".idea", ".vscode", "node_modules", ".pytest_cache",
}
IGNORE_EXT = {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg"}
OUTPUT = BASE / "PROJETO_SAMURAI.md"

LANG_MAP = {
    ".py": "python", ".bat": "bat", ".txt": "text",
    ".md": "markdown", ".json": "json", ".toml": "toml",
    ".css": "css", ".html": "html", ".js": "javascript",
}


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in IGNORE_EXT:
        return True
    return False


def generate() -> None:
    linhas: list[str] = ["# ⚔️ Projeto Samurai — Mapa do Código\n"]
    linhas.append("> Gerado automaticamente por `gerar_codigo.py`\n")
    linhas.append(f"> Raiz: `{BASE.name}`\n\n---\n")

    arquivos = sorted(
        p for p in BASE.rglob("*")
        if p.is_file() and not is_ignored(p.relative_to(BASE))
    )

    for path in arquivos:
        rel = path.relative_to(BASE)
        lang = LANG_MAP.get(path.suffix.lower(), "text")
        linhas.append(f"\n## `{rel.as_posix()}`\n")
        try:
            conteudo = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            conteudo = "<<arquivo binário ou ilegível>>"
        linhas.append(f"```{lang}")
        linhas.append(conteudo)
        linhas.append("```\n")

    OUTPUT.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[OK] Mapa gerado: {OUTPUT}")
    print(f"[OK] {len(arquivos)} arquivo(s) incluído(s).")


if __name__ == "__main__":
    generate()

```


## `INICIAR.bat`

```bat
@echo off
title Projeto Samurai
cd /d "%~dp0"

echo ==================================================
echo    PROJETO SAMURAI - Iniciando ambiente
echo ==================================================
echo.

echo [1/3] Verificando dependencias...
py -3 -m pip install --quiet --upgrade pip
py -3 -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

echo [2/3] Iniciando Streamlit na porta 8501...
echo [3/3] O navegador abrira automaticamente.
echo.
echo (Para encerrar o servidor, feche esta janela ou pressione Ctrl+C)
echo.

py -3 -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo Servidor encerrado.
pause

```


## `PROJETO_SAMURAI.md`

```markdown
# ⚔️ Projeto Samurai — Mapa do Código

> Gerado automaticamente por `gerar_codigo.py`

> Raiz: `Projeto Samurai`

---


## `.streamlit/config.toml`

```toml
[theme]
base="dark"
primaryColor="#8B0000"
backgroundColor="#0B0B0B"
secondaryBackgroundColor="#171717"
textColor="#F2F2F2"
font="sans serif"

```


## `app.py`

```python
"""
Projeto Samurai — Sistema Operacional Pessoal.
Entry point Streamlit. Configura tema, navegação e injeta CSS.
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from core.schema import init_db

init_db()

st.set_page_config(
    page_title="Projeto Samurai ⚔️",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

SAMURAI_CSS = """
<style>
:root {
    --s-red:        #8B0000;
    --s-dark-red:   #5C0000;
    --s-black:      #0B0B0B;
    --s-gray:       #171717;
    --s-gray-soft:  #1F1F1F;
    --s-white:      #FFFFFF;
    --s-white-soft: #CCCCCC;
}

/* Força o fundo escuro no app */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--s-black) !important;
}

/* Força cor do texto em TODOS os elementos comuns e containers do Streamlit */
h1, h2, h3, h4, h5, h6, p, span, li, label, 
div[data-testid="stMarkdownContainer"] *, 
[data-testid="stWidgetLabel"] * {
    color: var(--s-white) !important;
}

/* Linha vermelha embaixo do H1 */
h1 {
    border-bottom: 2px solid var(--s-red) !important;
    padding-bottom: 8px !important;
    letter-spacing: .5px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--s-gray) !important;
    border-right: 1px solid var(--s-red) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--s-white) !important;
}

/* Cards Customizados */
.samurai-card {
    background-color: var(--s-gray-soft) !important;
    border-left: 4px solid var(--s-red) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
}
.samurai-card .titulo {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--s-white-soft) !important;
    margin-bottom: 6px !important;
    font-weight: 600 !important;
}
.samurai-card .valor {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--s-white) !important;
}
.samurai-card .detalhe {
    font-size: 0.85rem !important;
    color: var(--s-white-soft) !important;
    margin-top: 6px !important;
}

/* Botões */
.stButton > button, .stFormSubmitButton > button {
    background-color: var(--s-red) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-dark-red) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--s-dark-red) !important;
    border-color: var(--s-white) !important;
}

/* Barras de Progresso */
.stProgress > div > div > div > div {
    background-color: var(--s-red) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--s-gray) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-red) !important;
}

/* Divisores e Caixas de Info/Alerta */
hr { border-color: var(--s-red) !important; opacity: .5 !important; }
.stAlert { 
    background-color: var(--s-gray-soft) !important; 
    color: var(--s-white) !important; 
    border: 1px solid var(--s-red) !important; 
}
.stAlert * { color: var(--s-white) !important; }
</style>
"""

st.markdown(SAMURAI_CSS, unsafe_allow_html=True)


home = st.Page("ui/pages/00_Home.py", title="🏯 Dojo", default=True)
consistencia = st.Page("ui/pages/07_Consistencia.py", title="🎯 Consistência")
corpo = st.Page("ui/pages/01_Corpo.py", title="💪 Corpo")
mente = st.Page("ui/pages/02_Mente.py", title="🧠 Mente")
informacao = st.Page("ui/pages/03_Informacao.py", title="📰 Informação")
patrimonio = st.Page("ui/pages/04_Patrimonio.py", title="💎 Patrimônio")
descanso = st.Page("ui/pages/05_Descanso.py", title="🌿 Descanso & Lazer")
autoconhecimento = st.Page("ui/pages/06_Autoconhecimento.py", title="🪞 Autoconhecimento")

pg = st.navigation(
    {
        "⚔️ Comando": [home, consistencia],
        "🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento],
    }
)

pg.run()

```


## `assets/.gitkeep`

```text

```


## `core/__init__.py`

```python
"""Núcleo do Projeto Samurai (banco, schema, utilitários)."""

```


## `core/database.py`

```python
"""
Conexão SQLite centralizada.
- WAL mode para leituras concorrentes.
- Lock em memória para evitar writes simultâneos (Streamlit é multithread).
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "samurai.db"

_lock = threading.RLock()


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão configurada. O caller é responsável por fechar."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def execute(sql: str, params: tuple = ()) -> int:
    """Executa um INSERT/UPDATE/DELETE. Retorna lastrowid."""
    with _lock:
        with get_connection() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid


def executemany(sql: str, seq_params: list[tuple]) -> None:
    with _lock:
        with get_connection() as conn:
            conn.executemany(sql, seq_params)
            conn.commit()


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchall()


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchone()

```


## `core/schema.py`

```python
"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    if query_one("SELECT COUNT(*) AS c FROM habits")["c"] == 0:
        for name, pillar, desc in SEED_HABITS:
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )

```


## `criar_projeto_samurai.py`

```python
import ast
import os
import sqlite3
import sys
from pathlib import Path

BASE = Path(r"C:\Users\Ricardo Fernandes\Desktop\Projeto Samurai")

def aplicar_patch():
    print("=" * 60)
    print("⚔️  PATCH DEFINITIVO - FORÇANDO CRIAÇÃO DE TABELA")
    print("=" * 60)

    if not BASE.exists():
        print(f"[ERRO] Pasta do projeto não encontrada: {BASE}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 1. Injetar a tabela diretamente no SQLite (Força Bruta)
    # -----------------------------------------------------------------------
    db_path = BASE / "data" / "samurai.db"
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS exercise_logs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date      TEXT    NOT NULL,
            exercise_name TEXT    NOT NULL,
            reps          INTEGER NOT NULL DEFAULT 0,
            sets          INTEGER NOT NULL DEFAULT 1,
            notes         TEXT,
            UNIQUE (log_date, exercise_name)
        );
        """)
        conn.commit()
        conn.close()
        print("[OK] Tabela 'exercise_logs' injetada diretamente no banco de dados.")
    except Exception as e:
        print(f"[ERRO] Falha ao injetar no banco: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 2. Sobrescrever o schema.py (Garantia de integridade)
    # -----------------------------------------------------------------------
    schema_file = BASE / "core" / "schema.py"
    schema_txt = '''"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    if query_one("SELECT COUNT(*) AS c FROM habits")["c"] == 0:
        for name, pillar, desc in SEED_HABITS:
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )
'''
    try:
        ast.parse(schema_txt)
        schema_file.write_text(schema_txt, encoding="utf-8")
        print("[OK] Corrigido: core/schema.py (Sobrescrito com sucesso)")
    except SyntaxError as e:
        print(f"[ERRO] Falha na validação do schema.py: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 3. Sobrescrever 01_Corpo.py (Garantia de execução do init_db)
    # -----------------------------------------------------------------------
    corpo_file = BASE / "ui" / "pages" / "01_Corpo.py"
    corpo_txt = '''import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()
'''
    try:
        ast.parse(corpo_txt)
        corpo_file.write_text(corpo_txt, encoding="utf-8")
        print("[OK] Corrigido: ui/pages/01_Corpo.py (Sobrescrito com sucesso)")
    except SyntaxError as e:
        print(f"[ERRO] Falha na validação do 01_Corpo.py: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 4. Reiniciar o servidor
    # -----------------------------------------------------------------------
    print("\nReiniciando o servidor...")
    os.system('taskkill /F /FI "WINDOWTITLE eq Projeto Samurai" >nul 2>&1')
    os.startfile(BASE / "INICIAR.bat")
    print("[OK] Servidor reiniciado. O erro do banco de dados foi sanado.")

if __name__ == "__main__":
    aplicar_patch()
```


## `gerar_codigo.py`

```python
"""
Gera um arquivo Markdown com o mapa completo do projeto.
Ignora __pycache__, data, .venv, .git, .idea, .vscode, node_modules e binários.
Uso:  py -3 gerar_codigo.py
Saída: PROJETO_SAMURAI.md na raiz.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent
IGNORE_DIRS = {
    "__pycache__", "data", ".venv", "venv", ".git",
    ".idea", ".vscode", "node_modules", ".pytest_cache",
}
IGNORE_EXT = {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg"}
OUTPUT = BASE / "PROJETO_SAMURAI.md"

LANG_MAP = {
    ".py": "python", ".bat": "bat", ".txt": "text",
    ".md": "markdown", ".json": "json", ".toml": "toml",
    ".css": "css", ".html": "html", ".js": "javascript",
}


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in IGNORE_EXT:
        return True
    return False


def generate() -> None:
    linhas: list[str] = ["# ⚔️ Projeto Samurai — Mapa do Código\n"]
    linhas.append("> Gerado automaticamente por `gerar_codigo.py`\n")
    linhas.append(f"> Raiz: `{BASE.name}`\n\n---\n")

    arquivos = sorted(
        p for p in BASE.rglob("*")
        if p.is_file() and not is_ignored(p.relative_to(BASE))
    )

    for path in arquivos:
        rel = path.relative_to(BASE)
        lang = LANG_MAP.get(path.suffix.lower(), "text")
        linhas.append(f"\n## `{rel.as_posix()}`\n")
        try:
            conteudo = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            conteudo = "<<arquivo binário ou ilegível>>"
        linhas.append(f"```{lang}")
        linhas.append(conteudo)
        linhas.append("```\n")

    OUTPUT.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[OK] Mapa gerado: {OUTPUT}")
    print(f"[OK] {len(arquivos)} arquivo(s) incluído(s).")


if __name__ == "__main__":
    generate()

```


## `INICIAR.bat`

```bat
@echo off
title Projeto Samurai
cd /d "%~dp0"

echo ==================================================
echo    PROJETO SAMURAI - Iniciando ambiente
echo ==================================================
echo.

echo [1/3] Verificando dependencias...
py -3 -m pip install --quiet --upgrade pip
py -3 -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

echo [2/3] Iniciando Streamlit na porta 8501...
echo [3/3] O navegador abrira automaticamente.
echo.
echo (Para encerrar o servidor, feche esta janela ou pressione Ctrl+C)
echo.

py -3 -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo Servidor encerrado.
pause

```


## `PROJETO_SAMURAI.md`

```markdown
# ⚔️ Projeto Samurai — Mapa do Código

> Gerado automaticamente por `gerar_codigo.py`

> Raiz: `Projeto Samurai`

---


## `.streamlit/config.toml`

```toml
[theme]
base="dark"
primaryColor="#8B0000"
backgroundColor="#0B0B0B"
secondaryBackgroundColor="#171717"
textColor="#F2F2F2"
font="sans serif"

```


## `app.py`

```python
"""
Projeto Samurai — Sistema Operacional Pessoal.
Entry point Streamlit. Configura tema, navegação e injeta CSS.
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from core.schema import init_db

init_db()

st.set_page_config(
    page_title="Projeto Samurai ⚔️",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

SAMURAI_CSS = """
<style>
:root {
    --s-red:        #8B0000;
    --s-dark-red:   #5C0000;
    --s-black:      #0B0B0B;
    --s-gray:       #171717;
    --s-gray-soft:  #1F1F1F;
    --s-white:      #FFFFFF;
    --s-white-soft: #CCCCCC;
}

/* Força o fundo escuro no app */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--s-black) !important;
}

/* Força cor do texto em TODOS os elementos comuns e containers do Streamlit */
h1, h2, h3, h4, h5, h6, p, span, li, label, 
div[data-testid="stMarkdownContainer"] *, 
[data-testid="stWidgetLabel"] * {
    color: var(--s-white) !important;
}

/* Linha vermelha embaixo do H1 */
h1 {
    border-bottom: 2px solid var(--s-red) !important;
    padding-bottom: 8px !important;
    letter-spacing: .5px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--s-gray) !important;
    border-right: 1px solid var(--s-red) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--s-white) !important;
}

/* Cards Customizados */
.samurai-card {
    background-color: var(--s-gray-soft) !important;
    border-left: 4px solid var(--s-red) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
}
.samurai-card .titulo {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--s-white-soft) !important;
    margin-bottom: 6px !important;
    font-weight: 600 !important;
}
.samurai-card .valor {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--s-white) !important;
}
.samurai-card .detalhe {
    font-size: 0.85rem !important;
    color: var(--s-white-soft) !important;
    margin-top: 6px !important;
}

/* Botões */
.stButton > button, .stFormSubmitButton > button {
    background-color: var(--s-red) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-dark-red) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--s-dark-red) !important;
    border-color: var(--s-white) !important;
}

/* Barras de Progresso */
.stProgress > div > div > div > div {
    background-color: var(--s-red) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--s-gray) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-red) !important;
}

/* Divisores e Caixas de Info/Alerta */
hr { border-color: var(--s-red) !important; opacity: .5 !important; }
.stAlert { 
    background-color: var(--s-gray-soft) !important; 
    color: var(--s-white) !important; 
    border: 1px solid var(--s-red) !important; 
}
.stAlert * { color: var(--s-white) !important; }
</style>
"""

st.markdown(SAMURAI_CSS, unsafe_allow_html=True)


home = st.Page("ui/pages/00_Home.py", title="🏯 Dojo", default=True)
consistencia = st.Page("ui/pages/07_Consistencia.py", title="🎯 Consistência")
corpo = st.Page("ui/pages/01_Corpo.py", title="💪 Corpo")
mente = st.Page("ui/pages/02_Mente.py", title="🧠 Mente")
informacao = st.Page("ui/pages/03_Informacao.py", title="📰 Informação")
patrimonio = st.Page("ui/pages/04_Patrimonio.py", title="💎 Patrimônio")
descanso = st.Page("ui/pages/05_Descanso.py", title="🌿 Descanso & Lazer")
autoconhecimento = st.Page("ui/pages/06_Autoconhecimento.py", title="🪞 Autoconhecimento")

pg = st.navigation(
    {
        "⚔️ Comando": [home, consistencia],
        "🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento],
    }
)

pg.run()

```


## `assets/.gitkeep`

```text

```


## `core/__init__.py`

```python
"""Núcleo do Projeto Samurai (banco, schema, utilitários)."""

```


## `core/database.py`

```python
"""
Conexão SQLite centralizada.
- WAL mode para leituras concorrentes.
- Lock em memória para evitar writes simultâneos (Streamlit é multithread).
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "samurai.db"

_lock = threading.RLock()


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão configurada. O caller é responsável por fechar."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def execute(sql: str, params: tuple = ()) -> int:
    """Executa um INSERT/UPDATE/DELETE. Retorna lastrowid."""
    with _lock:
        with get_connection() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid


def executemany(sql: str, seq_params: list[tuple]) -> None:
    with _lock:
        with get_connection() as conn:
            conn.executemany(sql, seq_params)
            conn.commit()


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchall()


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchone()

```


## `core/schema.py`

```python
"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    if query_one("SELECT COUNT(*) AS c FROM habits")["c"] == 0:
        for name, pillar, desc in SEED_HABITS:
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )

```


## `criar_projeto_samurai.py`

```python
import ast
import os
import sqlite3
import sys
from pathlib import Path

BASE = Path(r"C:\Users\Ricardo Fernandes\Desktop\Projeto Samurai")

def aplicar_patch():
    print("=" * 60)
    print("⚔️  PATCH DEFINITIVO - FORÇANDO CRIAÇÃO DE TABELA")
    print("=" * 60)

    if not BASE.exists():
        print(f"[ERRO] Pasta do projeto não encontrada: {BASE}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 1. Injetar a tabela diretamente no SQLite (Força Bruta)
    # -----------------------------------------------------------------------
    db_path = BASE / "data" / "samurai.db"
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS exercise_logs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date      TEXT    NOT NULL,
            exercise_name TEXT    NOT NULL,
            reps          INTEGER NOT NULL DEFAULT 0,
            sets          INTEGER NOT NULL DEFAULT 1,
            notes         TEXT,
            UNIQUE (log_date, exercise_name)
        );
        """)
        conn.commit()
        conn.close()
        print("[OK] Tabela 'exercise_logs' injetada diretamente no banco de dados.")
    except Exception as e:
        print(f"[ERRO] Falha ao injetar no banco: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 2. Sobrescrever o schema.py (Garantia de integridade)
    # -----------------------------------------------------------------------
    schema_file = BASE / "core" / "schema.py"
    schema_txt = '''"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    if query_one("SELECT COUNT(*) AS c FROM habits")["c"] == 0:
        for name, pillar, desc in SEED_HABITS:
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )
'''
    try:
        ast.parse(schema_txt)
        schema_file.write_text(schema_txt, encoding="utf-8")
        print("[OK] Corrigido: core/schema.py (Sobrescrito com sucesso)")
    except SyntaxError as e:
        print(f"[ERRO] Falha na validação do schema.py: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 3. Sobrescrever 01_Corpo.py (Garantia de execução do init_db)
    # -----------------------------------------------------------------------
    corpo_file = BASE / "ui" / "pages" / "01_Corpo.py"
    corpo_txt = '''import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()
'''
    try:
        ast.parse(corpo_txt)
        corpo_file.write_text(corpo_txt, encoding="utf-8")
        print("[OK] Corrigido: ui/pages/01_Corpo.py (Sobrescrito com sucesso)")
    except SyntaxError as e:
        print(f"[ERRO] Falha na validação do 01_Corpo.py: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 4. Reiniciar o servidor
    # -----------------------------------------------------------------------
    print("\nReiniciando o servidor...")
    os.system('taskkill /F /FI "WINDOWTITLE eq Projeto Samurai" >nul 2>&1')
    os.startfile(BASE / "INICIAR.bat")
    print("[OK] Servidor reiniciado. O erro do banco de dados foi sanado.")

if __name__ == "__main__":
    aplicar_patch()
```


## `gerar_codigo.py`

```python
"""
Gera um arquivo Markdown com o mapa completo do projeto.
Ignora __pycache__, data, .venv, .git, .idea, .vscode, node_modules e binários.
Uso:  py -3 gerar_codigo.py
Saída: PROJETO_SAMURAI.md na raiz.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent
IGNORE_DIRS = {
    "__pycache__", "data", ".venv", "venv", ".git",
    ".idea", ".vscode", "node_modules", ".pytest_cache",
}
IGNORE_EXT = {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg"}
OUTPUT = BASE / "PROJETO_SAMURAI.md"

LANG_MAP = {
    ".py": "python", ".bat": "bat", ".txt": "text",
    ".md": "markdown", ".json": "json", ".toml": "toml",
    ".css": "css", ".html": "html", ".js": "javascript",
}


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in IGNORE_EXT:
        return True
    return False


def generate() -> None:
    linhas: list[str] = ["# ⚔️ Projeto Samurai — Mapa do Código\n"]
    linhas.append("> Gerado automaticamente por `gerar_codigo.py`\n")
    linhas.append(f"> Raiz: `{BASE.name}`\n\n---\n")

    arquivos = sorted(
        p for p in BASE.rglob("*")
        if p.is_file() and not is_ignored(p.relative_to(BASE))
    )

    for path in arquivos:
        rel = path.relative_to(BASE)
        lang = LANG_MAP.get(path.suffix.lower(), "text")
        linhas.append(f"\n## `{rel.as_posix()}`\n")
        try:
            conteudo = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            conteudo = "<<arquivo binário ou ilegível>>"
        linhas.append(f"```{lang}")
        linhas.append(conteudo)
        linhas.append("```\n")

    OUTPUT.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[OK] Mapa gerado: {OUTPUT}")
    print(f"[OK] {len(arquivos)} arquivo(s) incluído(s).")


if __name__ == "__main__":
    generate()

```


## `INICIAR.bat`

```bat
@echo off
title Projeto Samurai
cd /d "%~dp0"

echo ==================================================
echo    PROJETO SAMURAI - Iniciando ambiente
echo ==================================================
echo.

echo [1/3] Verificando dependencias...
py -3 -m pip install --quiet --upgrade pip
py -3 -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

echo [2/3] Iniciando Streamlit na porta 8501...
echo [3/3] O navegador abrira automaticamente.
echo.
echo (Para encerrar o servidor, feche esta janela ou pressione Ctrl+C)
echo.

py -3 -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo Servidor encerrado.
pause

```


## `PROJETO_SAMURAI.md`

```markdown
# ⚔️ Projeto Samurai — Mapa do Código

> Gerado automaticamente por `gerar_codigo.py`

> Raiz: `Projeto Samurai`

---


## `.streamlit/config.toml`

```toml
[theme]
base="dark"
primaryColor="#8B0000"
backgroundColor="#0B0B0B"
secondaryBackgroundColor="#171717"
textColor="#F2F2F2"
font="sans serif"

```


## `app.py`

```python
"""
Projeto Samurai — Sistema Operacional Pessoal.
Entry point Streamlit. Configura tema, navegação e injeta CSS.
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
from core.schema import init_db

init_db()

st.set_page_config(
    page_title="Projeto Samurai ⚔️",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

SAMURAI_CSS = """
<style>
:root {
    --s-red:        #8B0000;
    --s-dark-red:   #5C0000;
    --s-black:      #0B0B0B;
    --s-gray:       #171717;
    --s-gray-soft:  #1F1F1F;
    --s-white:      #FFFFFF;
    --s-white-soft: #CCCCCC;
}

/* Força o fundo escuro no app */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--s-black) !important;
}

/* Força cor do texto em TODOS os elementos comuns e containers do Streamlit */
h1, h2, h3, h4, h5, h6, p, span, li, label, 
div[data-testid="stMarkdownContainer"] *, 
[data-testid="stWidgetLabel"] * {
    color: var(--s-white) !important;
}

/* Linha vermelha embaixo do H1 */
h1 {
    border-bottom: 2px solid var(--s-red) !important;
    padding-bottom: 8px !important;
    letter-spacing: .5px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--s-gray) !important;
    border-right: 1px solid var(--s-red) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--s-white) !important;
}

/* Cards Customizados */
.samurai-card {
    background-color: var(--s-gray-soft) !important;
    border-left: 4px solid var(--s-red) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
}
.samurai-card .titulo {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--s-white-soft) !important;
    margin-bottom: 6px !important;
    font-weight: 600 !important;
}
.samurai-card .valor {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--s-white) !important;
}
.samurai-card .detalhe {
    font-size: 0.85rem !important;
    color: var(--s-white-soft) !important;
    margin-top: 6px !important;
}

/* Botões */
.stButton > button, .stFormSubmitButton > button {
    background-color: var(--s-red) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-dark-red) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--s-dark-red) !important;
    border-color: var(--s-white) !important;
}

/* Barras de Progresso */
.stProgress > div > div > div > div {
    background-color: var(--s-red) !important;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--s-gray) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-red) !important;
}

/* Divisores e Caixas de Info/Alerta */
hr { border-color: var(--s-red) !important; opacity: .5 !important; }
.stAlert { 
    background-color: var(--s-gray-soft) !important; 
    color: var(--s-white) !important; 
    border: 1px solid var(--s-red) !important; 
}
.stAlert * { color: var(--s-white) !important; }
</style>
"""

st.markdown(SAMURAI_CSS, unsafe_allow_html=True)


home = st.Page("ui/pages/00_Home.py", title="🏯 Dojo", default=True)
consistencia = st.Page("ui/pages/07_Consistencia.py", title="🎯 Consistência")
corpo = st.Page("ui/pages/01_Corpo.py", title="💪 Corpo")
mente = st.Page("ui/pages/02_Mente.py", title="🧠 Mente")
informacao = st.Page("ui/pages/03_Informacao.py", title="📰 Informação")
patrimonio = st.Page("ui/pages/04_Patrimonio.py", title="💎 Patrimônio")
descanso = st.Page("ui/pages/05_Descanso.py", title="🌿 Descanso & Lazer")
autoconhecimento = st.Page("ui/pages/06_Autoconhecimento.py", title="🪞 Autoconhecimento")

pg = st.navigation(
    {
        "⚔️ Comando": [home, consistencia],
        "🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento],
    }
)

pg.run()

```


## `assets/.gitkeep`

```text

```


## `core/__init__.py`

```python
"""Núcleo do Projeto Samurai (banco, schema, utilitários)."""

```


## `core/database.py`

```python
"""
Conexão SQLite centralizada.
- WAL mode para leituras concorrentes.
- Lock em memória para evitar writes simultâneos (Streamlit é multithread).
"""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "samurai.db"

_lock = threading.RLock()


def get_connection() -> sqlite3.Connection:
    """Abre uma conexão configurada. O caller é responsável por fechar."""
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def execute(sql: str, params: tuple = ()) -> int:
    """Executa um INSERT/UPDATE/DELETE. Retorna lastrowid."""
    with _lock:
        with get_connection() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid


def executemany(sql: str, seq_params: list[tuple]) -> None:
    with _lock:
        with get_connection() as conn:
            conn.executemany(sql, seq_params)
            conn.commit()


def query_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchall()


def query_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with _lock:
        with get_connection() as conn:
            return conn.execute(sql, params).fetchone()

```


## `core/schema.py`

```python
"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    if query_one("SELECT COUNT(*) AS c FROM habits")["c"] == 0:
        for name, pillar, desc in SEED_HABITS:
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )

```


## `criar_projeto_samurai.py`

```python
import ast
import os
import sqlite3
import sys
from pathlib import Path

BASE = Path(r"C:\Users\Ricardo Fernandes\Desktop\Projeto Samurai")

def aplicar_patch():
    print("=" * 60)
    print("⚔️  PATCH DEFINITIVO - FORÇANDO CRIAÇÃO DE TABELA")
    print("=" * 60)

    if not BASE.exists():
        print(f"[ERRO] Pasta do projeto não encontrada: {BASE}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 1. Injetar a tabela diretamente no SQLite (Força Bruta)
    # -----------------------------------------------------------------------
    db_path = BASE / "data" / "samurai.db"
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS exercise_logs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date      TEXT    NOT NULL,
            exercise_name TEXT    NOT NULL,
            reps          INTEGER NOT NULL DEFAULT 0,
            sets          INTEGER NOT NULL DEFAULT 1,
            notes         TEXT,
            UNIQUE (log_date, exercise_name)
        );
        """)
        conn.commit()
        conn.close()
        print("[OK] Tabela 'exercise_logs' injetada diretamente no banco de dados.")
    except Exception as e:
        print(f"[ERRO] Falha ao injetar no banco: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 2. Sobrescrever o schema.py (Garantia de integridade)
    # -----------------------------------------------------------------------
    schema_file = BASE / "core" / "schema.py"
    schema_txt = '''"""
Criação das tabelas e seed inicial de hábitos.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

from datetime import date

from core.database import execute, query_one

DDL = [
    """
    CREATE TABLE IF NOT EXISTS habits (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT    NOT NULL,
        pillar      TEXT    NOT NULL,
        description TEXT,
        active      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS habit_logs (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id   INTEGER NOT NULL,
        log_date   TEXT    NOT NULL,
        done       INTEGER NOT NULL DEFAULT 0,
        notes      TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE (habit_id, log_date)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS daily_checkins (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_date  TEXT    NOT NULL UNIQUE,
        energy        INTEGER NOT NULL,
        sleep_hours   REAL    NOT NULL,
        mood          TEXT,
        stress        INTEGER NOT NULL,
        notes         TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_date TEXT    NOT NULL,
        description  TEXT    NOT NULL,
        amount       REAL    NOT NULL,
        category     TEXT,
        notes        TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS journal_entries (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date    TEXT    NOT NULL,
        prompt        TEXT,
        content       TEXT    NOT NULL,
        ai_reflection TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS book_progress (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        book_title   TEXT    NOT NULL UNIQUE,
        current_page INTEGER NOT NULL DEFAULT 0,
        total_pages  INTEGER NOT NULL DEFAULT 0,
        notes        TEXT,
        last_update  TEXT    NOT NULL DEFAULT (datetime('now'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        log_date      TEXT    NOT NULL,
        exercise_name TEXT    NOT NULL,
        reps          INTEGER NOT NULL DEFAULT 0,
        sets          INTEGER NOT NULL DEFAULT 1,
        notes         TEXT,
        UNIQUE (log_date, exercise_name)
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
    "CREATE INDEX IF NOT EXISTS idx_checkins_date   ON daily_checkins(checkin_date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_date   ON expenses(expense_date);",
]

SEED_HABITS = [
    ("Treino calistênico", "Corpo", "Treino progressivo do dia."),
    ("Mobilidade", "Corpo", "10 min de mobilidade."),
    ("Leitura guiada", "Mente", "Ler o trecho exato do dia."),
    ("Diário reflexivo", "Autoconhecimento", "Escrever uma reflexão breve."),
    ("Meditação curta", "Autoconhecimento", "5–10 min de respiração."),
    ("Check-in diário", "Consistência", "Energia + humor + sono."),
]


def init_db() -> None:
    for ddl in DDL:
        execute(ddl)

    if query_one("SELECT COUNT(*) AS c FROM habits")["c"] == 0:
        for name, pillar, desc in SEED_HABITS:
            execute(
                "INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)",
                (name, pillar, desc),
            )
'''
    try:
        ast.parse(schema_txt)
        schema_file.write_text(schema_txt, encoding="utf-8")
        print("[OK] Corrigido: core/schema.py (Sobrescrito com sucesso)")
    except SyntaxError as e:
        print(f"[ERRO] Falha na validação do schema.py: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 3. Sobrescrever 01_Corpo.py (Garantia de execução do init_db)
    # -----------------------------------------------------------------------
    corpo_file = BASE / "ui" / "pages" / "01_Corpo.py"
    corpo_txt = '''import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()
'''
    try:
        ast.parse(corpo_txt)
        corpo_file.write_text(corpo_txt, encoding="utf-8")
        print("[OK] Corrigido: ui/pages/01_Corpo.py (Sobrescrito com sucesso)")
    except SyntaxError as e:
        print(f"[ERRO] Falha na validação do 01_Corpo.py: {e}")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # 4. Reiniciar o servidor
    # -----------------------------------------------------------------------
    print("\nReiniciando o servidor...")
    os.system('taskkill /F /FI "WINDOWTITLE eq Projeto Samurai" >nul 2>&1')
    os.startfile(BASE / "INICIAR.bat")
    print("[OK] Servidor reiniciado. O erro do banco de dados foi sanado.")

if __name__ == "__main__":
    aplicar_patch()
```


## `gerar_codigo.py`

```python
"""
Gera um arquivo Markdown com o mapa completo do projeto.
Ignora __pycache__, data, .venv, .git, .idea, .vscode, node_modules e binários.
Uso:  py -3 gerar_codigo.py
Saída: PROJETO_SAMURAI.md na raiz.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent
IGNORE_DIRS = {
    "__pycache__", "data", ".venv", "venv", ".git",
    ".idea", ".vscode", "node_modules", ".pytest_cache",
}
IGNORE_EXT = {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg"}
OUTPUT = BASE / "PROJETO_SAMURAI.md"

LANG_MAP = {
    ".py": "python", ".bat": "bat", ".txt": "text",
    ".md": "markdown", ".json": "json", ".toml": "toml",
    ".css": "css", ".html": "html", ".js": "javascript",
}


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in IGNORE_EXT:
        return True
    return False


def generate() -> None:
    linhas: list[str] = ["# ⚔️ Projeto Samurai — Mapa do Código\n"]
    linhas.append("> Gerado automaticamente por `gerar_codigo.py`\n")
    linhas.append(f"> Raiz: `{BASE.name}`\n\n---\n")

    arquivos = sorted(
        p for p in BASE.rglob("*")
        if p.is_file() and not is_ignored(p.relative_to(BASE))
    )

    for path in arquivos:
        rel = path.relative_to(BASE)
        lang = LANG_MAP.get(path.suffix.lower(), "text")
        linhas.append(f"\n## `{rel.as_posix()}`\n")
        try:
            conteudo = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            conteudo = "<<arquivo binário ou ilegível>>"
        linhas.append(f"```{lang}")
        linhas.append(conteudo)
        linhas.append("```\n")

    OUTPUT.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[OK] Mapa gerado: {OUTPUT}")
    print(f"[OK] {len(arquivos)} arquivo(s) incluído(s).")


if __name__ == "__main__":
    generate()

```


## `INICIAR.bat`

```bat
@echo off
title Projeto Samurai
cd /d "%~dp0"

echo ==================================================
echo    PROJETO SAMURAI - Iniciando ambiente
echo ==================================================
echo.

echo [1/3] Verificando dependencias...
py -3 -m pip install --quiet --upgrade pip
py -3 -m pip install --quiet -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias. Verifique sua conexao.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas.
echo.

echo [2/3] Iniciando Streamlit na porta 8501...
echo [3/3] O navegador abrira automaticamente.
echo.
echo (Para encerrar o servidor, feche esta janela ou pressione Ctrl+C)
echo.

py -3 -m streamlit run app.py --server.port 8501 --server.headless false --browser.gatherUsageStats false

echo.
echo Servidor encerrado.
pause

```


## `requirements.txt`

```text
streamlit>=1.38.0
pandas>=2.2.0
yfinance>=0.2.40
requests>=2.31.0

```


## `services/__init__.py`

```python
"""Serviços externos (IA, yfinance, notícias, etc.)."""

```


## `ui/__init__.py`

```python
"""Camada de interface Streamlit."""

```


## `ui/pages/00_Home.py`

```python
"""Dojo — resumo do dia, hábitos pendentes e energia."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date

import streamlit as st

from core.database import query_all, query_one

today_iso = date.today().isoformat()

st.title("🏯 Dojo")
st.caption(f"Hoje é {date.today().strftime('%A, %d/%m/%Y')}")

checkin = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

col1, col2, col3 = st.columns(3)
if checkin:
    with col1:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Energia</div>
                <div class="valor">{checkin['energy']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Sono</div>
                <div class="valor">{checkin['sleep_hours']}h</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Estresse</div>
                <div class="valor">{checkin['stress']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("⚡ Nenhum check-in hoje. Vá em **Consistência** e registre sua energia.")

st.subheader("🎯 Hábitos pendentes hoje")

rows = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

pendentes = [r for r in rows if not r["done"]]
concluidos = [r for r in rows if r["done"]]

if not pendentes:
    st.success("🥋 Todos os hábitos foram cumpridos. Disciplina exemplar.")
else:
    for r in pendentes:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">{r['pillar']}</div>
                <div class="valor" style="font-size:1.1rem;">{r['name']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if concluidos:
    st.divider()
    st.caption(f"✅ {len(concluidos)} hábito(s) já cumprido(s) hoje")

st.divider()
if st.button("📝 Fazer check-in diário agora", use_container_width=True):
    st.switch_page("ui/pages/07_Consistencia.py")

```


## `ui/pages/01_Corpo.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()

```


## `ui/pages/02_Mente.py`

```python
import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db

init_db()  # Garante que as tabelas existam
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

# Busca o livro atual (pega o último atualizado)
livro = query_one("SELECT * FROM book_progress ORDER BY last_update DESC LIMIT 1")

col1, col2 = st.columns([2, 1])
with col1:
    if livro:
        st.markdown(f"**Livro atual:** {livro['book_title']}")
        
        # Calcula progresso
        pct = 0
        if livro['total_pages'] > 0:
            pct = min(1.0, livro['current_page'] / livro['total_pages'])
            
        st.progress(pct)
        st.caption(f"Página {livro['current_page']} de {livro['total_pages']} ({pct*100:.1f}%)")
    else:
        st.info("📖 Nenhum livro em andamento. Adicione um abaixo.")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Novo Livro", use_container_width=True):
        st.session_state["novo_livro"] = True

# Formulário para novo livro ou atualização
if not livro or st.session_state.get("novo_livro", False):
    with st.form("form_livro"):
        st.subheader("Adicionar Livro")
        titulo = st.text_input("Título do Livro")
        total_pag = st.number_input("Total de Páginas", min_value=1, value=100)
        
        if st.form_submit_button("Salvar Livro"):
            if titulo:
                execute(
                    """
                    INSERT INTO book_progress (book_title, total_pages) 
                    VALUES (?, ?)
                    ON CONFLICT(book_title) DO UPDATE SET total_pages = excluded.total_pages
                    """, (titulo, total_pag)
                )
                st.session_state["novo_livro"] = False
                st.rerun()
            else:
                st.error("O título é obrigatório.")

st.divider()
st.subheader("📖 Texto Exato do Dia")

# Área preparada para o futuro (Leitura PDF / IA)
st.info("Esta seção receberá o texto exato do dia gerado por IA nas próximas sprints.")
st.text_area("Seu resumo ou anotação da leitura de hoje:", placeholder="Digite aqui os insights do capítulo de hoje...")

if livro:
    st.divider()
    with st.form("form_progresso"):
        st.subheader("Atualizar Progresso")
        nova_pag = st.number_input("Página atual", min_value=0, max_value=int(livro['total_pages']), value=int(livro['current_page']))
        
        if st.form_submit_button("Atualizar Página", use_container_width=True):
            execute(
                "UPDATE book_progress SET current_page = ?, last_update = datetime('now') WHERE id = ?",
                (nova_pag, livro['id'])
            )
            st.rerun()

```


## `ui/pages/03_Informacao.py`

```python
import streamlit as st
st.title("📰 Informação")
st.info("🚧 Em construção — Sprint 2 trará notícias (Mundo, Brasil, RJ, Macaé), legislativo e finanças.")

```


## `ui/pages/04_Patrimonio.py`

```python
import streamlit as st
st.title("💎 Patrimônio")
st.info("🚧 Em construção — Sprint 2 trará cotações via yfinance, notícias por ticker e registro de gastos.")

```


## `ui/pages/05_Descanso.py`

```python
import streamlit as st
st.title("🌿 Descanso & Lazer")
st.info("🚧 Em construção — Sprint 2 trará sugestões semanais (Cartão Macaé + arredores).")

```


## `ui/pages/06_Autoconhecimento.py`

```python
import streamlit as st
st.title("🪞 Autoconhecimento")
st.info("🚧 Em construção — Sprint 2 trará diário reflexivo guiado por IA e meditações curtas.")

```


## `ui/pages/07_Consistencia.py`

```python
"""Consistência — check-in diário, marcação de hábitos e score anti-burnout."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date, timedelta

import streamlit as st

from core.database import execute, query_all, query_one

today = date.today()
today_iso = today.isoformat()


def calcular_burnout() -> tuple[float, dict]:
    """Score 0–100 (quanto maior, mais risco de burnout)."""
    week_ago = (today - timedelta(days=7)).isoformat()

    checkins = query_all(
        "SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?",
        (week_ago,),
    )
    total_habits = query_one("SELECT COUNT(*) AS c FROM habits WHERE active = 1")["c"] or 0
    logs = query_all(
        "SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,)
    )
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    total = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return total, {
        "avg_energy": avg_energy,
        "avg_stress": avg_stress,
        "avg_sleep": avg_sleep,
        "taxa": taxa,
    }


def classificar_burnout(score: float) -> tuple[str, str]:
    if score < 30:
        return "🟢 Baixo", "#2E7D32"
    if score < 60:
        return "🟡 Médio", "#F9A825"
    if score < 80:
        return "🟠 Alto", "#EF6C00"
    return "🔴 Crítico", "#C62828"


st.title("🎯 Consistência")
st.caption("Disciplina diária é o que forja o samurai.")

st.subheader("📝 Check-in do dia")

existente = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

MOOD_OPTIONS = ["Ótimo", "Bom", "Neutro", "Cansado", "Estressado", "Ansioso"]
mood_default = (
    MOOD_OPTIONS.index(existente["mood"])
    if existente and existente["mood"] in MOOD_OPTIONS
    else 2
)

with st.form("form_checkin", clear_on_submit=False):
    energy = st.slider(
        "Energia (1–10)", 1, 10,
        int(existente["energy"]) if existente else 6,
    )
    sleep_hours = st.number_input(
        "Horas de sono",
        min_value=0.0, max_value=16.0, step=0.5,
        value=float(existente["sleep_hours"]) if existente else 7.0,
    )
    mood = st.selectbox("Humor", MOOD_OPTIONS, index=mood_default)
    stress = st.slider(
        "Estresse (1–10)", 1, 10,
        int(existente["stress"]) if existente else 5,
    )
    notes = st.text_area(
        "Notas (opcional)",
        value=existente["notes"] if existente and existente["notes"] else "",
    )

    submit = st.form_submit_button("💾 Salvar check-in", use_container_width=True)

if submit:
    execute(
        """
        INSERT INTO daily_checkins
            (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy      = excluded.energy,
            sleep_hours = excluded.sleep_hours,
            mood        = excluded.mood,
            stress      = excluded.stress,
            notes       = excluded.notes
        """,
        (today_iso, energy, sleep_hours, mood, stress, notes or None),
    )
    st.success("[OK] Check-in registrado.")
    st.rerun()

st.divider()
st.subheader("🥋 Hábitos de hoje")

habits = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

alterou = False
for h in habits:
    novo = st.checkbox(
        f"**{h['pillar']}** · {h['name']}",
        value=bool(h["done"]),
        key=f"habit_{h['id']}",
    )
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done)
            VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """,
            (h["id"], today_iso, 1 if novo else 0),
        )
        alterou = True

if alterou:
    st.rerun()

st.divider()
st.subheader("🔥 Score Anti-Burnout (7 dias)")

score, metricas = calcular_burnout()
label, cor = classificar_burnout(score)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color:{cor};">
        <div class="titulo">Risco atual</div>
        <div class="valor" style="color:{cor};">{score:.0f}/100 — {label}</div>
        <div class="detalhe">
            Média energia: {metricas['avg_energy']:.1f} ·
            Sono: {metricas['avg_sleep']:.1f}h ·
            Estresse: {metricas['avg_stress']:.1f} ·
            Hábitos: {metricas['taxa']*100:.0f}%
        </div>
    </div>""",
    unsafe_allow_html=True,
)

st.progress(min(1.0, score / 100.0))

with st.expander("Como o score é calculado?"):
    st.markdown(
        """
- **Energia** (30 pts) — quanto menor, maior o risco.
- **Estresse** (30 pts) — quanto maior, maior o risco.
- **Sono** (20 pts) — abaixo de 8h aumenta o risco.
- **Aderência aos hábitos** (20 pts) — baixa execução nos últimos 7 dias eleva o risco.

**0–29:** 🟢 Baixo · **30–59:** 🟡 Médio · **60–79:** 🟠 Alto · **80–100:** 🔴 Crítico
        """
    )

if score >= 80:
    st.error("⚠️ Risco crítico. Priorize descanso hoje. Nenhum treino vale um colapso.")
elif score >= 60:
    st.warning("Atenção: sinais de sobrecarga. Reduza intensidade e priorize sono.")

```


## `ui/pages/__init__.py`

```python
"""Páginas do Projeto Samurai."""

```

```


## `requirements.txt`

```text
streamlit>=1.38.0
pandas>=2.2.0
yfinance>=0.2.40
requests>=2.31.0

```


## `services/__init__.py`

```python
"""Serviços externos (IA, yfinance, notícias, etc.)."""

```


## `ui/__init__.py`

```python
"""Camada de interface Streamlit."""

```


## `ui/pages/00_Home.py`

```python
"""Dojo — resumo do dia, hábitos pendentes e energia."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date

import streamlit as st

from core.database import query_all, query_one

today_iso = date.today().isoformat()

st.title("🏯 Dojo")
st.caption(f"Hoje é {date.today().strftime('%A, %d/%m/%Y')}")

checkin = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

col1, col2, col3 = st.columns(3)
if checkin:
    with col1:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Energia</div>
                <div class="valor">{checkin['energy']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Sono</div>
                <div class="valor">{checkin['sleep_hours']}h</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Estresse</div>
                <div class="valor">{checkin['stress']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("⚡ Nenhum check-in hoje. Vá em **Consistência** e registre sua energia.")

st.subheader("🎯 Hábitos pendentes hoje")

rows = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

pendentes = [r for r in rows if not r["done"]]
concluidos = [r for r in rows if r["done"]]

if not pendentes:
    st.success("🥋 Todos os hábitos foram cumpridos. Disciplina exemplar.")
else:
    for r in pendentes:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">{r['pillar']}</div>
                <div class="valor" style="font-size:1.1rem;">{r['name']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if concluidos:
    st.divider()
    st.caption(f"✅ {len(concluidos)} hábito(s) já cumprido(s) hoje")

st.divider()
if st.button("📝 Fazer check-in diário agora", use_container_width=True):
    st.switch_page("ui/pages/07_Consistencia.py")

```


## `ui/pages/01_Corpo.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()

```


## `ui/pages/02_Mente.py`

```python
import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db

init_db()  # Garante que as tabelas existam
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

# Busca o livro atual (pega o último atualizado)
livro = query_one("SELECT * FROM book_progress ORDER BY last_update DESC LIMIT 1")

col1, col2 = st.columns([2, 1])
with col1:
    if livro:
        st.markdown(f"**Livro atual:** {livro['book_title']}")
        
        # Calcula progresso
        pct = 0
        if livro['total_pages'] > 0:
            pct = min(1.0, livro['current_page'] / livro['total_pages'])
            
        st.progress(pct)
        st.caption(f"Página {livro['current_page']} de {livro['total_pages']} ({pct*100:.1f}%)")
    else:
        st.info("📖 Nenhum livro em andamento. Adicione um abaixo.")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Novo Livro", use_container_width=True):
        st.session_state["novo_livro"] = True

# Formulário para novo livro ou atualização
if not livro or st.session_state.get("novo_livro", False):
    with st.form("form_livro"):
        st.subheader("Adicionar Livro")
        titulo = st.text_input("Título do Livro")
        total_pag = st.number_input("Total de Páginas", min_value=1, value=100)
        
        if st.form_submit_button("Salvar Livro"):
            if titulo:
                execute(
                    """
                    INSERT INTO book_progress (book_title, total_pages) 
                    VALUES (?, ?)
                    ON CONFLICT(book_title) DO UPDATE SET total_pages = excluded.total_pages
                    """, (titulo, total_pag)
                )
                st.session_state["novo_livro"] = False
                st.rerun()
            else:
                st.error("O título é obrigatório.")

st.divider()
st.subheader("📖 Texto Exato do Dia")

# Área preparada para o futuro (Leitura PDF / IA)
st.info("Esta seção receberá o texto exato do dia gerado por IA nas próximas sprints.")
st.text_area("Seu resumo ou anotação da leitura de hoje:", placeholder="Digite aqui os insights do capítulo de hoje...")

if livro:
    st.divider()
    with st.form("form_progresso"):
        st.subheader("Atualizar Progresso")
        nova_pag = st.number_input("Página atual", min_value=0, max_value=int(livro['total_pages']), value=int(livro['current_page']))
        
        if st.form_submit_button("Atualizar Página", use_container_width=True):
            execute(
                "UPDATE book_progress SET current_page = ?, last_update = datetime('now') WHERE id = ?",
                (nova_pag, livro['id'])
            )
            st.rerun()

```


## `ui/pages/03_Informacao.py`

```python
import streamlit as st
st.title("📰 Informação")
st.info("🚧 Em construção — Sprint 2 trará notícias (Mundo, Brasil, RJ, Macaé), legislativo e finanças.")

```


## `ui/pages/04_Patrimonio.py`

```python
import streamlit as st
st.title("💎 Patrimônio")
st.info("🚧 Em construção — Sprint 2 trará cotações via yfinance, notícias por ticker e registro de gastos.")

```


## `ui/pages/05_Descanso.py`

```python
import streamlit as st
st.title("🌿 Descanso & Lazer")
st.info("🚧 Em construção — Sprint 2 trará sugestões semanais (Cartão Macaé + arredores).")

```


## `ui/pages/06_Autoconhecimento.py`

```python
import streamlit as st
st.title("🪞 Autoconhecimento")
st.info("🚧 Em construção — Sprint 2 trará diário reflexivo guiado por IA e meditações curtas.")

```


## `ui/pages/07_Consistencia.py`

```python
"""Consistência — check-in diário, marcação de hábitos e score anti-burnout."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date, timedelta

import streamlit as st

from core.database import execute, query_all, query_one

today = date.today()
today_iso = today.isoformat()


def calcular_burnout() -> tuple[float, dict]:
    """Score 0–100 (quanto maior, mais risco de burnout)."""
    week_ago = (today - timedelta(days=7)).isoformat()

    checkins = query_all(
        "SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?",
        (week_ago,),
    )
    total_habits = query_one("SELECT COUNT(*) AS c FROM habits WHERE active = 1")["c"] or 0
    logs = query_all(
        "SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,)
    )
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    total = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return total, {
        "avg_energy": avg_energy,
        "avg_stress": avg_stress,
        "avg_sleep": avg_sleep,
        "taxa": taxa,
    }


def classificar_burnout(score: float) -> tuple[str, str]:
    if score < 30:
        return "🟢 Baixo", "#2E7D32"
    if score < 60:
        return "🟡 Médio", "#F9A825"
    if score < 80:
        return "🟠 Alto", "#EF6C00"
    return "🔴 Crítico", "#C62828"


st.title("🎯 Consistência")
st.caption("Disciplina diária é o que forja o samurai.")

st.subheader("📝 Check-in do dia")

existente = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

MOOD_OPTIONS = ["Ótimo", "Bom", "Neutro", "Cansado", "Estressado", "Ansioso"]
mood_default = (
    MOOD_OPTIONS.index(existente["mood"])
    if existente and existente["mood"] in MOOD_OPTIONS
    else 2
)

with st.form("form_checkin", clear_on_submit=False):
    energy = st.slider(
        "Energia (1–10)", 1, 10,
        int(existente["energy"]) if existente else 6,
    )
    sleep_hours = st.number_input(
        "Horas de sono",
        min_value=0.0, max_value=16.0, step=0.5,
        value=float(existente["sleep_hours"]) if existente else 7.0,
    )
    mood = st.selectbox("Humor", MOOD_OPTIONS, index=mood_default)
    stress = st.slider(
        "Estresse (1–10)", 1, 10,
        int(existente["stress"]) if existente else 5,
    )
    notes = st.text_area(
        "Notas (opcional)",
        value=existente["notes"] if existente and existente["notes"] else "",
    )

    submit = st.form_submit_button("💾 Salvar check-in", use_container_width=True)

if submit:
    execute(
        """
        INSERT INTO daily_checkins
            (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy      = excluded.energy,
            sleep_hours = excluded.sleep_hours,
            mood        = excluded.mood,
            stress      = excluded.stress,
            notes       = excluded.notes
        """,
        (today_iso, energy, sleep_hours, mood, stress, notes or None),
    )
    st.success("[OK] Check-in registrado.")
    st.rerun()

st.divider()
st.subheader("🥋 Hábitos de hoje")

habits = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

alterou = False
for h in habits:
    novo = st.checkbox(
        f"**{h['pillar']}** · {h['name']}",
        value=bool(h["done"]),
        key=f"habit_{h['id']}",
    )
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done)
            VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """,
            (h["id"], today_iso, 1 if novo else 0),
        )
        alterou = True

if alterou:
    st.rerun()

st.divider()
st.subheader("🔥 Score Anti-Burnout (7 dias)")

score, metricas = calcular_burnout()
label, cor = classificar_burnout(score)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color:{cor};">
        <div class="titulo">Risco atual</div>
        <div class="valor" style="color:{cor};">{score:.0f}/100 — {label}</div>
        <div class="detalhe">
            Média energia: {metricas['avg_energy']:.1f} ·
            Sono: {metricas['avg_sleep']:.1f}h ·
            Estresse: {metricas['avg_stress']:.1f} ·
            Hábitos: {metricas['taxa']*100:.0f}%
        </div>
    </div>""",
    unsafe_allow_html=True,
)

st.progress(min(1.0, score / 100.0))

with st.expander("Como o score é calculado?"):
    st.markdown(
        """
- **Energia** (30 pts) — quanto menor, maior o risco.
- **Estresse** (30 pts) — quanto maior, maior o risco.
- **Sono** (20 pts) — abaixo de 8h aumenta o risco.
- **Aderência aos hábitos** (20 pts) — baixa execução nos últimos 7 dias eleva o risco.

**0–29:** 🟢 Baixo · **30–59:** 🟡 Médio · **60–79:** 🟠 Alto · **80–100:** 🔴 Crítico
        """
    )

if score >= 80:
    st.error("⚠️ Risco crítico. Priorize descanso hoje. Nenhum treino vale um colapso.")
elif score >= 60:
    st.warning("Atenção: sinais de sobrecarga. Reduza intensidade e priorize sono.")

```


## `ui/pages/__init__.py`

```python
"""Páginas do Projeto Samurai."""

```

```


## `requirements.txt`

```text
streamlit>=1.38.0
pandas>=2.2.0
yfinance>=0.2.40
requests>=2.31.0

```


## `services/__init__.py`

```python
"""Serviços externos (IA, yfinance, notícias, etc.)."""

```


## `ui/__init__.py`

```python
"""Camada de interface Streamlit."""

```


## `ui/pages/00_Home.py`

```python
"""Dojo — resumo do dia, hábitos pendentes e energia."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date

import streamlit as st

from core.database import query_all, query_one

today_iso = date.today().isoformat()

st.title("🏯 Dojo")
st.caption(f"Hoje é {date.today().strftime('%A, %d/%m/%Y')}")

checkin = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

col1, col2, col3 = st.columns(3)
if checkin:
    with col1:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Energia</div>
                <div class="valor">{checkin['energy']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Sono</div>
                <div class="valor">{checkin['sleep_hours']}h</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Estresse</div>
                <div class="valor">{checkin['stress']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("⚡ Nenhum check-in hoje. Vá em **Consistência** e registre sua energia.")

st.subheader("🎯 Hábitos pendentes hoje")

rows = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

pendentes = [r for r in rows if not r["done"]]
concluidos = [r for r in rows if r["done"]]

if not pendentes:
    st.success("🥋 Todos os hábitos foram cumpridos. Disciplina exemplar.")
else:
    for r in pendentes:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">{r['pillar']}</div>
                <div class="valor" style="font-size:1.1rem;">{r['name']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if concluidos:
    st.divider()
    st.caption(f"✅ {len(concluidos)} hábito(s) já cumprido(s) hoje")

st.divider()
if st.button("📝 Fazer check-in diário agora", use_container_width=True):
    st.switch_page("ui/pages/07_Consistencia.py")

```


## `ui/pages/01_Corpo.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()

```


## `ui/pages/02_Mente.py`

```python
import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db

init_db()  # Garante que as tabelas existam
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

# Busca o livro atual (pega o último atualizado)
livro = query_one("SELECT * FROM book_progress ORDER BY last_update DESC LIMIT 1")

col1, col2 = st.columns([2, 1])
with col1:
    if livro:
        st.markdown(f"**Livro atual:** {livro['book_title']}")
        
        # Calcula progresso
        pct = 0
        if livro['total_pages'] > 0:
            pct = min(1.0, livro['current_page'] / livro['total_pages'])
            
        st.progress(pct)
        st.caption(f"Página {livro['current_page']} de {livro['total_pages']} ({pct*100:.1f}%)")
    else:
        st.info("📖 Nenhum livro em andamento. Adicione um abaixo.")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Novo Livro", use_container_width=True):
        st.session_state["novo_livro"] = True

# Formulário para novo livro ou atualização
if not livro or st.session_state.get("novo_livro", False):
    with st.form("form_livro"):
        st.subheader("Adicionar Livro")
        titulo = st.text_input("Título do Livro")
        total_pag = st.number_input("Total de Páginas", min_value=1, value=100)
        
        if st.form_submit_button("Salvar Livro"):
            if titulo:
                execute(
                    """
                    INSERT INTO book_progress (book_title, total_pages) 
                    VALUES (?, ?)
                    ON CONFLICT(book_title) DO UPDATE SET total_pages = excluded.total_pages
                    """, (titulo, total_pag)
                )
                st.session_state["novo_livro"] = False
                st.rerun()
            else:
                st.error("O título é obrigatório.")

st.divider()
st.subheader("📖 Texto Exato do Dia")

# Área preparada para o futuro (Leitura PDF / IA)
st.info("Esta seção receberá o texto exato do dia gerado por IA nas próximas sprints.")
st.text_area("Seu resumo ou anotação da leitura de hoje:", placeholder="Digite aqui os insights do capítulo de hoje...")

if livro:
    st.divider()
    with st.form("form_progresso"):
        st.subheader("Atualizar Progresso")
        nova_pag = st.number_input("Página atual", min_value=0, max_value=int(livro['total_pages']), value=int(livro['current_page']))
        
        if st.form_submit_button("Atualizar Página", use_container_width=True):
            execute(
                "UPDATE book_progress SET current_page = ?, last_update = datetime('now') WHERE id = ?",
                (nova_pag, livro['id'])
            )
            st.rerun()

```


## `ui/pages/03_Informacao.py`

```python
import streamlit as st
st.title("📰 Informação")
st.info("🚧 Em construção — Sprint 2 trará notícias (Mundo, Brasil, RJ, Macaé), legislativo e finanças.")

```


## `ui/pages/04_Patrimonio.py`

```python
import streamlit as st
st.title("💎 Patrimônio")
st.info("🚧 Em construção — Sprint 2 trará cotações via yfinance, notícias por ticker e registro de gastos.")

```


## `ui/pages/05_Descanso.py`

```python
import streamlit as st
st.title("🌿 Descanso & Lazer")
st.info("🚧 Em construção — Sprint 2 trará sugestões semanais (Cartão Macaé + arredores).")

```


## `ui/pages/06_Autoconhecimento.py`

```python
import streamlit as st
st.title("🪞 Autoconhecimento")
st.info("🚧 Em construção — Sprint 2 trará diário reflexivo guiado por IA e meditações curtas.")

```


## `ui/pages/07_Consistencia.py`

```python
"""Consistência — check-in diário, marcação de hábitos e score anti-burnout."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date, timedelta

import streamlit as st

from core.database import execute, query_all, query_one

today = date.today()
today_iso = today.isoformat()


def calcular_burnout() -> tuple[float, dict]:
    """Score 0–100 (quanto maior, mais risco de burnout)."""
    week_ago = (today - timedelta(days=7)).isoformat()

    checkins = query_all(
        "SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?",
        (week_ago,),
    )
    total_habits = query_one("SELECT COUNT(*) AS c FROM habits WHERE active = 1")["c"] or 0
    logs = query_all(
        "SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,)
    )
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    total = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return total, {
        "avg_energy": avg_energy,
        "avg_stress": avg_stress,
        "avg_sleep": avg_sleep,
        "taxa": taxa,
    }


def classificar_burnout(score: float) -> tuple[str, str]:
    if score < 30:
        return "🟢 Baixo", "#2E7D32"
    if score < 60:
        return "🟡 Médio", "#F9A825"
    if score < 80:
        return "🟠 Alto", "#EF6C00"
    return "🔴 Crítico", "#C62828"


st.title("🎯 Consistência")
st.caption("Disciplina diária é o que forja o samurai.")

st.subheader("📝 Check-in do dia")

existente = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

MOOD_OPTIONS = ["Ótimo", "Bom", "Neutro", "Cansado", "Estressado", "Ansioso"]
mood_default = (
    MOOD_OPTIONS.index(existente["mood"])
    if existente and existente["mood"] in MOOD_OPTIONS
    else 2
)

with st.form("form_checkin", clear_on_submit=False):
    energy = st.slider(
        "Energia (1–10)", 1, 10,
        int(existente["energy"]) if existente else 6,
    )
    sleep_hours = st.number_input(
        "Horas de sono",
        min_value=0.0, max_value=16.0, step=0.5,
        value=float(existente["sleep_hours"]) if existente else 7.0,
    )
    mood = st.selectbox("Humor", MOOD_OPTIONS, index=mood_default)
    stress = st.slider(
        "Estresse (1–10)", 1, 10,
        int(existente["stress"]) if existente else 5,
    )
    notes = st.text_area(
        "Notas (opcional)",
        value=existente["notes"] if existente and existente["notes"] else "",
    )

    submit = st.form_submit_button("💾 Salvar check-in", use_container_width=True)

if submit:
    execute(
        """
        INSERT INTO daily_checkins
            (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy      = excluded.energy,
            sleep_hours = excluded.sleep_hours,
            mood        = excluded.mood,
            stress      = excluded.stress,
            notes       = excluded.notes
        """,
        (today_iso, energy, sleep_hours, mood, stress, notes or None),
    )
    st.success("[OK] Check-in registrado.")
    st.rerun()

st.divider()
st.subheader("🥋 Hábitos de hoje")

habits = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

alterou = False
for h in habits:
    novo = st.checkbox(
        f"**{h['pillar']}** · {h['name']}",
        value=bool(h["done"]),
        key=f"habit_{h['id']}",
    )
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done)
            VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """,
            (h["id"], today_iso, 1 if novo else 0),
        )
        alterou = True

if alterou:
    st.rerun()

st.divider()
st.subheader("🔥 Score Anti-Burnout (7 dias)")

score, metricas = calcular_burnout()
label, cor = classificar_burnout(score)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color:{cor};">
        <div class="titulo">Risco atual</div>
        <div class="valor" style="color:{cor};">{score:.0f}/100 — {label}</div>
        <div class="detalhe">
            Média energia: {metricas['avg_energy']:.1f} ·
            Sono: {metricas['avg_sleep']:.1f}h ·
            Estresse: {metricas['avg_stress']:.1f} ·
            Hábitos: {metricas['taxa']*100:.0f}%
        </div>
    </div>""",
    unsafe_allow_html=True,
)

st.progress(min(1.0, score / 100.0))

with st.expander("Como o score é calculado?"):
    st.markdown(
        """
- **Energia** (30 pts) — quanto menor, maior o risco.
- **Estresse** (30 pts) — quanto maior, maior o risco.
- **Sono** (20 pts) — abaixo de 8h aumenta o risco.
- **Aderência aos hábitos** (20 pts) — baixa execução nos últimos 7 dias eleva o risco.

**0–29:** 🟢 Baixo · **30–59:** 🟡 Médio · **60–79:** 🟠 Alto · **80–100:** 🔴 Crítico
        """
    )

if score >= 80:
    st.error("⚠️ Risco crítico. Priorize descanso hoje. Nenhum treino vale um colapso.")
elif score >= 60:
    st.warning("Atenção: sinais de sobrecarga. Reduza intensidade e priorize sono.")

```


## `ui/pages/__init__.py`

```python
"""Páginas do Projeto Samurai."""

```

```


## `requirements.txt`

```text
streamlit>=1.38.0
pandas>=2.2.0
yfinance>=0.2.40
requests>=2.31.0

```


## `services/__init__.py`

```python
"""Serviços externos (IA, yfinance, notícias, etc.)."""

```


## `ui/__init__.py`

```python
"""Camada de interface Streamlit."""

```


## `ui/pages/00_Home.py`

```python
"""Dojo — resumo do dia, hábitos pendentes e energia."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date

import streamlit as st

from core.database import query_all, query_one

today_iso = date.today().isoformat()

st.title("🏯 Dojo")
st.caption(f"Hoje é {date.today().strftime('%A, %d/%m/%Y')}")

checkin = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

col1, col2, col3 = st.columns(3)
if checkin:
    with col1:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Energia</div>
                <div class="valor">{checkin['energy']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Sono</div>
                <div class="valor">{checkin['sleep_hours']}h</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Estresse</div>
                <div class="valor">{checkin['stress']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("⚡ Nenhum check-in hoje. Vá em **Consistência** e registre sua energia.")

st.subheader("🎯 Hábitos pendentes hoje")

rows = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

pendentes = [r for r in rows if not r["done"]]
concluidos = [r for r in rows if r["done"]]

if not pendentes:
    st.success("🥋 Todos os hábitos foram cumpridos. Disciplina exemplar.")
else:
    for r in pendentes:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">{r['pillar']}</div>
                <div class="valor" style="font-size:1.1rem;">{r['name']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if concluidos:
    st.divider()
    st.caption(f"✅ {len(concluidos)} hábito(s) já cumprido(s) hoje")

st.divider()
if st.button("📝 Fazer check-in diário agora", use_container_width=True):
    st.switch_page("ui/pages/07_Consistencia.py")

```


## `ui/pages/01_Corpo.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()

```


## `ui/pages/02_Mente.py`

```python
import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db

init_db()  # Garante que as tabelas existam
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

# Busca o livro atual (pega o último atualizado)
livro = query_one("SELECT * FROM book_progress ORDER BY last_update DESC LIMIT 1")

col1, col2 = st.columns([2, 1])
with col1:
    if livro:
        st.markdown(f"**Livro atual:** {livro['book_title']}")
        
        # Calcula progresso
        pct = 0
        if livro['total_pages'] > 0:
            pct = min(1.0, livro['current_page'] / livro['total_pages'])
            
        st.progress(pct)
        st.caption(f"Página {livro['current_page']} de {livro['total_pages']} ({pct*100:.1f}%)")
    else:
        st.info("📖 Nenhum livro em andamento. Adicione um abaixo.")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Novo Livro", use_container_width=True):
        st.session_state["novo_livro"] = True

# Formulário para novo livro ou atualização
if not livro or st.session_state.get("novo_livro", False):
    with st.form("form_livro"):
        st.subheader("Adicionar Livro")
        titulo = st.text_input("Título do Livro")
        total_pag = st.number_input("Total de Páginas", min_value=1, value=100)
        
        if st.form_submit_button("Salvar Livro"):
            if titulo:
                execute(
                    """
                    INSERT INTO book_progress (book_title, total_pages) 
                    VALUES (?, ?)
                    ON CONFLICT(book_title) DO UPDATE SET total_pages = excluded.total_pages
                    """, (titulo, total_pag)
                )
                st.session_state["novo_livro"] = False
                st.rerun()
            else:
                st.error("O título é obrigatório.")

st.divider()
st.subheader("📖 Texto Exato do Dia")

# Área preparada para o futuro (Leitura PDF / IA)
st.info("Esta seção receberá o texto exato do dia gerado por IA nas próximas sprints.")
st.text_area("Seu resumo ou anotação da leitura de hoje:", placeholder="Digite aqui os insights do capítulo de hoje...")

if livro:
    st.divider()
    with st.form("form_progresso"):
        st.subheader("Atualizar Progresso")
        nova_pag = st.number_input("Página atual", min_value=0, max_value=int(livro['total_pages']), value=int(livro['current_page']))
        
        if st.form_submit_button("Atualizar Página", use_container_width=True):
            execute(
                "UPDATE book_progress SET current_page = ?, last_update = datetime('now') WHERE id = ?",
                (nova_pag, livro['id'])
            )
            st.rerun()

```


## `ui/pages/03_Informacao.py`

```python
import streamlit as st
import sys
from pathlib import Path
import yfinance as yf
import urllib.request
import xml.etree.ElementTree as ET

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db

init_db()

st.title("📰 Informação")
st.caption("Mundo, Brasil, Macaé, Legislativo e Finanças.")

# --- FINANÇAS ---
st.subheader("📈 Finanças (Tempo Real)")
col1, col2, col3 = st.columns(3)
tickers = {"Dólar": "BRL=X", "IBOVESPA": "^BVSP", "Bitcoin": "BTC-USD"}
cols = [col1, col2, col3]

for i, (nome, ticker) in enumerate(tickers.items()):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            preco = data['Close'].iloc[-1]
            with cols[i]:
                st.markdown(
                    f"""<div class="samurai-card">
                        <div class="titulo">{nome}</div>
                        <div class="valor">R$ {preco:,.2f}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    except Exception:
        with cols[i]:
            st.error(f"Erro ao carregar {nome}")

st.divider()

# --- NOTÍCIAS ---
st.subheader("🗞️ Últimas Notícias (G1)")
try:
    url = "https://g1.globo.com/rss/g1/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    tree = ET.fromstring(response.read())
    
    for item in tree.findall('.//item')[:5]:
        title = item.find('title').text
        link = item.find('link').text
        st.markdown(f"- [{title}]({link})")
except Exception as e:
    st.warning("Não foi possível carregar as notícias no momento (verifique a conexão).")

st.divider()
st.subheader("⚖️ Legislativo")
st.info("🚧 Integração com APIs do Senado, Câmara, ALERJ e Câmara de Macaé será implementada na Sprint 4.")

```


## `ui/pages/04_Patrimonio.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("💎 Patrimônio")
st.caption("Ações, notícias e controle de gastos.")

# --- AÇÕES ---
st.subheader("📊 Ações e FIIs")
col1, col2 = st.columns([2, 1])
with col1:
    ticker_input = st.text_input("Digite o ticker (ex: PETR4.SA, VALE3.SA, HGLG11.SA):", value="PETR4.SA")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    buscar = st.button("Buscar Cotação", use_container_width=True)

if buscar or ticker_input:
    try:
        ticker = yf.Ticker(ticker_input)
        data = ticker.history(period="5d")
        if not data.empty:
            preco_atual = data['Close'].iloc[-1]
            variacao = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
            
            cor = "#4CAF50" if variacao >= 0 else "#F44336"
            
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: {cor};">
                    <div class="titulo">{ticker_input}</div>
                    <div class="valor">R$ {preco_atual:.2f}</div>
                    <div class="detalhe" style="color: {cor};">Variação (5d): {variacao:+.2f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )
            
            with st.expander("Ver Notícias do Ticker"):
                noticias = ticker.news
                if noticias:
                    for n in noticias[:3]:
                        st.markdown(f"- [{n['title']}]({n['link']})")
                else:
                    st.write("Nenhuma notícia recente encontrada.")
        else:
            st.error("Ticker não encontrado ou sem dados.")
    except Exception:
        st.error("Erro ao buscar dados. Verifique o ticker digitado.")

st.divider()

# --- GASTOS ---
st.subheader("💸 Registro de Gastos")

with st.form("form_gasto"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        descricao = st.text_input("Descrição")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
    with col3:
        categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Outros"])
    
    submitted = st.form_submit_button("Registrar Gasto", use_container_width=True)

if submitted:
    if descricao and valor > 0:
        execute(
            "INSERT INTO expenses (expense_date, description, amount, category) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), descricao, valor, categoria)
        )
        st.success("Gasto registrado!")
        st.rerun()
    else:
        st.error("Preencha a descrição e um valor maior que zero.")

# Listar gastos
gastos = query_all("SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 10")
if gastos:
    st.markdown("### Últimos Gastos")
    for g in gastos:
        st.markdown(
            f"""<div class="samurai-card" style="border-left-color: #171717; padding: 10px;">
                <div style="display: flex; justify-content: space-between; color: #CCC;">
                    <span>{g['description']}</span>
                    <span>R$ {g['amount']:.2f} ({g['category']})</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

```


## `ui/pages/05_Descanso.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

st.title("🌿 Descanso & Lazer")
st.caption("Sugestões semanais para recarregar as energias.")

# Pegar a semana do ano para alternar as sugestões
semana_ano = date.today().isocalendar()[1]

MACAÉ = [
    {"local": "Praia dos Cavaleiros", "dica": "Caminhada na orla e um açaí no fim da tarde."},
    {"local": "Lagoa de Imboassica", "dica": "Passeio de caiaque ou pedalinho, ótimo para desacelerar."},
    {"local": "Pico do Frade", "dica": "Trilha leve com vista panorâmica da cidade. Leve água."},
    {"local": "Praia do Pecado", "dica": "Lugar mais reservado para ler um livro e relaxar."},
    {"local": "Parque Municipal da Lagoa", "dica": "Caminhada e contato com a natureza."},
]

ARREDORES = [
    {"local": "Búzios - Rua das Pedras", "dica": "Almoço, caminhada e fim de tarde na praia de Geribá."},
    {"local": "Cabo Frio - Praia do Forte", "dica": "Visitar as dunas e a Fortaleza de São Mateus."},
    {"local": "Arraial do Cabo - Pontal do Atalaia", "dica": "Levar água e preparar para o visual mais bonito da região."},
    {"local": "Lumiar (Nova Friburgo)", "dica": "Pousada, cachoeiras e gastronomia mineira."},
    {"local": "Rio das Ostras - Costazul", "dica": "Feira de artesanato e passeio na lagoa."},
]

sugestao_macae = MACAÉ[semana_ano % len(MACAÉ)]
sugestao_arredores = ARREDORES[semana_ano % len(ARREDORES)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão em Macaé</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_macae['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_macae['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão nos Arredores</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_arredores['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_arredores['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.info("💡 Lembre-se de usar o **Cartão Macaé** nos estabelecimentos parceiros da cidade.")

```


## `ui/pages/06_Autoconhecimento.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("🪞 Autoconhecimento")
st.caption("Diário reflexivo e meditação.")

PROMPTS = [
    "O que drenou minha energia hoje e por quê?",
    "Qual pequena vitória eu tive hoje?",
    "O que eu faria diferente se pudesse recomeçar o dia?",
    "Pelo que sou grato neste exato momento?",
    "Qual pensamento negativo eu posso deixar ir embora?",
    "Como eu tratei as pessoas ao meu redor hoje?",
    "O que aprendi sobre mim mesmo nesta semana?",
]

# Define o prompt do dia baseado no dia do ano (para ser consistente durante o dia)
prompt_do_dia = PROMPTS[date.today().toordinal() % len(PROMPTS)]

st.subheader("📝 Diário Reflexivo")
st.markdown(f"**Prompt de hoje:** *{prompt_do_dia}*")

with st.form("form_journal"):
    texto = st.text_area("Sua reflexão:", height=150, placeholder="Escreva livremente...")
    submitted = st.form_submit_button("Salvar no Diário", use_container_width=True)

if submitted and texto.strip():
    execute(
        "INSERT INTO journal_entries (entry_date, prompt, content) VALUES (?, ?, ?)",
        (date.today().isoformat(), prompt_do_dia, texto.strip())
    )
    st.success("Reflexão salva.")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Meditação Curta")
st.markdown("""
**Respiração Box (5 minutos):**
1. Inspire contando até **4**.
2. Segure a respiração contando até **4**.
3. Expire lentamente contando até **4**.
4. Aguarde contando até **4**.
5. Repita por 5 minutos.
""")

st.divider()
st.subheader("📚 Histórico de Reflexões")

entries = query_all("SELECT * FROM journal_entries ORDER BY entry_date DESC, id DESC LIMIT 5")
if not entries:
    st.info("Nenhuma reflexão registrada ainda.")
else:
    for e in entries:
        with st.expander(f"📅 {e['entry_date']} — {e['prompt']}"):
            st.write(e['content'])

```


## `ui/pages/07_Consistencia.py`

```python
"""Consistência — check-in diário, marcação de hábitos e score anti-burnout."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date, timedelta

import streamlit as st

from core.database import execute, query_all, query_one

today = date.today()
today_iso = today.isoformat()


def calcular_burnout() -> tuple[float, dict]:
    """Score 0–100 (quanto maior, mais risco de burnout)."""
    week_ago = (today - timedelta(days=7)).isoformat()

    checkins = query_all(
        "SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?",
        (week_ago,),
    )
    total_habits = query_one("SELECT COUNT(*) AS c FROM habits WHERE active = 1")["c"] or 0
    logs = query_all(
        "SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,)
    )
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    total = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return total, {
        "avg_energy": avg_energy,
        "avg_stress": avg_stress,
        "avg_sleep": avg_sleep,
        "taxa": taxa,
    }


def classificar_burnout(score: float) -> tuple[str, str]:
    if score < 30:
        return "🟢 Baixo", "#2E7D32"
    if score < 60:
        return "🟡 Médio", "#F9A825"
    if score < 80:
        return "🟠 Alto", "#EF6C00"
    return "🔴 Crítico", "#C62828"


st.title("🎯 Consistência")
st.caption("Disciplina diária é o que forja o samurai.")

st.subheader("📝 Check-in do dia")

existente = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

MOOD_OPTIONS = ["Ótimo", "Bom", "Neutro", "Cansado", "Estressado", "Ansioso"]
mood_default = (
    MOOD_OPTIONS.index(existente["mood"])
    if existente and existente["mood"] in MOOD_OPTIONS
    else 2
)

with st.form("form_checkin", clear_on_submit=False):
    energy = st.slider(
        "Energia (1–10)", 1, 10,
        int(existente["energy"]) if existente else 6,
    )
    sleep_hours = st.number_input(
        "Horas de sono",
        min_value=0.0, max_value=16.0, step=0.5,
        value=float(existente["sleep_hours"]) if existente else 7.0,
    )
    mood = st.selectbox("Humor", MOOD_OPTIONS, index=mood_default)
    stress = st.slider(
        "Estresse (1–10)", 1, 10,
        int(existente["stress"]) if existente else 5,
    )
    notes = st.text_area(
        "Notas (opcional)",
        value=existente["notes"] if existente and existente["notes"] else "",
    )

    submit = st.form_submit_button("💾 Salvar check-in", use_container_width=True)

if submit:
    execute(
        """
        INSERT INTO daily_checkins
            (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy      = excluded.energy,
            sleep_hours = excluded.sleep_hours,
            mood        = excluded.mood,
            stress      = excluded.stress,
            notes       = excluded.notes
        """,
        (today_iso, energy, sleep_hours, mood, stress, notes or None),
    )
    st.success("[OK] Check-in registrado.")
    st.rerun()

st.divider()
st.subheader("🥋 Hábitos de hoje")

habits = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

alterou = False
for h in habits:
    novo = st.checkbox(
        f"**{h['pillar']}** · {h['name']}",
        value=bool(h["done"]),
        key=f"habit_{h['id']}",
    )
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done)
            VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """,
            (h["id"], today_iso, 1 if novo else 0),
        )
        alterou = True

if alterou:
    st.rerun()

st.divider()
st.subheader("🔥 Score Anti-Burnout (7 dias)")

score, metricas = calcular_burnout()
label, cor = classificar_burnout(score)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color:{cor};">
        <div class="titulo">Risco atual</div>
        <div class="valor" style="color:{cor};">{score:.0f}/100 — {label}</div>
        <div class="detalhe">
            Média energia: {metricas['avg_energy']:.1f} ·
            Sono: {metricas['avg_sleep']:.1f}h ·
            Estresse: {metricas['avg_stress']:.1f} ·
            Hábitos: {metricas['taxa']*100:.0f}%
        </div>
    </div>""",
    unsafe_allow_html=True,
)

st.progress(min(1.0, score / 100.0))

with st.expander("Como o score é calculado?"):
    st.markdown(
        """
- **Energia** (30 pts) — quanto menor, maior o risco.
- **Estresse** (30 pts) — quanto maior, maior o risco.
- **Sono** (20 pts) — abaixo de 8h aumenta o risco.
- **Aderência aos hábitos** (20 pts) — baixa execução nos últimos 7 dias eleva o risco.

**0–29:** 🟢 Baixo · **30–59:** 🟡 Médio · **60–79:** 🟠 Alto · **80–100:** 🔴 Crítico
        """
    )

if score >= 80:
    st.error("⚠️ Risco crítico. Priorize descanso hoje. Nenhum treino vale um colapso.")
elif score >= 60:
    st.warning("Atenção: sinais de sobrecarga. Reduza intensidade e priorize sono.")

```


## `ui/pages/__init__.py`

```python
"""Páginas do Projeto Samurai."""

```

```


## `requirements.txt`

```text
streamlit>=1.38.0
pandas>=2.2.0
yfinance>=0.2.40
requests>=2.31.0
feedparser>=6.0.10

```


## `services/__init__.py`

```python
"""Serviços externos (IA, yfinance, notícias, etc.)."""

```


## `ui/__init__.py`

```python
"""Camada de interface Streamlit."""

```


## `ui/pages/00_Home.py`

```python
"""Dojo — resumo do dia, hábitos pendentes e energia."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date

import streamlit as st

from core.database import query_all, query_one

today_iso = date.today().isoformat()

st.title("🏯 Dojo")
st.caption(f"Hoje é {date.today().strftime('%A, %d/%m/%Y')}")

checkin = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

col1, col2, col3 = st.columns(3)
if checkin:
    with col1:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Energia</div>
                <div class="valor">{checkin['energy']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Sono</div>
                <div class="valor">{checkin['sleep_hours']}h</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Estresse</div>
                <div class="valor">{checkin['stress']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("⚡ Nenhum check-in hoje. Vá em **Consistência** e registre sua energia.")

st.subheader("🎯 Hábitos pendentes hoje")

rows = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

pendentes = [r for r in rows if not r["done"]]
concluidos = [r for r in rows if r["done"]]

if not pendentes:
    st.success("🥋 Todos os hábitos foram cumpridos. Disciplina exemplar.")
else:
    for r in pendentes:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">{r['pillar']}</div>
                <div class="valor" style="font-size:1.1rem;">{r['name']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if concluidos:
    st.divider()
    st.caption(f"✅ {len(concluidos)} hábito(s) já cumprido(s) hoje")

st.divider()
if st.button("📝 Fazer check-in diário agora", use_container_width=True):
    st.switch_page("ui/pages/07_Consistencia.py")

```


## `ui/pages/01_Corpo.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()

```


## `ui/pages/02_Mente.py`

```python
import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db

init_db()  # Garante que as tabelas existam
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

# Busca o livro atual (pega o último atualizado)
livro = query_one("SELECT * FROM book_progress ORDER BY last_update DESC LIMIT 1")

col1, col2 = st.columns([2, 1])
with col1:
    if livro:
        st.markdown(f"**Livro atual:** {livro['book_title']}")
        
        # Calcula progresso
        pct = 0
        if livro['total_pages'] > 0:
            pct = min(1.0, livro['current_page'] / livro['total_pages'])
            
        st.progress(pct)
        st.caption(f"Página {livro['current_page']} de {livro['total_pages']} ({pct*100:.1f}%)")
    else:
        st.info("📖 Nenhum livro em andamento. Adicione um abaixo.")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Novo Livro", use_container_width=True):
        st.session_state["novo_livro"] = True

# Formulário para novo livro ou atualização
if not livro or st.session_state.get("novo_livro", False):
    with st.form("form_livro"):
        st.subheader("Adicionar Livro")
        titulo = st.text_input("Título do Livro")
        total_pag = st.number_input("Total de Páginas", min_value=1, value=100)
        
        if st.form_submit_button("Salvar Livro"):
            if titulo:
                execute(
                    """
                    INSERT INTO book_progress (book_title, total_pages) 
                    VALUES (?, ?)
                    ON CONFLICT(book_title) DO UPDATE SET total_pages = excluded.total_pages
                    """, (titulo, total_pag)
                )
                st.session_state["novo_livro"] = False
                st.rerun()
            else:
                st.error("O título é obrigatório.")

st.divider()
st.subheader("📖 Texto Exato do Dia")

# Área preparada para o futuro (Leitura PDF / IA)
st.info("Esta seção receberá o texto exato do dia gerado por IA nas próximas sprints.")
st.text_area("Seu resumo ou anotação da leitura de hoje:", placeholder="Digite aqui os insights do capítulo de hoje...")

if livro:
    st.divider()
    with st.form("form_progresso"):
        st.subheader("Atualizar Progresso")
        nova_pag = st.number_input("Página atual", min_value=0, max_value=int(livro['total_pages']), value=int(livro['current_page']))
        
        if st.form_submit_button("Atualizar Página", use_container_width=True):
            execute(
                "UPDATE book_progress SET current_page = ?, last_update = datetime('now') WHERE id = ?",
                (nova_pag, livro['id'])
            )
            st.rerun()

```


## `ui/pages/03_Informacao.py`

```python
import streamlit as st
import sys
from pathlib import Path
import yfinance as yf
import requests
import feedparser

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db

init_db()

st.title("📰 Informação")
st.caption("Mundo, Brasil, Macaé, Legislativo e Finanças.")

# --- FINANÇAS ---
st.subheader("📈 Finanças (Tempo Real)")
col1, col2, col3 = st.columns(3)
tickers = {"Dólar": "BRL=X", "IBOVESPA": "^BVSP", "Bitcoin": "BTC-USD"}
cols = [col1, col2, col3]

for i, (nome, ticker) in enumerate(tickers.items()):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            preco = data['Close'].iloc[-1]
            with cols[i]:
                st.markdown(
                    f"""<div class="samurai-card">
                        <div class="titulo">{nome}</div>
                        <div class="valor">R$ {preco:,.2f}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    except Exception:
        with cols[i]:
            st.error(f"Erro ao carregar {nome}")

st.divider()

# --- NOTÍCIAS ---
st.subheader("🗞️ Últimas Notícias (G1)")
try:
    url = "https://g1.globo.com/rss/g1/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() # Levanta um erro se a requisição falhar
    
    feed = feedparser.parse(response.content)
    
    if feed.entries:
        for entry in feed.entries[:5]:
            st.markdown(f"- [{entry.title}]({entry.link})")
    else:
        st.warning("O feed de notícias está vazio no momento.")
except requests.exceptions.RequestException:
    st.warning("Não foi possível carregar as notícias (servidor do G1 fora do ar ou bloqueando a conexão).")
except Exception as e:
    st.warning("Erro inesperado ao carregar as notícias.")

st.divider()
st.subheader("⚖️ Legislativo")
st.info("🚧 Integração com APIs do Senado, Câmara, ALERJ e Câmara de Macaé será implementada na Sprint 4.")

```


## `ui/pages/04_Patrimonio.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("💎 Patrimônio")
st.caption("Ações, notícias e controle de gastos.")

# --- AÇÕES ---
st.subheader("📊 Ações e FIIs")
col1, col2 = st.columns([2, 1])
with col1:
    ticker_input = st.text_input("Digite o ticker (ex: PETR4.SA, VALE3.SA, HGLG11.SA):", value="PETR4.SA")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    buscar = st.button("Buscar Cotação", use_container_width=True)

if buscar or ticker_input:
    try:
        ticker = yf.Ticker(ticker_input)
        data = ticker.history(period="5d")
        if not data.empty:
            preco_atual = data['Close'].iloc[-1]
            variacao = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
            
            cor = "#4CAF50" if variacao >= 0 else "#F44336"
            
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: {cor};">
                    <div class="titulo">{ticker_input}</div>
                    <div class="valor">R$ {preco_atual:.2f}</div>
                    <div class="detalhe" style="color: {cor};">Variação (5d): {variacao:+.2f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )
            
            with st.expander("Ver Notícias do Ticker"):
                noticias = ticker.news
                if noticias:
                    for n in noticias[:3]:
                        st.markdown(f"- [{n['title']}]({n['link']})")
                else:
                    st.write("Nenhuma notícia recente encontrada.")
        else:
            st.error("Ticker não encontrado ou sem dados.")
    except Exception:
        st.error("Erro ao buscar dados. Verifique o ticker digitado.")

st.divider()

# --- GASTOS ---
st.subheader("💸 Registro de Gastos")

with st.form("form_gasto"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        descricao = st.text_input("Descrição")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
    with col3:
        categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Outros"])
    
    submitted = st.form_submit_button("Registrar Gasto", use_container_width=True)

if submitted:
    if descricao and valor > 0:
        execute(
            "INSERT INTO expenses (expense_date, description, amount, category) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), descricao, valor, categoria)
        )
        st.success("Gasto registrado!")
        st.rerun()
    else:
        st.error("Preencha a descrição e um valor maior que zero.")

# Listar gastos
gastos = query_all("SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 10")
if gastos:
    st.markdown("### Últimos Gastos")
    for g in gastos:
        st.markdown(
            f"""<div class="samurai-card" style="border-left-color: #171717; padding: 10px;">
                <div style="display: flex; justify-content: space-between; color: #CCC;">
                    <span>{g['description']}</span>
                    <span>R$ {g['amount']:.2f} ({g['category']})</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

```


## `ui/pages/05_Descanso.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

st.title("🌿 Descanso & Lazer")
st.caption("Sugestões semanais para recarregar as energias.")

# Pegar a semana do ano para alternar as sugestões
semana_ano = date.today().isocalendar()[1]

MACAÉ = [
    {"local": "Praia dos Cavaleiros", "dica": "Caminhada na orla e um açaí no fim da tarde."},
    {"local": "Lagoa de Imboassica", "dica": "Passeio de caiaque ou pedalinho, ótimo para desacelerar."},
    {"local": "Pico do Frade", "dica": "Trilha leve com vista panorâmica da cidade. Leve água."},
    {"local": "Praia do Pecado", "dica": "Lugar mais reservado para ler um livro e relaxar."},
    {"local": "Parque Municipal da Lagoa", "dica": "Caminhada e contato com a natureza."},
]

ARREDORES = [
    {"local": "Búzios - Rua das Pedras", "dica": "Almoço, caminhada e fim de tarde na praia de Geribá."},
    {"local": "Cabo Frio - Praia do Forte", "dica": "Visitar as dunas e a Fortaleza de São Mateus."},
    {"local": "Arraial do Cabo - Pontal do Atalaia", "dica": "Levar água e preparar para o visual mais bonito da região."},
    {"local": "Lumiar (Nova Friburgo)", "dica": "Pousada, cachoeiras e gastronomia mineira."},
    {"local": "Rio das Ostras - Costazul", "dica": "Feira de artesanato e passeio na lagoa."},
]

sugestao_macae = MACAÉ[semana_ano % len(MACAÉ)]
sugestao_arredores = ARREDORES[semana_ano % len(ARREDORES)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão em Macaé</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_macae['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_macae['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão nos Arredores</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_arredores['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_arredores['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.info("💡 Lembre-se de usar o **Cartão Macaé** nos estabelecimentos parceiros da cidade.")

```


## `ui/pages/06_Autoconhecimento.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("🪞 Autoconhecimento")
st.caption("Diário reflexivo e meditação.")

PROMPTS = [
    "O que drenou minha energia hoje e por quê?",
    "Qual pequena vitória eu tive hoje?",
    "O que eu faria diferente se pudesse recomeçar o dia?",
    "Pelo que sou grato neste exato momento?",
    "Qual pensamento negativo eu posso deixar ir embora?",
    "Como eu tratei as pessoas ao meu redor hoje?",
    "O que aprendi sobre mim mesmo nesta semana?",
]

# Define o prompt do dia baseado no dia do ano (para ser consistente durante o dia)
prompt_do_dia = PROMPTS[date.today().toordinal() % len(PROMPTS)]

st.subheader("📝 Diário Reflexivo")
st.markdown(f"**Prompt de hoje:** *{prompt_do_dia}*")

with st.form("form_journal"):
    texto = st.text_area("Sua reflexão:", height=150, placeholder="Escreva livremente...")
    submitted = st.form_submit_button("Salvar no Diário", use_container_width=True)

if submitted and texto.strip():
    execute(
        "INSERT INTO journal_entries (entry_date, prompt, content) VALUES (?, ?, ?)",
        (date.today().isoformat(), prompt_do_dia, texto.strip())
    )
    st.success("Reflexão salva.")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Meditação Curta")
st.markdown("""
**Respiração Box (5 minutos):**
1. Inspire contando até **4**.
2. Segure a respiração contando até **4**.
3. Expire lentamente contando até **4**.
4. Aguarde contando até **4**.
5. Repita por 5 minutos.
""")

st.divider()
st.subheader("📚 Histórico de Reflexões")

entries = query_all("SELECT * FROM journal_entries ORDER BY entry_date DESC, id DESC LIMIT 5")
if not entries:
    st.info("Nenhuma reflexão registrada ainda.")
else:
    for e in entries:
        with st.expander(f"📅 {e['entry_date']} — {e['prompt']}"):
            st.write(e['content'])

```


## `ui/pages/07_Consistencia.py`

```python
"""Consistência — check-in diário, marcação de hábitos e score anti-burnout."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date, timedelta

import streamlit as st

from core.database import execute, query_all, query_one

today = date.today()
today_iso = today.isoformat()


def calcular_burnout() -> tuple[float, dict]:
    """Score 0–100 (quanto maior, mais risco de burnout)."""
    week_ago = (today - timedelta(days=7)).isoformat()

    checkins = query_all(
        "SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?",
        (week_ago,),
    )
    total_habits = query_one("SELECT COUNT(*) AS c FROM habits WHERE active = 1")["c"] or 0
    logs = query_all(
        "SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,)
    )
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    total = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return total, {
        "avg_energy": avg_energy,
        "avg_stress": avg_stress,
        "avg_sleep": avg_sleep,
        "taxa": taxa,
    }


def classificar_burnout(score: float) -> tuple[str, str]:
    if score < 30:
        return "🟢 Baixo", "#2E7D32"
    if score < 60:
        return "🟡 Médio", "#F9A825"
    if score < 80:
        return "🟠 Alto", "#EF6C00"
    return "🔴 Crítico", "#C62828"


st.title("🎯 Consistência")
st.caption("Disciplina diária é o que forja o samurai.")

st.subheader("📝 Check-in do dia")

existente = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

MOOD_OPTIONS = ["Ótimo", "Bom", "Neutro", "Cansado", "Estressado", "Ansioso"]
mood_default = (
    MOOD_OPTIONS.index(existente["mood"])
    if existente and existente["mood"] in MOOD_OPTIONS
    else 2
)

with st.form("form_checkin", clear_on_submit=False):
    energy = st.slider(
        "Energia (1–10)", 1, 10,
        int(existente["energy"]) if existente else 6,
    )
    sleep_hours = st.number_input(
        "Horas de sono",
        min_value=0.0, max_value=16.0, step=0.5,
        value=float(existente["sleep_hours"]) if existente else 7.0,
    )
    mood = st.selectbox("Humor", MOOD_OPTIONS, index=mood_default)
    stress = st.slider(
        "Estresse (1–10)", 1, 10,
        int(existente["stress"]) if existente else 5,
    )
    notes = st.text_area(
        "Notas (opcional)",
        value=existente["notes"] if existente and existente["notes"] else "",
    )

    submit = st.form_submit_button("💾 Salvar check-in", use_container_width=True)

if submit:
    execute(
        """
        INSERT INTO daily_checkins
            (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy      = excluded.energy,
            sleep_hours = excluded.sleep_hours,
            mood        = excluded.mood,
            stress      = excluded.stress,
            notes       = excluded.notes
        """,
        (today_iso, energy, sleep_hours, mood, stress, notes or None),
    )
    st.success("[OK] Check-in registrado.")
    st.rerun()

st.divider()
st.subheader("🥋 Hábitos de hoje")

habits = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

alterou = False
for h in habits:
    novo = st.checkbox(
        f"**{h['pillar']}** · {h['name']}",
        value=bool(h["done"]),
        key=f"habit_{h['id']}",
    )
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done)
            VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """,
            (h["id"], today_iso, 1 if novo else 0),
        )
        alterou = True

if alterou:
    st.rerun()

st.divider()
st.subheader("🔥 Score Anti-Burnout (7 dias)")

score, metricas = calcular_burnout()
label, cor = classificar_burnout(score)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color:{cor};">
        <div class="titulo">Risco atual</div>
        <div class="valor" style="color:{cor};">{score:.0f}/100 — {label}</div>
        <div class="detalhe">
            Média energia: {metricas['avg_energy']:.1f} ·
            Sono: {metricas['avg_sleep']:.1f}h ·
            Estresse: {metricas['avg_stress']:.1f} ·
            Hábitos: {metricas['taxa']*100:.0f}%
        </div>
    </div>""",
    unsafe_allow_html=True,
)

st.progress(min(1.0, score / 100.0))

with st.expander("Como o score é calculado?"):
    st.markdown(
        """
- **Energia** (30 pts) — quanto menor, maior o risco.
- **Estresse** (30 pts) — quanto maior, maior o risco.
- **Sono** (20 pts) — abaixo de 8h aumenta o risco.
- **Aderência aos hábitos** (20 pts) — baixa execução nos últimos 7 dias eleva o risco.

**0–29:** 🟢 Baixo · **30–59:** 🟡 Médio · **60–79:** 🟠 Alto · **80–100:** 🔴 Crítico
        """
    )

if score >= 80:
    st.error("⚠️ Risco crítico. Priorize descanso hoje. Nenhum treino vale um colapso.")
elif score >= 60:
    st.warning("Atenção: sinais de sobrecarga. Reduza intensidade e priorize sono.")

```


## `ui/pages/__init__.py`

```python
"""Páginas do Projeto Samurai."""

```

```


## `requirements.txt`

```text
streamlit>=1.38.0
pandas>=2.2.0
yfinance>=0.2.40
requests>=2.31.0
feedparser>=6.0.10
google-generativeai>=0.5.0

```


## `services/__init__.py`

```python
"""Serviços externos (IA, yfinance, notícias, etc.)."""

```


## `services/ai.py`

```python
import google.generativeai as genai
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

def get_api_key() -> str:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("gemini_api_key", "")
        except Exception:
            pass
    return ""

def ask_gemini(prompt: str) -> str:
    api_key = get_api_key()
    if not api_key or api_key == "COLE_SUA_CHAVE_AQUI":
        return "⚠️ API Key não configurada. Abra o arquivo 'config.json' na raiz do projeto e insira sua chave do Gemini."
    
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Erro na IA: {str(e)}"

```


## `ui/__init__.py`

```python
"""Camada de interface Streamlit."""

```


## `ui/pages/00_Home.py`

```python
"""Dojo — resumo do dia, hábitos pendentes e energia."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date

import streamlit as st

from core.database import query_all, query_one

today_iso = date.today().isoformat()

st.title("🏯 Dojo")
st.caption(f"Hoje é {date.today().strftime('%A, %d/%m/%Y')}")

checkin = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

col1, col2, col3 = st.columns(3)
if checkin:
    with col1:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Energia</div>
                <div class="valor">{checkin['energy']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Sono</div>
                <div class="valor">{checkin['sleep_hours']}h</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Estresse</div>
                <div class="valor">{checkin['stress']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("⚡ Nenhum check-in hoje. Vá em **Consistência** e registre sua energia.")

st.subheader("🎯 Hábitos pendentes hoje")

rows = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

pendentes = [r for r in rows if not r["done"]]
concluidos = [r for r in rows if r["done"]]

if not pendentes:
    st.success("🥋 Todos os hábitos foram cumpridos. Disciplina exemplar.")
else:
    for r in pendentes:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">{r['pillar']}</div>
                <div class="valor" style="font-size:1.1rem;">{r['name']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if concluidos:
    st.divider()
    st.caption(f"✅ {len(concluidos)} hábito(s) já cumprido(s) hoje")

st.divider()
if st.button("📝 Fazer check-in diário agora", use_container_width=True):
    st.switch_page("ui/pages/07_Consistencia.py")

```


## `ui/pages/01_Corpo.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()

```


## `ui/pages/02_Mente.py`

```python
import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

livro = query_one("SELECT * FROM book_progress ORDER BY last_update DESC LIMIT 1")

col1, col2 = st.columns([2, 1])
with col1:
    if livro:
        st.markdown(f"**Livro atual:** {livro['book_title']}")
        pct = 0
        if livro['total_pages'] > 0:
            pct = min(1.0, livro['current_page'] / livro['total_pages'])
        st.progress(pct)
        st.caption(f"Página {livro['current_page']} de {livro['total_pages']} ({pct*100:.1f}%)")
    else:
        st.info("📖 Nenhum livro em andamento. Adicione um abaixo.")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Novo Livro", use_container_width=True):
        st.session_state["novo_livro"] = True

if not livro or st.session_state.get("novo_livro", False):
    with st.form("form_livro"):
        st.subheader("Adicionar Livro")
        titulo = st.text_input("Título do Livro")
        total_pag = st.number_input("Total de Páginas", min_value=1, value=100)
        
        if st.form_submit_button("Salvar Livro"):
            if titulo:
                execute(
                    """
                    INSERT INTO book_progress (book_title, total_pages) 
                    VALUES (?, ?)
                    ON CONFLICT(book_title) DO UPDATE SET total_pages = excluded.total_pages
                    """, (titulo, total_pag)
                )
                st.session_state["novo_livro"] = False
                st.rerun()
            else:
                st.error("O título é obrigatório.")

st.divider()
st.subheader("📖 Texto Exato do Dia")

if livro:
    if st.button("🪄 Gerar Leitura do Dia com IA", use_container_width=True):
        with st.spinner("O Mentor está lendo o livro e preparando sua lição..."):
            prompt_ia = f"Atue como um mentor samurai sábio. O usuário está lendo o livro '{livro['book_title']}'. Gere um texto curto e inspirador (cerca de 100 palavras) ou um resumo de um dos principais conceitos desse livro, como se fosse a leitura diária para forjar a mente."
            resumo_ia = ask_gemini(prompt_ia)
            st.session_state["resumo_ia"] = resumo_ia
    
    if "resumo_ia" in st.session_state:
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 15px;">
            <div class="titulo">Leitura Recomendada</div>
            <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{st.session_state['resumo_ia']}</div>
        </div>""", unsafe_allow_html=True)
else:
    st.info("Adicione um livro para gerar o texto do dia.")

with st.expander("✍️ Anotações da Leitura"):
    st.text_area("Seu resumo ou insights de hoje:", placeholder="Digite aqui o que você absorveu do capítulo...")

if livro:
    st.divider()
    with st.form("form_progresso"):
        st.subheader("Atualizar Progresso")
        nova_pag = st.number_input("Página atual", min_value=0, max_value=int(livro['total_pages']), value=int(livro['current_page']))
        
        if st.form_submit_button("Atualizar Página", use_container_width=True):
            execute(
                "UPDATE book_progress SET current_page = ?, last_update = datetime('now') WHERE id = ?",
                (nova_pag, livro['id'])
            )
            st.rerun()

```


## `ui/pages/03_Informacao.py`

```python
import streamlit as st
import sys
from pathlib import Path
import yfinance as yf
import requests
import feedparser

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db

init_db()

st.title("📰 Informação")
st.caption("Mundo, Brasil, Macaé, Legislativo e Finanças.")

# --- FINANÇAS ---
st.subheader("📈 Finanças (Tempo Real)")
col1, col2, col3 = st.columns(3)
tickers = {"Dólar": "BRL=X", "IBOVESPA": "^BVSP", "Bitcoin": "BTC-USD"}
cols = [col1, col2, col3]

for i, (nome, ticker) in enumerate(tickers.items()):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            preco = data['Close'].iloc[-1]
            with cols[i]:
                st.markdown(
                    f"""<div class="samurai-card">
                        <div class="titulo">{nome}</div>
                        <div class="valor">R$ {preco:,.2f}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    except Exception:
        with cols[i]:
            st.error(f"Erro ao carregar {nome}")

st.divider()

# --- NOTÍCIAS ---
st.subheader("🗞️ Últimas Notícias (G1)")
try:
    url = "https://g1.globo.com/rss/g1/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() # Levanta um erro se a requisição falhar
    
    feed = feedparser.parse(response.content)
    
    if feed.entries:
        for entry in feed.entries[:5]:
            st.markdown(f"- [{entry.title}]({entry.link})")
    else:
        st.warning("O feed de notícias está vazio no momento.")
except requests.exceptions.RequestException:
    st.warning("Não foi possível carregar as notícias (servidor do G1 fora do ar ou bloqueando a conexão).")
except Exception as e:
    st.warning("Erro inesperado ao carregar as notícias.")

st.divider()
st.subheader("⚖️ Legislativo")
st.info("🚧 Integração com APIs do Senado, Câmara, ALERJ e Câmara de Macaé será implementada na Sprint 4.")

```


## `ui/pages/04_Patrimonio.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("💎 Patrimônio")
st.caption("Ações, notícias e controle de gastos.")

# --- AÇÕES ---
st.subheader("📊 Ações e FIIs")
col1, col2 = st.columns([2, 1])
with col1:
    ticker_input = st.text_input("Digite o ticker (ex: PETR4.SA, VALE3.SA, HGLG11.SA):", value="PETR4.SA")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    buscar = st.button("Buscar Cotação", use_container_width=True)

if buscar or ticker_input:
    try:
        ticker = yf.Ticker(ticker_input)
        data = ticker.history(period="5d")
        if not data.empty:
            preco_atual = data['Close'].iloc[-1]
            variacao = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
            
            cor = "#4CAF50" if variacao >= 0 else "#F44336"
            
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: {cor};">
                    <div class="titulo">{ticker_input}</div>
                    <div class="valor">R$ {preco_atual:.2f}</div>
                    <div class="detalhe" style="color: {cor};">Variação (5d): {variacao:+.2f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )
            
            with st.expander("Ver Notícias do Ticker"):
                noticias = ticker.news
                if noticias:
                    for n in noticias[:3]:
                        st.markdown(f"- [{n['title']}]({n['link']})")
                else:
                    st.write("Nenhuma notícia recente encontrada.")
        else:
            st.error("Ticker não encontrado ou sem dados.")
    except Exception:
        st.error("Erro ao buscar dados. Verifique o ticker digitado.")

st.divider()

# --- GASTOS ---
st.subheader("💸 Registro de Gastos")

with st.form("form_gasto"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        descricao = st.text_input("Descrição")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
    with col3:
        categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Outros"])
    
    submitted = st.form_submit_button("Registrar Gasto", use_container_width=True)

if submitted:
    if descricao and valor > 0:
        execute(
            "INSERT INTO expenses (expense_date, description, amount, category) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), descricao, valor, categoria)
        )
        st.success("Gasto registrado!")
        st.rerun()
    else:
        st.error("Preencha a descrição e um valor maior que zero.")

# Listar gastos
gastos = query_all("SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 10")
if gastos:
    st.markdown("### Últimos Gastos")
    for g in gastos:
        st.markdown(
            f"""<div class="samurai-card" style="border-left-color: #171717; padding: 10px;">
                <div style="display: flex; justify-content: space-between; color: #CCC;">
                    <span>{g['description']}</span>
                    <span>R$ {g['amount']:.2f} ({g['category']})</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

```


## `ui/pages/05_Descanso.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

st.title("🌿 Descanso & Lazer")
st.caption("Sugestões semanais para recarregar as energias.")

# Pegar a semana do ano para alternar as sugestões
semana_ano = date.today().isocalendar()[1]

MACAÉ = [
    {"local": "Praia dos Cavaleiros", "dica": "Caminhada na orla e um açaí no fim da tarde."},
    {"local": "Lagoa de Imboassica", "dica": "Passeio de caiaque ou pedalinho, ótimo para desacelerar."},
    {"local": "Pico do Frade", "dica": "Trilha leve com vista panorâmica da cidade. Leve água."},
    {"local": "Praia do Pecado", "dica": "Lugar mais reservado para ler um livro e relaxar."},
    {"local": "Parque Municipal da Lagoa", "dica": "Caminhada e contato com a natureza."},
]

ARREDORES = [
    {"local": "Búzios - Rua das Pedras", "dica": "Almoço, caminhada e fim de tarde na praia de Geribá."},
    {"local": "Cabo Frio - Praia do Forte", "dica": "Visitar as dunas e a Fortaleza de São Mateus."},
    {"local": "Arraial do Cabo - Pontal do Atalaia", "dica": "Levar água e preparar para o visual mais bonito da região."},
    {"local": "Lumiar (Nova Friburgo)", "dica": "Pousada, cachoeiras e gastronomia mineira."},
    {"local": "Rio das Ostras - Costazul", "dica": "Feira de artesanato e passeio na lagoa."},
]

sugestao_macae = MACAÉ[semana_ano % len(MACAÉ)]
sugestao_arredores = ARREDORES[semana_ano % len(ARREDORES)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão em Macaé</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_macae['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_macae['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão nos Arredores</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_arredores['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_arredores['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.info("💡 Lembre-se de usar o **Cartão Macaé** nos estabelecimentos parceiros da cidade.")

```


## `ui/pages/06_Autoconhecimento.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("🪞 Autoconhecimento")
st.caption("Diário reflexivo e meditação.")

PROMPTS = [
    "O que drenou minha energia hoje e por quê?",
    "Qual pequena vitória eu tive hoje?",
    "O que eu faria diferente se pudesse recomeçar o dia?",
    "Pelo que sou grato neste exato momento?",
    "Qual pensamento negativo eu posso deixar ir embora?",
    "Como eu tratei as pessoas ao meu redor hoje?",
    "O que aprendi sobre mim mesmo nesta semana?",
]

# Define o prompt do dia baseado no dia do ano (para ser consistente durante o dia)
prompt_do_dia = PROMPTS[date.today().toordinal() % len(PROMPTS)]

st.subheader("📝 Diário Reflexivo")
st.markdown(f"**Prompt de hoje:** *{prompt_do_dia}*")

with st.form("form_journal"):
    texto = st.text_area("Sua reflexão:", height=150, placeholder="Escreva livremente...")
    submitted = st.form_submit_button("Salvar no Diário", use_container_width=True)

if submitted and texto.strip():
    execute(
        "INSERT INTO journal_entries (entry_date, prompt, content) VALUES (?, ?, ?)",
        (date.today().isoformat(), prompt_do_dia, texto.strip())
    )
    st.success("Reflexão salva.")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Meditação Curta")
st.markdown("""
**Respiração Box (5 minutos):**
1. Inspire contando até **4**.
2. Segure a respiração contando até **4**.
3. Expire lentamente contando até **4**.
4. Aguarde contando até **4**.
5. Repita por 5 minutos.
""")

st.divider()
st.subheader("📚 Histórico de Reflexões")

entries = query_all("SELECT * FROM journal_entries ORDER BY entry_date DESC, id DESC LIMIT 5")
if not entries:
    st.info("Nenhuma reflexão registrada ainda.")
else:
    for e in entries:
        with st.expander(f"📅 {e['entry_date']} — {e['prompt']}"):
            st.write(e['content'])

```


## `ui/pages/07_Consistencia.py`

```python
"""Consistência — check-in diário, marcação de hábitos e score anti-burnout."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date, timedelta

import streamlit as st

from core.database import execute, query_all, query_one

today = date.today()
today_iso = today.isoformat()


def calcular_burnout() -> tuple[float, dict]:
    """Score 0–100 (quanto maior, mais risco de burnout)."""
    week_ago = (today - timedelta(days=7)).isoformat()

    checkins = query_all(
        "SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?",
        (week_ago,),
    )
    total_habits = query_one("SELECT COUNT(*) AS c FROM habits WHERE active = 1")["c"] or 0
    logs = query_all(
        "SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,)
    )
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    total = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return total, {
        "avg_energy": avg_energy,
        "avg_stress": avg_stress,
        "avg_sleep": avg_sleep,
        "taxa": taxa,
    }


def classificar_burnout(score: float) -> tuple[str, str]:
    if score < 30:
        return "🟢 Baixo", "#2E7D32"
    if score < 60:
        return "🟡 Médio", "#F9A825"
    if score < 80:
        return "🟠 Alto", "#EF6C00"
    return "🔴 Crítico", "#C62828"


st.title("🎯 Consistência")
st.caption("Disciplina diária é o que forja o samurai.")

st.subheader("📝 Check-in do dia")

existente = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

MOOD_OPTIONS = ["Ótimo", "Bom", "Neutro", "Cansado", "Estressado", "Ansioso"]
mood_default = (
    MOOD_OPTIONS.index(existente["mood"])
    if existente and existente["mood"] in MOOD_OPTIONS
    else 2
)

with st.form("form_checkin", clear_on_submit=False):
    energy = st.slider(
        "Energia (1–10)", 1, 10,
        int(existente["energy"]) if existente else 6,
    )
    sleep_hours = st.number_input(
        "Horas de sono",
        min_value=0.0, max_value=16.0, step=0.5,
        value=float(existente["sleep_hours"]) if existente else 7.0,
    )
    mood = st.selectbox("Humor", MOOD_OPTIONS, index=mood_default)
    stress = st.slider(
        "Estresse (1–10)", 1, 10,
        int(existente["stress"]) if existente else 5,
    )
    notes = st.text_area(
        "Notas (opcional)",
        value=existente["notes"] if existente and existente["notes"] else "",
    )

    submit = st.form_submit_button("💾 Salvar check-in", use_container_width=True)

if submit:
    execute(
        """
        INSERT INTO daily_checkins
            (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy      = excluded.energy,
            sleep_hours = excluded.sleep_hours,
            mood        = excluded.mood,
            stress      = excluded.stress,
            notes       = excluded.notes
        """,
        (today_iso, energy, sleep_hours, mood, stress, notes or None),
    )
    st.success("[OK] Check-in registrado.")
    st.rerun()

st.divider()
st.subheader("🥋 Hábitos de hoje")

habits = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

alterou = False
for h in habits:
    novo = st.checkbox(
        f"**{h['pillar']}** · {h['name']}",
        value=bool(h["done"]),
        key=f"habit_{h['id']}",
    )
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done)
            VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """,
            (h["id"], today_iso, 1 if novo else 0),
        )
        alterou = True

if alterou:
    st.rerun()

st.divider()
st.subheader("🔥 Score Anti-Burnout (7 dias)")

score, metricas = calcular_burnout()
label, cor = classificar_burnout(score)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color:{cor};">
        <div class="titulo">Risco atual</div>
        <div class="valor" style="color:{cor};">{score:.0f}/100 — {label}</div>
        <div class="detalhe">
            Média energia: {metricas['avg_energy']:.1f} ·
            Sono: {metricas['avg_sleep']:.1f}h ·
            Estresse: {metricas['avg_stress']:.1f} ·
            Hábitos: {metricas['taxa']*100:.0f}%
        </div>
    </div>""",
    unsafe_allow_html=True,
)

st.progress(min(1.0, score / 100.0))

with st.expander("Como o score é calculado?"):
    st.markdown(
        """
- **Energia** (30 pts) — quanto menor, maior o risco.
- **Estresse** (30 pts) — quanto maior, maior o risco.
- **Sono** (20 pts) — abaixo de 8h aumenta o risco.
- **Aderência aos hábitos** (20 pts) — baixa execução nos últimos 7 dias eleva o risco.

**0–29:** 🟢 Baixo · **30–59:** 🟡 Médio · **60–79:** 🟠 Alto · **80–100:** 🔴 Crítico
        """
    )

if score >= 80:
    st.error("⚠️ Risco crítico. Priorize descanso hoje. Nenhum treino vale um colapso.")
elif score >= 60:
    st.warning("Atenção: sinais de sobrecarga. Reduza intensidade e priorize sono.")

```


## `ui/pages/__init__.py`

```python
"""Páginas do Projeto Samurai."""

```

```


## `requirements.txt`

```text
streamlit>=1.38.0
pandas>=2.2.0
yfinance>=0.2.40
requests>=2.31.0
feedparser>=6.0.10
google-generativeai>=0.5.0

```


## `services/__init__.py`

```python
"""Serviços externos (IA, yfinance, notícias, etc.)."""

```


## `services/ai.py`

```python
import google.generativeai as genai
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

def get_api_key() -> str:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("gemini_api_key", "")
        except Exception:
            pass
    return ""

def ask_gemini(prompt: str) -> str:
    api_key = get_api_key()
    if not api_key or api_key == "COLE_SUA_CHAVE_AQUI":
        return "⚠️ API Key não configurada. Abra o arquivo 'config.json' na raiz do projeto e insira sua chave do Gemini."
    
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-3.5-flash-lite')  # MODELO FIXADO - NÃO ALTERAR
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Erro na IA: {str(e)}"

```


## `ui/__init__.py`

```python
"""Camada de interface Streamlit."""

```


## `ui/pages/00_Home.py`

```python
"""Dojo — resumo do dia, hábitos pendentes e energia."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date

import streamlit as st

from core.database import query_all, query_one

today_iso = date.today().isoformat()

st.title("🏯 Dojo")
st.caption(f"Hoje é {date.today().strftime('%A, %d/%m/%Y')}")

checkin = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

col1, col2, col3 = st.columns(3)
if checkin:
    with col1:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Energia</div>
                <div class="valor">{checkin['energy']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Sono</div>
                <div class="valor">{checkin['sleep_hours']}h</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Estresse</div>
                <div class="valor">{checkin['stress']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("⚡ Nenhum check-in hoje. Vá em **Consistência** e registre sua energia.")

st.subheader("🎯 Hábitos pendentes hoje")

rows = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

pendentes = [r for r in rows if not r["done"]]
concluidos = [r for r in rows if r["done"]]

if not pendentes:
    st.success("🥋 Todos os hábitos foram cumpridos. Disciplina exemplar.")
else:
    for r in pendentes:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">{r['pillar']}</div>
                <div class="valor" style="font-size:1.1rem;">{r['name']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if concluidos:
    st.divider()
    st.caption(f"✅ {len(concluidos)} hábito(s) já cumprido(s) hoje")

st.divider()
if st.button("📝 Fazer check-in diário agora", use_container_width=True):
    st.switch_page("ui/pages/07_Consistencia.py")

```


## `ui/pages/01_Corpo.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()

```


## `ui/pages/02_Mente.py`

```python
import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

livro = query_one("SELECT * FROM book_progress ORDER BY last_update DESC LIMIT 1")

col1, col2 = st.columns([2, 1])
with col1:
    if livro:
        st.markdown(f"**Livro atual:** {livro['book_title']}")
        pct = 0
        if livro['total_pages'] > 0:
            pct = min(1.0, livro['current_page'] / livro['total_pages'])
        st.progress(pct)
        st.caption(f"Página {livro['current_page']} de {livro['total_pages']} ({pct*100:.1f}%)")
    else:
        st.info("📖 Nenhum livro em andamento. Adicione um abaixo.")

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Novo Livro", use_container_width=True):
        st.session_state["novo_livro"] = True

if not livro or st.session_state.get("novo_livro", False):
    with st.form("form_livro"):
        st.subheader("Adicionar Livro")
        titulo = st.text_input("Título do Livro")
        total_pag = st.number_input("Total de Páginas", min_value=1, value=100)
        
        if st.form_submit_button("Salvar Livro"):
            if titulo:
                execute(
                    """
                    INSERT INTO book_progress (book_title, total_pages) 
                    VALUES (?, ?)
                    ON CONFLICT(book_title) DO UPDATE SET total_pages = excluded.total_pages
                    """, (titulo, total_pag)
                )
                st.session_state["novo_livro"] = False
                st.rerun()
            else:
                st.error("O título é obrigatório.")

st.divider()
st.subheader("📖 Texto Exato do Dia")

if livro:
    if st.button("🪄 Gerar Leitura do Dia com IA", use_container_width=True):
        with st.spinner("O Mentor está lendo o livro e preparando sua lição..."):
            prompt_ia = f"Atue como um mentor samurai sábio. O usuário está lendo o livro '{livro['book_title']}'. Gere um texto curto e inspirador (cerca de 100 palavras) ou um resumo de um dos principais conceitos desse livro, como se fosse a leitura diária para forjar a mente."
            resumo_ia = ask_gemini(prompt_ia)
            st.session_state["resumo_ia"] = resumo_ia
    
    if "resumo_ia" in st.session_state:
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 15px;">
            <div class="titulo">Leitura Recomendada</div>
            <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{st.session_state['resumo_ia']}</div>
        </div>""", unsafe_allow_html=True)
else:
    st.info("Adicione um livro para gerar o texto do dia.")

with st.expander("✍️ Anotações da Leitura"):
    st.text_area("Seu resumo ou insights de hoje:", placeholder="Digite aqui o que você absorveu do capítulo...")

if livro:
    st.divider()
    with st.form("form_progresso"):
        st.subheader("Atualizar Progresso")
        nova_pag = st.number_input("Página atual", min_value=0, max_value=int(livro['total_pages']), value=int(livro['current_page']))
        
        if st.form_submit_button("Atualizar Página", use_container_width=True):
            execute(
                "UPDATE book_progress SET current_page = ?, last_update = datetime('now') WHERE id = ?",
                (nova_pag, livro['id'])
            )
            st.rerun()

```


## `ui/pages/03_Informacao.py`

```python
import streamlit as st
import sys
from pathlib import Path
import yfinance as yf
import requests
import feedparser

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db

init_db()

st.title("📰 Informação")
st.caption("Mundo, Brasil, Macaé, Legislativo e Finanças.")

# --- FINANÇAS ---
st.subheader("📈 Finanças (Tempo Real)")
col1, col2, col3 = st.columns(3)
tickers = {"Dólar": "BRL=X", "IBOVESPA": "^BVSP", "Bitcoin": "BTC-USD"}
cols = [col1, col2, col3]

for i, (nome, ticker) in enumerate(tickers.items()):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            preco = data['Close'].iloc[-1]
            with cols[i]:
                st.markdown(
                    f"""<div class="samurai-card">
                        <div class="titulo">{nome}</div>
                        <div class="valor">R$ {preco:,.2f}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    except Exception:
        with cols[i]:
            st.error(f"Erro ao carregar {nome}")

st.divider()

# --- NOTÍCIAS ---
st.subheader("🗞️ Últimas Notícias (G1)")
try:
    url = "https://g1.globo.com/rss/g1/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() # Levanta um erro se a requisição falhar
    
    feed = feedparser.parse(response.content)
    
    if feed.entries:
        for entry in feed.entries[:5]:
            st.markdown(f"- [{entry.title}]({entry.link})")
    else:
        st.warning("O feed de notícias está vazio no momento.")
except requests.exceptions.RequestException:
    st.warning("Não foi possível carregar as notícias (servidor do G1 fora do ar ou bloqueando a conexão).")
except Exception as e:
    st.warning("Erro inesperado ao carregar as notícias.")

st.divider()
st.subheader("⚖️ Legislativo")
st.info("🚧 Integração com APIs do Senado, Câmara, ALERJ e Câmara de Macaé será implementada na Sprint 4.")

```


## `ui/pages/04_Patrimonio.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("💎 Patrimônio")
st.caption("Ações, notícias e controle de gastos.")

# --- AÇÕES ---
st.subheader("📊 Ações e FIIs")
col1, col2 = st.columns([2, 1])
with col1:
    ticker_input = st.text_input("Digite o ticker (ex: PETR4.SA, VALE3.SA, HGLG11.SA):", value="PETR4.SA")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    buscar = st.button("Buscar Cotação", use_container_width=True)

if buscar or ticker_input:
    try:
        ticker = yf.Ticker(ticker_input)
        data = ticker.history(period="5d")
        if not data.empty:
            preco_atual = data['Close'].iloc[-1]
            variacao = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
            
            cor = "#4CAF50" if variacao >= 0 else "#F44336"
            
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: {cor};">
                    <div class="titulo">{ticker_input}</div>
                    <div class="valor">R$ {preco_atual:.2f}</div>
                    <div class="detalhe" style="color: {cor};">Variação (5d): {variacao:+.2f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )
            
            with st.expander("Ver Notícias do Ticker"):
                noticias = ticker.news
                if noticias:
                    for n in noticias[:3]:
                        st.markdown(f"- [{n['title']}]({n['link']})")
                else:
                    st.write("Nenhuma notícia recente encontrada.")
        else:
            st.error("Ticker não encontrado ou sem dados.")
    except Exception:
        st.error("Erro ao buscar dados. Verifique o ticker digitado.")

st.divider()

# --- GASTOS ---
st.subheader("💸 Registro de Gastos")

with st.form("form_gasto"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        descricao = st.text_input("Descrição")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
    with col3:
        categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Outros"])
    
    submitted = st.form_submit_button("Registrar Gasto", use_container_width=True)

if submitted:
    if descricao and valor > 0:
        execute(
            "INSERT INTO expenses (expense_date, description, amount, category) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), descricao, valor, categoria)
        )
        st.success("Gasto registrado!")
        st.rerun()
    else:
        st.error("Preencha a descrição e um valor maior que zero.")

# Listar gastos
gastos = query_all("SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 10")
if gastos:
    st.markdown("### Últimos Gastos")
    for g in gastos:
        st.markdown(
            f"""<div class="samurai-card" style="border-left-color: #171717; padding: 10px;">
                <div style="display: flex; justify-content: space-between; color: #CCC;">
                    <span>{g['description']}</span>
                    <span>R$ {g['amount']:.2f} ({g['category']})</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

```


## `ui/pages/05_Descanso.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

st.title("🌿 Descanso & Lazer")
st.caption("Sugestões semanais para recarregar as energias.")

# Pegar a semana do ano para alternar as sugestões
semana_ano = date.today().isocalendar()[1]

MACAÉ = [
    {"local": "Praia dos Cavaleiros", "dica": "Caminhada na orla e um açaí no fim da tarde."},
    {"local": "Lagoa de Imboassica", "dica": "Passeio de caiaque ou pedalinho, ótimo para desacelerar."},
    {"local": "Pico do Frade", "dica": "Trilha leve com vista panorâmica da cidade. Leve água."},
    {"local": "Praia do Pecado", "dica": "Lugar mais reservado para ler um livro e relaxar."},
    {"local": "Parque Municipal da Lagoa", "dica": "Caminhada e contato com a natureza."},
]

ARREDORES = [
    {"local": "Búzios - Rua das Pedras", "dica": "Almoço, caminhada e fim de tarde na praia de Geribá."},
    {"local": "Cabo Frio - Praia do Forte", "dica": "Visitar as dunas e a Fortaleza de São Mateus."},
    {"local": "Arraial do Cabo - Pontal do Atalaia", "dica": "Levar água e preparar para o visual mais bonito da região."},
    {"local": "Lumiar (Nova Friburgo)", "dica": "Pousada, cachoeiras e gastronomia mineira."},
    {"local": "Rio das Ostras - Costazul", "dica": "Feira de artesanato e passeio na lagoa."},
]

sugestao_macae = MACAÉ[semana_ano % len(MACAÉ)]
sugestao_arredores = ARREDORES[semana_ano % len(ARREDORES)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão em Macaé</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_macae['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_macae['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão nos Arredores</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_arredores['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_arredores['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.info("💡 Lembre-se de usar o **Cartão Macaé** nos estabelecimentos parceiros da cidade.")

```


## `ui/pages/06_Autoconhecimento.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()

st.title("🪞 Autoconhecimento")
st.caption("Diário reflexivo e meditação.")

PROMPTS = [
    "O que drenou minha energia hoje e por quê?",
    "Qual pequena vitória eu tive hoje?",
    "O que eu faria diferente se pudesse recomeçar o dia?",
    "Pelo que sou grato neste exato momento?",
    "Qual pensamento negativo eu posso deixar ir embora?",
    "Como eu tratei as pessoas ao meu redor hoje?",
    "O que aprendi sobre mim mesmo nesta semana?",
]

prompt_do_dia = PROMPTS[date.today().toordinal() % len(PROMPTS)]

st.subheader("📝 Diário Reflexivo")
st.markdown(f"**Prompt de hoje:** *{prompt_do_dia}*")

with st.form("form_journal"):
    texto = st.text_area("Sua reflexão:", height=150, placeholder="Escreva livremente...")
    submitted = st.form_submit_button("Salvar e Refletir com IA", use_container_width=True)

if submitted and texto.strip():
    with st.spinner("O Mentor Samurai está refletindo sobre suas palavras..."):
        prompt_ia = f"Atue como um mentor samurai sábio e empático. O usuário escreveu a seguinte reflexão sobre o prompt '{prompt_do_dia}':\n\n'{texto.strip()}'\n\nForneça uma resposta curta (máximo 2 parágrafos) validando os sentimentos dele e oferecendo uma perspectiva focada em disciplina, evolução e paz interior. Fale de forma direta e acolhedora."
        reflexao_ia = ask_gemini(prompt_ia)
        
        execute(
            "INSERT INTO journal_entries (entry_date, prompt, content, ai_reflection) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), prompt_do_dia, texto.strip(), reflexao_ia)
        )
    st.success("Reflexão salva e analisada.")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Meditação Curta")
st.markdown("""
**Respiração Box (5 minutos):**
1. Inspire contando até **4**.
2. Segure a respiração contando até **4**.
3. Expire lentamente contando até **4**.
4. Aguarde contando até **4**.
5. Repita por 5 minutos.
""")

st.divider()
st.subheader("📚 Histórico de Reflexões")

entries = query_all("SELECT * FROM journal_entries ORDER BY entry_date DESC, id DESC LIMIT 5")
if not entries:
    st.info("Nenhuma reflexão registrada ainda.")
else:
    for e in entries:
        with st.expander(f"📅 {e['entry_date']} — {e['prompt']}"):
            st.markdown(f"**Sua reflexão:**\n{e['content']}")
            if e['ai_reflection']:
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 10px; padding: 10px;">
                    <div style="color: #F2F2F2; font-size: 0.9rem; font-style: italic;">
                        <b>Mentor Samurai:</b><br>{e['ai_reflection']}
                    </div>
                </div>""", unsafe_allow_html=True)

```


## `ui/pages/07_Consistencia.py`

```python
"""Consistência — check-in diário, marcação de hábitos e score anti-burnout."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date, timedelta

import streamlit as st

from core.database import execute, query_all, query_one
from services.ai import ask_gemini

today = date.today()
today_iso = today.isoformat()

def calcular_burnout() -> tuple[float, dict]:
    week_ago = (today - timedelta(days=7)).isoformat()

    checkins = query_all("SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?", (week_ago,))
    total_habits = query_one("SELECT COUNT(*) AS c FROM habits WHERE active = 1")["c"] or 0
    logs = query_all("SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,))
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    total = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return total, {
        "avg_energy": avg_energy,
        "avg_stress": avg_stress,
        "avg_sleep": avg_sleep,
        "taxa": taxa,
    }

def classificar_burnout(score: float) -> tuple[str, str]:
    if score < 30:
        return "🟢 Baixo", "#2E7D32"
    if score < 60:
        return "🟡 Médio", "#F9A825"
    if score < 80:
        return "🟠 Alto", "#EF6C00"
    return "🔴 Crítico", "#C62828"

st.title("🎯 Consistência")
st.caption("Disciplina diária é o que forja o samurai.")

st.subheader("📝 Check-in do dia")
existente = query_one("SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,))
MOOD_OPTIONS = ["Ótimo", "Bom", "Neutro", "Cansado", "Estressado", "Ansioso"]
mood_default = (MOOD_OPTIONS.index(existente["mood"]) if existente and existente["mood"] in MOOD_OPTIONS else 2)

with st.form("form_checkin", clear_on_submit=False):
    energy = st.slider("Energia (1–10)", 1, 10, int(existente["energy"]) if existente else 6)
    sleep_hours = st.number_input("Horas de sono", min_value=0.0, max_value=16.0, step=0.5, value=float(existente["sleep_hours"]) if existente else 7.0)
    mood = st.selectbox("Humor", MOOD_OPTIONS, index=mood_default)
    stress = st.slider("Estresse (1–10)", 1, 10, int(existente["stress"]) if existente else 5)
    notes = st.text_area("Notas (opcional)", value=existente["notes"] if existente and existente["notes"] else "")
    submit = st.form_submit_button("💾 Salvar check-in", use_container_width=True)

if submit:
    execute(
        """
        INSERT INTO daily_checkins (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy = excluded.energy, sleep_hours = excluded.sleep_hours, mood = excluded.mood, stress = excluded.stress, notes = excluded.notes
        """,
        (today_iso, energy, sleep_hours, mood, stress, notes or None),
    )
    st.success("[OK] Check-in registrado.")
    st.rerun()

st.divider()
st.subheader("🥋 Hábitos de hoje")
habits = query_all(
    """
    SELECT h.id, h.name, h.pillar, COALESCE(l.done, 0) AS done
    FROM habits h LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1 ORDER BY h.pillar, h.name
    """, (today_iso,),
)
alterou = False
for h in habits:
    novo = st.checkbox(f"**{h['pillar']}** · {h['name']}", value=bool(h["done"]), key=f"habit_{h['id']}")
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """, (h["id"], today_iso, 1 if novo else 0),
        )
        alterou = True
if alterou: st.rerun()

st.divider()
st.subheader("🔥 Score Anti-Burnout (7 dias)")
score, metricas = calcular_burnout()
label, cor = classificar_burnout(score)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color:{cor};">
        <div class="titulo">Risco atual</div>
        <div class="valor" style="color:{cor};">{score:.0f}/100 — {label}</div>
        <div class="detalhe">
            Média energia: {metricas['avg_energy']:.1f} · Sono: {metricas['avg_sleep']:.1f}h · Estresse: {metricas['avg_stress']:.1f} · Hábitos: {metricas['taxa']*100:.0f}%
        </div>
    </div>""", unsafe_allow_html=True,
)
st.progress(min(1.0, score / 100.0))

if score >= 80:
    st.error("⚠️ Risco crítico. Priorize descanso hoje. Nenhum treino vale um colapso.")
elif score >= 60:
    st.warning("Atenção: sinais de sobrecarga. Reduza intensidade e priorize sono.")

st.divider()
st.subheader("🧠 Relatório do Mentor Samurai")
if st.button("📜 Gerar Análise Semanal com IA", use_container_width=True):
    with st.spinner("O Mentor está analisando seus dados da semana..."):
        prompt_ia = f"Atue como um mentor samurai sábio e direto. Aqui estão os dados da semana do usuário:\n- Score de Burnout: {score:.0f}/100\n- Média de Energia: {metricas['avg_energy']:.1f}\n- Média de Sono: {metricas['avg_sleep']:.1f}h\n- Média de Estresse: {metricas['avg_stress']:.1f}\n- Taxa de conclusão de hábitos: {metricas['taxa']*100:.0f}%\n\nEscreva um relatório semanal curto (max 3 parágrafos), motivador e realista. Se o burnout estiver alto (>60), aconselhe descanso. Se estiver baixo, parabenize e incentive a manter a disciplina. Mantenha o tom sério, mas encorajador."
        relatorio_ia = ask_gemini(prompt_ia)
        
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 15px;">
            <div class="titulo">Visão do Mestre</div>
            <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{relatorio_ia}</div>
        </div>""", unsafe_allow_html=True)

```


## `ui/pages/08_Religiao.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("🕊️ Religião")
st.caption("Cultivando a fé e a conexão com Deus.")

hoje = date.today().isoformat()

# --- HÁBITOS RELIGIOSOS ---
st.subheader("🙏 Práticas Espirituais")

habits = query_all(
    """
    SELECT h.id, h.name, COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.pillar = 'Religião' AND h.active = 1
    ORDER BY h.name
    """,
    (hoje,),
)

alterou = False
for h in habits:
    novo = st.checkbox(h["name"], value=bool(h["done"]), key=f"rel_{h['id']}")
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """,
            (h["id"], hoje, 1 if novo else 0),
        )
        alterou = True

if alterou:
    st.rerun()

st.divider()

# --- VERSÍCULO DO DIA ---
st.subheader("📖 Versículo do Dia")

VERSICULOS = [
    ("Salmos 23:1", "O Senhor é o meu pastor; nada me faltará."),
    ("Filipenses 4:13", "Posso todas as coisas naquele que me fortalece."),
    ("Josué 1:9", "Sê forte e corajoso; não temas, nem te espantes, porque o Senhor, teu Deus, é contigo."),
    ("Provérbios 3:5", "Confia no Senhor de todo o teu coração e não te estribes no teu próprio entendimento."),
    ("Isaías 41:10", "Não temas, porque eu sou contigo; não te assombres, porque eu sou o teu Deus."),
    ("Salmos 119:105", "Lâmpada para os meus pés é tua palavra e luz, para o meu caminho."),
    ("Romanos 8:28", "E sabemos que todas as coisas contribuem juntamente para o bem daqueles que amam a Deus."),
]

# Escolhe o versículo baseado no dia do ano
v = VERSICULOS[date.today().toordinal() % len(VERSICULOS)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
        <div class="titulo">{v[0]}</div>
        <div class="valor" style="font-size: 1.1rem; font-style: italic; color: #F2F2F2;">"{v[1]}"</div>
    </div>""",
    unsafe_allow_html=True,
)

st.divider()
st.subheader("✍️ Diário Espiritual")

with st.form("form_diario_espiritual"):
    texto = st.text_area("O que Deus falou com você hoje?", placeholder="Escreva uma oração, um agradecimento ou um aprendizado...")
    submitted = st.form_submit_button("Salvar no Diário", use_container_width=True)

if submitted and texto.strip():
    execute(
        "INSERT INTO journal_entries (entry_date, prompt, content) VALUES (?, ?, ?)",
        (date.today().isoformat(), "Diário Espiritual", texto.strip())
    )
    st.success("Registro salvo.")
    st.rerun()

```


## `ui/pages/__init__.py`

```python
"""Páginas do Projeto Samurai."""

```

```


## `requirements.txt`

```text
streamlit>=1.38.0
pandas>=2.2.0
yfinance>=0.2.40
requests>=2.31.0
feedparser>=6.0.10
google-generativeai>=0.5.0
pypdf>=4.0.0

```


## `services/__init__.py`

```python
"""Serviços externos (IA, yfinance, notícias, etc.)."""

```


## `services/ai.py`

```python
import google.generativeai as genai
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

def get_api_key() -> str:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("gemini_api_key", "")
        except Exception:
            pass
    return ""

def ask_gemini(prompt: str) -> str:
    api_key = get_api_key()
    if not api_key or api_key == "COLE_SUA_CHAVE_AQUI":
        return "⚠️ API Key não configurada. Abra o arquivo 'config.json' na raiz do projeto e insira sua chave do Gemini."
    
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-3.5-flash-lite')  # MODELO FIXADO - NÃO ALTERAR
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Erro na IA: {str(e)}"

```


## `ui/__init__.py`

```python
"""Camada de interface Streamlit."""

```


## `ui/pages/00_Home.py`

```python
"""Dojo — resumo do dia, hábitos pendentes e energia."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date

import streamlit as st

from core.database import query_all, query_one

today_iso = date.today().isoformat()

st.title("🏯 Dojo")
DIAS_SEMANA = {
    "Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"
}
dia_ingles = date.today().strftime('%A')
dia_pt = DIAS_SEMANA.get(dia_ingles, dia_ingles)
st.caption(f"Hoje é {dia_pt}, {date.today().strftime('%d/%m/%Y')}")

checkin = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

col1, col2, col3 = st.columns(3)
if checkin:
    with col1:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Energia</div>
                <div class="valor">{checkin['energy']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Sono</div>
                <div class="valor">{checkin['sleep_hours']}h</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Estresse</div>
                <div class="valor">{checkin['stress']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("⚡ Nenhum check-in hoje. Vá em **Consistência** e registre sua energia.")

st.subheader("🎯 Hábitos pendentes hoje")

rows = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

pendentes = [r for r in rows if not r["done"]]
concluidos = [r for r in rows if r["done"]]

if not pendentes:
    st.success("🥋 Todos os hábitos foram cumpridos. Disciplina exemplar.")
else:
    for r in pendentes:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">{r['pillar']}</div>
                <div class="valor" style="font-size:1.1rem;">{r['name']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if concluidos:
    st.divider()
    st.caption(f"✅ {len(concluidos)} hábito(s) já cumprido(s) hoje")

st.divider()
if st.button("📝 Fazer check-in diário agora", use_container_width=True):
    st.switch_page("ui/pages/07_Consistencia.py")

```


## `ui/pages/01_Corpo.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()

```


## `ui/pages/02_Mente.py`

```python
import streamlit as st
import sys
from pathlib import Path
import re

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db
from services.ai import ask_gemini
from pypdf import PdfReader

init_db()
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

# --- UPLOAD DE PDF ---
with st.expander("📚 Enviar Novo Livro (PDF)"):
    uploaded_file = st.file_uploader("Selecione o PDF do livro", type=["pdf"])
    palavras_por_dia = st.number_input("Meta de leitura diária (palavras)", min_value=200, max_value=5000, value=1000, step=100)
    
    if uploaded_file and st.button("Processar PDF e Criar Plano"):
        with st.spinner("Extraindo texto e dividindo a leitura..."):
            try:
                reader = PdfReader(uploaded_file)
                full_text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        full_text += extracted + " "
                
                # Limpeza básica
                full_text = re.sub(r'\s+', ' ', full_text)
                palavras = full_text.split()
                
                if len(palavras) < 100:
                    st.error("O PDF parece conter pouco texto ou é composto por imagens.")
                else:
                    book_title = uploaded_file.name.replace(".pdf", "")
                    
                    # Limpa dados antigos do mesmo livro
                    execute("DELETE FROM book_chunks WHERE book_title = ?", (book_title,))
                    
                    # Divide em chunks
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
            except Exception as e:
                st.error(f"Erro ao ler o PDF: {e}")

st.divider()

# --- LEITURA DO DIA ---
# Busca o livro atual ativo (aquele que tem blocos não concluídos)
livro_ativo = query_one("SELECT book_title FROM book_chunks WHERE completed = 0 ORDER BY id ASC LIMIT 1")

if livro_ativo:
    book_title = livro_ativo["book_title"]
    
    # Busca o próximo chunk
    chunk = query_one(
        "SELECT * FROM book_chunks WHERE book_title = ? AND completed = 0 ORDER BY chunk_index ASC LIMIT 1",
        (book_title,)
    )
    
    if chunk:
        total_chunks = query_one("SELECT COUNT(*) AS c FROM book_chunks WHERE book_title = ?", (book_title,))["c"]
        st.subheader(f"📖 {book_title}")
        st.caption(f"Leitura {chunk['chunk_index'] + 1} de {total_chunks}")
        
        # Exibe o texto formatado no card
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
                st.rerun()
        with col2:
            if st.button("🪄 Resumo com IA", use_container_width=True):
                with st.spinner("O Mentor está resumindo o texto de hoje..."):
                    prompt = f"Resuma o seguinte trecho de um livro de forma inspiradora e direta, destacando os principais aprendizados:\n\n{chunk['text_content']}"
                    resumo = ask_gemini(prompt)
                    st.session_state["resumo_pdf"] = resumo
        
        if "resumo_pdf" in st.session_state:
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
                    <div class="titulo">Resumo do Mentor</div>
                    <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6;">{st.session_state['resumo_pdf']}</div>
                </div>""",
                unsafe_allow_html=True
            )
else:
    st.info("📖 Nenhum livro em andamento. Envie um PDF na seção acima para começar.")

```


## `ui/pages/03_Informacao.py`

```python
import streamlit as st
import sys
from pathlib import Path
import yfinance as yf
import requests
import feedparser

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db

init_db()

st.title("📰 Informação")
st.caption("Mundo, Brasil, Macaé, Legislativo e Finanças.")

# --- FINANÇAS ---
st.subheader("📈 Finanças (Tempo Real)")
col1, col2, col3 = st.columns(3)
tickers = {"Dólar": "BRL=X", "IBOVESPA": "^BVSP", "Bitcoin": "BTC-USD"}
cols = [col1, col2, col3]

for i, (nome, ticker) in enumerate(tickers.items()):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            preco = data['Close'].iloc[-1]
            with cols[i]:
                st.markdown(
                    f"""<div class="samurai-card">
                        <div class="titulo">{nome}</div>
                        <div class="valor">R$ {preco:,.2f}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    except Exception:
        with cols[i]:
            st.error(f"Erro ao carregar {nome}")

st.divider()

# --- NOTÍCIAS ---
st.subheader("🗞️ Últimas Notícias (G1)")
try:
    url = "https://g1.globo.com/rss/g1/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() # Levanta um erro se a requisição falhar
    
    feed = feedparser.parse(response.content)
    
    if feed.entries:
        for entry in feed.entries[:5]:
            st.markdown(f"- [{entry.title}]({entry.link})")
    else:
        st.warning("O feed de notícias está vazio no momento.")
except requests.exceptions.RequestException:
    st.warning("Não foi possível carregar as notícias (servidor do G1 fora do ar ou bloqueando a conexão).")
except Exception as e:
    st.warning("Erro inesperado ao carregar as notícias.")

st.divider()
st.subheader("⚖️ Legislativo")
st.info("🚧 Integração com APIs do Senado, Câmara, ALERJ e Câmara de Macaé será implementada na Sprint 4.")

```


## `ui/pages/04_Patrimonio.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("💎 Patrimônio")
st.caption("Ações, notícias e controle de gastos.")

# --- AÇÕES ---
st.subheader("📊 Ações e FIIs")
col1, col2 = st.columns([2, 1])
with col1:
    ticker_input = st.text_input("Digite o ticker (ex: PETR4.SA, VALE3.SA, HGLG11.SA):", value="PETR4.SA")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    buscar = st.button("Buscar Cotação", use_container_width=True)

if buscar or ticker_input:
    try:
        ticker = yf.Ticker(ticker_input)
        data = ticker.history(period="5d")
        if not data.empty:
            preco_atual = data['Close'].iloc[-1]
            variacao = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
            
            cor = "#4CAF50" if variacao >= 0 else "#F44336"
            
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: {cor};">
                    <div class="titulo">{ticker_input}</div>
                    <div class="valor">R$ {preco_atual:.2f}</div>
                    <div class="detalhe" style="color: {cor};">Variação (5d): {variacao:+.2f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )
            
            with st.expander("Ver Notícias do Ticker"):
                noticias = ticker.news
                if noticias:
                    for n in noticias[:3]:
                        st.markdown(f"- [{n['title']}]({n['link']})")
                else:
                    st.write("Nenhuma notícia recente encontrada.")
        else:
            st.error("Ticker não encontrado ou sem dados.")
    except Exception:
        st.error("Erro ao buscar dados. Verifique o ticker digitado.")

st.divider()

# --- GASTOS ---
st.subheader("💸 Registro de Gastos")

with st.form("form_gasto"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        descricao = st.text_input("Descrição")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
    with col3:
        categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Outros"])
    
    submitted = st.form_submit_button("Registrar Gasto", use_container_width=True)

if submitted:
    if descricao and valor > 0:
        execute(
            "INSERT INTO expenses (expense_date, description, amount, category) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), descricao, valor, categoria)
        )
        st.success("Gasto registrado!")
        st.rerun()
    else:
        st.error("Preencha a descrição e um valor maior que zero.")

# Listar gastos
gastos = query_all("SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 10")
if gastos:
    st.markdown("### Últimos Gastos")
    for g in gastos:
        st.markdown(
            f"""<div class="samurai-card" style="border-left-color: #171717; padding: 10px;">
                <div style="display: flex; justify-content: space-between; color: #CCC;">
                    <span>{g['description']}</span>
                    <span>R$ {g['amount']:.2f} ({g['category']})</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

```


## `ui/pages/05_Descanso.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

st.title("🌿 Descanso & Lazer")
st.caption("Sugestões semanais para recarregar as energias.")

# Pegar a semana do ano para alternar as sugestões
semana_ano = date.today().isocalendar()[1]

MACAÉ = [
    {"local": "Praia dos Cavaleiros", "dica": "Caminhada na orla e um açaí no fim da tarde."},
    {"local": "Lagoa de Imboassica", "dica": "Passeio de caiaque ou pedalinho, ótimo para desacelerar."},
    {"local": "Pico do Frade", "dica": "Trilha leve com vista panorâmica da cidade. Leve água."},
    {"local": "Praia do Pecado", "dica": "Lugar mais reservado para ler um livro e relaxar."},
    {"local": "Parque Municipal da Lagoa", "dica": "Caminhada e contato com a natureza."},
]

ARREDORES = [
    {"local": "Búzios - Rua das Pedras", "dica": "Almoço, caminhada e fim de tarde na praia de Geribá."},
    {"local": "Cabo Frio - Praia do Forte", "dica": "Visitar as dunas e a Fortaleza de São Mateus."},
    {"local": "Arraial do Cabo - Pontal do Atalaia", "dica": "Levar água e preparar para o visual mais bonito da região."},
    {"local": "Lumiar (Nova Friburgo)", "dica": "Pousada, cachoeiras e gastronomia mineira."},
    {"local": "Rio das Ostras - Costazul", "dica": "Feira de artesanato e passeio na lagoa."},
]

sugestao_macae = MACAÉ[semana_ano % len(MACAÉ)]
sugestao_arredores = ARREDORES[semana_ano % len(ARREDORES)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão em Macaé</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_macae['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_macae['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão nos Arredores</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_arredores['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_arredores['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.info("💡 Lembre-se de usar o **Cartão Macaé** nos estabelecimentos parceiros da cidade.")

```


## `ui/pages/06_Autoconhecimento.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()

st.title("🪞 Autoconhecimento")
st.caption("Diário reflexivo e meditação.")

PROMPTS = [
    "O que drenou minha energia hoje e por quê?",
    "Qual pequena vitória eu tive hoje?",
    "O que eu faria diferente se pudesse recomeçar o dia?",
    "Pelo que sou grato neste exato momento?",
    "Qual pensamento negativo eu posso deixar ir embora?",
    "Como eu tratei as pessoas ao meu redor hoje?",
    "O que aprendi sobre mim mesmo nesta semana?",
]

prompt_do_dia = PROMPTS[date.today().toordinal() % len(PROMPTS)]

st.subheader("📝 Diário Reflexivo")
st.markdown(f"**Prompt de hoje:** *{prompt_do_dia}*")

with st.form("form_journal"):
    texto = st.text_area("Sua reflexão:", height=150, placeholder="Escreva livremente...")
    submitted = st.form_submit_button("Salvar e Refletir com IA", use_container_width=True)

if submitted and texto.strip():
    with st.spinner("O Mentor Samurai está refletindo sobre suas palavras..."):
        prompt_ia = f"Atue como um mentor samurai sábio e empático. O usuário escreveu a seguinte reflexão sobre o prompt '{prompt_do_dia}':\n\n'{texto.strip()}'\n\nForneça uma resposta curta (máximo 2 parágrafos) validando os sentimentos dele e oferecendo uma perspectiva focada em disciplina, evolução e paz interior. Fale de forma direta e acolhedora."
        reflexao_ia = ask_gemini(prompt_ia)
        
        execute(
            "INSERT INTO journal_entries (entry_date, prompt, content, ai_reflection) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), prompt_do_dia, texto.strip(), reflexao_ia)
        )
    st.success("Reflexão salva e analisada.")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Meditação Curta")
st.markdown("""
**Respiração Box (5 minutos):**
1. Inspire contando até **4**.
2. Segure a respiração contando até **4**.
3. Expire lentamente contando até **4**.
4. Aguarde contando até **4**.
5. Repita por 5 minutos.
""")

st.divider()
st.subheader("📚 Histórico de Reflexões")

entries = query_all("SELECT * FROM journal_entries ORDER BY entry_date DESC, id DESC LIMIT 5")
if not entries:
    st.info("Nenhuma reflexão registrada ainda.")
else:
    for e in entries:
        with st.expander(f"📅 {e['entry_date']} — {e['prompt']}"):
            st.markdown(f"**Sua reflexão:**\n{e['content']}")
            if e['ai_reflection']:
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 10px; padding: 10px;">
                    <div style="color: #F2F2F2; font-size: 0.9rem; font-style: italic;">
                        <b>Mentor Samurai:</b><br>{e['ai_reflection']}
                    </div>
                </div>""", unsafe_allow_html=True)

```


## `ui/pages/07_Consistencia.py`

```python
"""Consistência — check-in diário, marcação de hábitos e score anti-burnout."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date, timedelta

import streamlit as st

from core.database import execute, query_all, query_one
from services.ai import ask_gemini

today = date.today()
today_iso = today.isoformat()

def calcular_burnout() -> tuple[float, dict]:
    week_ago = (today - timedelta(days=7)).isoformat()

    checkins = query_all("SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?", (week_ago,))
    total_habits = query_one("SELECT COUNT(*) AS c FROM habits WHERE active = 1")["c"] or 0
    logs = query_all("SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,))
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    total = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return total, {
        "avg_energy": avg_energy,
        "avg_stress": avg_stress,
        "avg_sleep": avg_sleep,
        "taxa": taxa,
    }

def classificar_burnout(score: float) -> tuple[str, str]:
    if score < 30:
        return "🟢 Baixo", "#2E7D32"
    if score < 60:
        return "🟡 Médio", "#F9A825"
    if score < 80:
        return "🟠 Alto", "#EF6C00"
    return "🔴 Crítico", "#C62828"

st.title("🎯 Consistência")
st.caption("Disciplina diária é o que forja o samurai.")

st.subheader("📝 Check-in do dia")
existente = query_one("SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,))
MOOD_OPTIONS = ["Ótimo", "Bom", "Neutro", "Cansado", "Estressado", "Ansioso"]
mood_default = (MOOD_OPTIONS.index(existente["mood"]) if existente and existente["mood"] in MOOD_OPTIONS else 2)

with st.form("form_checkin", clear_on_submit=False):
    energy = st.slider("Energia (1–10)", 1, 10, int(existente["energy"]) if existente else 6)
    sleep_hours = st.number_input("Horas de sono", min_value=0.0, max_value=16.0, step=0.5, value=float(existente["sleep_hours"]) if existente else 7.0)
    mood = st.selectbox("Humor", MOOD_OPTIONS, index=mood_default)
    stress = st.slider("Estresse (1–10)", 1, 10, int(existente["stress"]) if existente else 5)
    notes = st.text_area("Notas (opcional)", value=existente["notes"] if existente and existente["notes"] else "")
    submit = st.form_submit_button("💾 Salvar check-in", use_container_width=True)

if submit:
    execute(
        """
        INSERT INTO daily_checkins (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy = excluded.energy, sleep_hours = excluded.sleep_hours, mood = excluded.mood, stress = excluded.stress, notes = excluded.notes
        """,
        (today_iso, energy, sleep_hours, mood, stress, notes or None),
    )
    st.success("[OK] Check-in registrado.")
    st.rerun()

st.divider()
st.subheader("🥋 Hábitos de hoje")
habits = query_all(
    """
    SELECT h.id, h.name, h.pillar, COALESCE(l.done, 0) AS done
    FROM habits h LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1 ORDER BY h.pillar, h.name
    """, (today_iso,),
)
alterou = False
for h in habits:
    novo = st.checkbox(f"**{h['pillar']}** · {h['name']}", value=bool(h["done"]), key=f"habit_{h['id']}")
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """, (h["id"], today_iso, 1 if novo else 0),
        )
        alterou = True
if alterou: st.rerun()

st.divider()
st.subheader("🔥 Score Anti-Burnout (7 dias)")
score, metricas = calcular_burnout()
label, cor = classificar_burnout(score)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color:{cor};">
        <div class="titulo">Risco atual</div>
        <div class="valor" style="color:{cor};">{score:.0f}/100 — {label}</div>
        <div class="detalhe">
            Média energia: {metricas['avg_energy']:.1f} · Sono: {metricas['avg_sleep']:.1f}h · Estresse: {metricas['avg_stress']:.1f} · Hábitos: {metricas['taxa']*100:.0f}%
        </div>
    </div>""", unsafe_allow_html=True,
)
st.progress(min(1.0, score / 100.0))

if score >= 80:
    st.error("⚠️ Risco crítico. Priorize descanso hoje. Nenhum treino vale um colapso.")
elif score >= 60:
    st.warning("Atenção: sinais de sobrecarga. Reduza intensidade e priorize sono.")

st.divider()
st.subheader("🧠 Relatório do Mentor Samurai")
if st.button("📜 Gerar Análise Semanal com IA", use_container_width=True):
    with st.spinner("O Mentor está analisando seus dados da semana..."):
        prompt_ia = f"Atue como um mentor samurai sábio e direto. Aqui estão os dados da semana do usuário:\n- Score de Burnout: {score:.0f}/100\n- Média de Energia: {metricas['avg_energy']:.1f}\n- Média de Sono: {metricas['avg_sleep']:.1f}h\n- Média de Estresse: {metricas['avg_stress']:.1f}\n- Taxa de conclusão de hábitos: {metricas['taxa']*100:.0f}%\n\nEscreva um relatório semanal curto (max 3 parágrafos), motivador e realista. Se o burnout estiver alto (>60), aconselhe descanso. Se estiver baixo, parabenize e incentive a manter a disciplina. Mantenha o tom sério, mas encorajador."
        relatorio_ia = ask_gemini(prompt_ia)
        
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 15px;">
            <div class="titulo">Visão do Mestre</div>
            <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{relatorio_ia}</div>
        </div>""", unsafe_allow_html=True)

```


## `ui/pages/08_Religiao.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("🕊️ Religião")
st.caption("Cultivando a fé e a conexão com Deus.")

hoje = date.today().isoformat()

# --- HÁBITOS RELIGIOSOS ---
st.subheader("🙏 Práticas Espirituais")

habits = query_all(
    """
    SELECT h.id, h.name, COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.pillar = 'Religião' AND h.active = 1
    ORDER BY h.name
    """,
    (hoje,),
)

alterou = False
for h in habits:
    novo = st.checkbox(h["name"], value=bool(h["done"]), key=f"rel_{h['id']}")
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """,
            (h["id"], hoje, 1 if novo else 0),
        )
        alterou = True

if alterou:
    st.rerun()

st.divider()

# --- VERSÍCULO DO DIA ---
st.subheader("📖 Versículo do Dia")

VERSICULOS = [
    ("Salmos 23:1", "O Senhor é o meu pastor; nada me faltará."),
    ("Filipenses 4:13", "Posso todas as coisas naquele que me fortalece."),
    ("Josué 1:9", "Sê forte e corajoso; não temas, nem te espantes, porque o Senhor, teu Deus, é contigo."),
    ("Provérbios 3:5", "Confia no Senhor de todo o teu coração e não te estribes no teu próprio entendimento."),
    ("Isaías 41:10", "Não temas, porque eu sou contigo; não te assombres, porque eu sou o teu Deus."),
    ("Salmos 119:105", "Lâmpada para os meus pés é tua palavra e luz, para o meu caminho."),
    ("Romanos 8:28", "E sabemos que todas as coisas contribuem juntamente para o bem daqueles que amam a Deus."),
]

# Escolhe o versículo baseado no dia do ano
v = VERSICULOS[date.today().toordinal() % len(VERSICULOS)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
        <div class="titulo">{v[0]}</div>
        <div class="valor" style="font-size: 1.1rem; font-style: italic; color: #F2F2F2;">"{v[1]}"</div>
    </div>""",
    unsafe_allow_html=True,
)

st.divider()
st.subheader("✍️ Diário Espiritual")

with st.form("form_diario_espiritual"):
    texto = st.text_area("O que Deus falou com você hoje?", placeholder="Escreva uma oração, um agradecimento ou um aprendizado...")
    submitted = st.form_submit_button("Salvar no Diário", use_container_width=True)

if submitted and texto.strip():
    execute(
        "INSERT INTO journal_entries (entry_date, prompt, content) VALUES (?, ?, ?)",
        (date.today().isoformat(), "Diário Espiritual", texto.strip())
    )
    st.success("Registro salvo.")
    st.rerun()

```


## `ui/pages/__init__.py`

```python
"""Páginas do Projeto Samurai."""

```

```


## `requirements.txt`

```text
streamlit>=1.38.0
pandas>=2.2.0
yfinance>=0.2.40
requests>=2.31.0
feedparser>=6.0.10
google-generativeai>=0.5.0
pymupdf>=1.24.0

```


## `services/__init__.py`

```python
"""Serviços externos (IA, yfinance, notícias, etc.)."""

```


## `services/ai.py`

```python
import google.generativeai as genai
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

def get_api_key() -> str:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("gemini_api_key", "")
        except Exception:
            pass
    return ""

def ask_gemini(prompt: str) -> str:
    api_key = get_api_key()
    if not api_key or api_key == "COLE_SUA_CHAVE_AQUI":
        return "⚠️ API Key não configurada. Abra o arquivo 'config.json' na raiz do projeto e insira sua chave do Gemini."
    
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-3.5-flash-lite')  # MODELO FIXADO - NÃO ALTERAR
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Erro na IA: {str(e)}"

```


## `ui/__init__.py`

```python
"""Camada de interface Streamlit."""

```


## `ui/pages/00_Home.py`

```python
"""Dojo — resumo do dia, hábitos pendentes e energia."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date

import streamlit as st

from core.database import query_all, query_one

today_iso = date.today().isoformat()

st.title("🏯 Dojo")
DIAS_SEMANA = {
    "Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"
}
dia_ingles = date.today().strftime('%A')
dia_pt = DIAS_SEMANA.get(dia_ingles, dia_ingles)
st.caption(f"Hoje é {dia_pt}, {date.today().strftime('%d/%m/%Y')}")

checkin = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

col1, col2, col3 = st.columns(3)
if checkin:
    with col1:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Energia</div>
                <div class="valor">{checkin['energy']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Sono</div>
                <div class="valor">{checkin['sleep_hours']}h</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Estresse</div>
                <div class="valor">{checkin['stress']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("⚡ Nenhum check-in hoje. Vá em **Consistência** e registre sua energia.")

st.subheader("🎯 Hábitos pendentes hoje")

rows = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

pendentes = [r for r in rows if not r["done"]]
concluidos = [r for r in rows if r["done"]]

if not pendentes:
    st.success("🥋 Todos os hábitos foram cumpridos. Disciplina exemplar.")
else:
    for r in pendentes:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">{r['pillar']}</div>
                <div class="valor" style="font-size:1.1rem;">{r['name']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if concluidos:
    st.divider()
    st.caption(f"✅ {len(concluidos)} hábito(s) já cumprido(s) hoje")

st.divider()
if st.button("📝 Fazer check-in diário agora", use_container_width=True):
    st.switch_page("ui/pages/07_Consistencia.py")

```


## `ui/pages/01_Corpo.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()

```


## `ui/pages/02_Mente.py`

```python
import streamlit as st
import sys
from pathlib import Path
import re
import fitz  # PyMuPDF

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("🧠 Mente")
st.caption("Leitura guiada e evolução do conhecimento.")

# --- UPLOAD DE PDF ---
with st.expander("📚 Enviar Novo Livro (PDF)"):
    uploaded_file = st.file_uploader("Selecione o PDF do livro", type=["pdf"])
    palavras_por_dia = st.number_input("Meta de leitura diária (palavras)", min_value=200, max_value=5000, value=1000, step=100)
    
    if uploaded_file and st.button("Processar PDF e Criar Plano"):
        with st.spinner("Extraindo texto e dividindo a leitura..."):
            try:
                # Usando PyMuPDF para extração muito mais precisa
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                full_text = ""
                for page in doc:
                    full_text += page.get_text("text") + " "
                
                # Limpeza básica
                full_text = re.sub(r'\s+', ' ', full_text)
                palavras = full_text.split()
                
                if len(palavras) < 100:
                    st.error("O PDF parece conter pouco texto ou é composto por imagens (necessita OCR).")
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
        
        # Usamos st.write em vez de HTML puro para evitar quebras por caracteres especiais do livro
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
                st.rerun()
        with col2:
            if st.button("🪄 Resumo com IA", use_container_width=True):
                with st.spinner("O Mentor está resumindo o texto de hoje..."):
                    prompt = f"Resuma o seguinte trecho de um livro de forma inspiradora e direta, destacando os principais aprendizados:\n\n{chunk['text_content']}"
                    resumo = ask_gemini(prompt)
                    st.session_state["resumo_pdf"] = resumo
        
        if "resumo_pdf" in st.session_state:
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
                    <div class="titulo">Resumo do Mentor</div>
                    <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6;">{st.session_state['resumo_pdf']}</div>
                </div>""",
                unsafe_allow_html=True
            )
else:
    st.info("📖 Nenhum livro em andamento. Envie um PDF na seção acima para começar.")

```


## `ui/pages/03_Informacao.py`

```python
import streamlit as st
import sys
from pathlib import Path
import yfinance as yf
import requests
import feedparser

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db

init_db()

st.title("📰 Informação")
st.caption("Mundo, Brasil, Macaé, Legislativo e Finanças.")

# --- FINANÇAS ---
st.subheader("📈 Finanças (Tempo Real)")
col1, col2, col3 = st.columns(3)
tickers = {"Dólar": "BRL=X", "IBOVESPA": "^BVSP", "Bitcoin": "BTC-USD"}
cols = [col1, col2, col3]

for i, (nome, ticker) in enumerate(tickers.items()):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            preco = data['Close'].iloc[-1]
            with cols[i]:
                st.markdown(
                    f"""<div class="samurai-card">
                        <div class="titulo">{nome}</div>
                        <div class="valor">R$ {preco:,.2f}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    except Exception:
        with cols[i]:
            st.error(f"Erro ao carregar {nome}")

st.divider()

# --- NOTÍCIAS ---
st.subheader("🗞️ Últimas Notícias (G1)")
try:
    url = "https://g1.globo.com/rss/g1/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() # Levanta um erro se a requisição falhar
    
    feed = feedparser.parse(response.content)
    
    if feed.entries:
        for entry in feed.entries[:5]:
            st.markdown(f"- [{entry.title}]({entry.link})")
    else:
        st.warning("O feed de notícias está vazio no momento.")
except requests.exceptions.RequestException:
    st.warning("Não foi possível carregar as notícias (servidor do G1 fora do ar ou bloqueando a conexão).")
except Exception as e:
    st.warning("Erro inesperado ao carregar as notícias.")

st.divider()
st.subheader("⚖️ Legislativo")
st.info("🚧 Integração com APIs do Senado, Câmara, ALERJ e Câmara de Macaé será implementada na Sprint 4.")

```


## `ui/pages/04_Patrimonio.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("💎 Patrimônio")
st.caption("Ações, notícias e controle de gastos.")

# --- AÇÕES ---
st.subheader("📊 Ações e FIIs")
col1, col2 = st.columns([2, 1])
with col1:
    ticker_input = st.text_input("Digite o ticker (ex: PETR4.SA, VALE3.SA, HGLG11.SA):", value="PETR4.SA")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    buscar = st.button("Buscar Cotação", use_container_width=True)

if buscar or ticker_input:
    try:
        ticker = yf.Ticker(ticker_input)
        data = ticker.history(period="5d")
        if not data.empty:
            preco_atual = data['Close'].iloc[-1]
            variacao = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
            
            cor = "#4CAF50" if variacao >= 0 else "#F44336"
            
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: {cor};">
                    <div class="titulo">{ticker_input}</div>
                    <div class="valor">R$ {preco_atual:.2f}</div>
                    <div class="detalhe" style="color: {cor};">Variação (5d): {variacao:+.2f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )
            
            with st.expander("Ver Notícias do Ticker"):
                noticias = ticker.news
                if noticias:
                    for n in noticias[:3]:
                        st.markdown(f"- [{n['title']}]({n['link']})")
                else:
                    st.write("Nenhuma notícia recente encontrada.")
        else:
            st.error("Ticker não encontrado ou sem dados.")
    except Exception:
        st.error("Erro ao buscar dados. Verifique o ticker digitado.")

st.divider()

# --- GASTOS ---
st.subheader("💸 Registro de Gastos")

with st.form("form_gasto"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        descricao = st.text_input("Descrição")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
    with col3:
        categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Outros"])
    
    submitted = st.form_submit_button("Registrar Gasto", use_container_width=True)

if submitted:
    if descricao and valor > 0:
        execute(
            "INSERT INTO expenses (expense_date, description, amount, category) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), descricao, valor, categoria)
        )
        st.success("Gasto registrado!")
        st.rerun()
    else:
        st.error("Preencha a descrição e um valor maior que zero.")

# Listar gastos
gastos = query_all("SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 10")
if gastos:
    st.markdown("### Últimos Gastos")
    for g in gastos:
        st.markdown(
            f"""<div class="samurai-card" style="border-left-color: #171717; padding: 10px;">
                <div style="display: flex; justify-content: space-between; color: #CCC;">
                    <span>{g['description']}</span>
                    <span>R$ {g['amount']:.2f} ({g['category']})</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

```


## `ui/pages/05_Descanso.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

st.title("🌿 Descanso & Lazer")
st.caption("Sugestões semanais para recarregar as energias.")

# Pegar a semana do ano para alternar as sugestões
semana_ano = date.today().isocalendar()[1]

MACAÉ = [
    {"local": "Praia dos Cavaleiros", "dica": "Caminhada na orla e um açaí no fim da tarde."},
    {"local": "Lagoa de Imboassica", "dica": "Passeio de caiaque ou pedalinho, ótimo para desacelerar."},
    {"local": "Pico do Frade", "dica": "Trilha leve com vista panorâmica da cidade. Leve água."},
    {"local": "Praia do Pecado", "dica": "Lugar mais reservado para ler um livro e relaxar."},
    {"local": "Parque Municipal da Lagoa", "dica": "Caminhada e contato com a natureza."},
]

ARREDORES = [
    {"local": "Búzios - Rua das Pedras", "dica": "Almoço, caminhada e fim de tarde na praia de Geribá."},
    {"local": "Cabo Frio - Praia do Forte", "dica": "Visitar as dunas e a Fortaleza de São Mateus."},
    {"local": "Arraial do Cabo - Pontal do Atalaia", "dica": "Levar água e preparar para o visual mais bonito da região."},
    {"local": "Lumiar (Nova Friburgo)", "dica": "Pousada, cachoeiras e gastronomia mineira."},
    {"local": "Rio das Ostras - Costazul", "dica": "Feira de artesanato e passeio na lagoa."},
]

sugestao_macae = MACAÉ[semana_ano % len(MACAÉ)]
sugestao_arredores = ARREDORES[semana_ano % len(ARREDORES)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão em Macaé</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_macae['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_macae['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão nos Arredores</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_arredores['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_arredores['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.info("💡 Lembre-se de usar o **Cartão Macaé** nos estabelecimentos parceiros da cidade.")

```


## `ui/pages/06_Autoconhecimento.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()

st.title("🪞 Autoconhecimento")
st.caption("Diário reflexivo e meditação.")

PROMPTS = [
    "O que drenou minha energia hoje e por quê?",
    "Qual pequena vitória eu tive hoje?",
    "O que eu faria diferente se pudesse recomeçar o dia?",
    "Pelo que sou grato neste exato momento?",
    "Qual pensamento negativo eu posso deixar ir embora?",
    "Como eu tratei as pessoas ao meu redor hoje?",
    "O que aprendi sobre mim mesmo nesta semana?",
]

prompt_do_dia = PROMPTS[date.today().toordinal() % len(PROMPTS)]

st.subheader("📝 Diário Reflexivo")
st.markdown(f"**Prompt de hoje:** *{prompt_do_dia}*")

with st.form("form_journal"):
    texto = st.text_area("Sua reflexão:", height=150, placeholder="Escreva livremente...")
    submitted = st.form_submit_button("Salvar e Refletir com IA", use_container_width=True)

if submitted and texto.strip():
    with st.spinner("O Mentor Samurai está refletindo sobre suas palavras..."):
        prompt_ia = f"Atue como um mentor samurai sábio e empático. O usuário escreveu a seguinte reflexão sobre o prompt '{prompt_do_dia}':\n\n'{texto.strip()}'\n\nForneça uma resposta curta (máximo 2 parágrafos) validando os sentimentos dele e oferecendo uma perspectiva focada em disciplina, evolução e paz interior. Fale de forma direta e acolhedora."
        reflexao_ia = ask_gemini(prompt_ia)
        
        execute(
            "INSERT INTO journal_entries (entry_date, prompt, content, ai_reflection) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), prompt_do_dia, texto.strip(), reflexao_ia)
        )
    st.success("Reflexão salva e analisada.")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Meditação Curta")
st.markdown("""
**Respiração Box (5 minutos):**
1. Inspire contando até **4**.
2. Segure a respiração contando até **4**.
3. Expire lentamente contando até **4**.
4. Aguarde contando até **4**.
5. Repita por 5 minutos.
""")

st.divider()
st.subheader("📚 Histórico de Reflexões")

entries = query_all("SELECT * FROM journal_entries ORDER BY entry_date DESC, id DESC LIMIT 5")
if not entries:
    st.info("Nenhuma reflexão registrada ainda.")
else:
    for e in entries:
        with st.expander(f"📅 {e['entry_date']} — {e['prompt']}"):
            st.markdown(f"**Sua reflexão:**\n{e['content']}")
            if e['ai_reflection']:
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 10px; padding: 10px;">
                    <div style="color: #F2F2F2; font-size: 0.9rem; font-style: italic;">
                        <b>Mentor Samurai:</b><br>{e['ai_reflection']}
                    </div>
                </div>""", unsafe_allow_html=True)

```


## `ui/pages/07_Consistencia.py`

```python
"""Consistência — check-in diário, marcação de hábitos e score anti-burnout."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date, timedelta

import streamlit as st

from core.database import execute, query_all, query_one
from services.ai import ask_gemini

today = date.today()
today_iso = today.isoformat()

def calcular_burnout() -> tuple[float, dict]:
    week_ago = (today - timedelta(days=7)).isoformat()

    checkins = query_all("SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?", (week_ago,))
    total_habits = query_one("SELECT COUNT(*) AS c FROM habits WHERE active = 1")["c"] or 0
    logs = query_all("SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,))
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    total = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return total, {
        "avg_energy": avg_energy,
        "avg_stress": avg_stress,
        "avg_sleep": avg_sleep,
        "taxa": taxa,
    }

def classificar_burnout(score: float) -> tuple[str, str]:
    if score < 30:
        return "🟢 Baixo", "#2E7D32"
    if score < 60:
        return "🟡 Médio", "#F9A825"
    if score < 80:
        return "🟠 Alto", "#EF6C00"
    return "🔴 Crítico", "#C62828"

st.title("🎯 Consistência")
st.caption("Disciplina diária é o que forja o samurai.")

st.subheader("📝 Check-in do dia")
existente = query_one("SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,))
MOOD_OPTIONS = ["Ótimo", "Bom", "Neutro", "Cansado", "Estressado", "Ansioso"]
mood_default = (MOOD_OPTIONS.index(existente["mood"]) if existente and existente["mood"] in MOOD_OPTIONS else 2)

with st.form("form_checkin", clear_on_submit=False):
    energy = st.slider("Energia (1–10)", 1, 10, int(existente["energy"]) if existente else 6)
    sleep_hours = st.number_input("Horas de sono", min_value=0.0, max_value=16.0, step=0.5, value=float(existente["sleep_hours"]) if existente else 7.0)
    mood = st.selectbox("Humor", MOOD_OPTIONS, index=mood_default)
    stress = st.slider("Estresse (1–10)", 1, 10, int(existente["stress"]) if existente else 5)
    notes = st.text_area("Notas (opcional)", value=existente["notes"] if existente and existente["notes"] else "")
    submit = st.form_submit_button("💾 Salvar check-in", use_container_width=True)

if submit:
    execute(
        """
        INSERT INTO daily_checkins (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy = excluded.energy, sleep_hours = excluded.sleep_hours, mood = excluded.mood, stress = excluded.stress, notes = excluded.notes
        """,
        (today_iso, energy, sleep_hours, mood, stress, notes or None),
    )
    st.success("[OK] Check-in registrado.")
    st.rerun()

st.divider()
st.subheader("🥋 Hábitos de hoje")
habits = query_all(
    """
    SELECT h.id, h.name, h.pillar, COALESCE(l.done, 0) AS done
    FROM habits h LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1 ORDER BY h.pillar, h.name
    """, (today_iso,),
)
alterou = False
for h in habits:
    novo = st.checkbox(f"**{h['pillar']}** · {h['name']}", value=bool(h["done"]), key=f"habit_{h['id']}")
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """, (h["id"], today_iso, 1 if novo else 0),
        )
        alterou = True
if alterou: st.rerun()

st.divider()
st.subheader("🔥 Score Anti-Burnout (7 dias)")
score, metricas = calcular_burnout()
label, cor = classificar_burnout(score)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color:{cor};">
        <div class="titulo">Risco atual</div>
        <div class="valor" style="color:{cor};">{score:.0f}/100 — {label}</div>
        <div class="detalhe">
            Média energia: {metricas['avg_energy']:.1f} · Sono: {metricas['avg_sleep']:.1f}h · Estresse: {metricas['avg_stress']:.1f} · Hábitos: {metricas['taxa']*100:.0f}%
        </div>
    </div>""", unsafe_allow_html=True,
)
st.progress(min(1.0, score / 100.0))

if score >= 80:
    st.error("⚠️ Risco crítico. Priorize descanso hoje. Nenhum treino vale um colapso.")
elif score >= 60:
    st.warning("Atenção: sinais de sobrecarga. Reduza intensidade e priorize sono.")

st.divider()
st.subheader("🧠 Relatório do Mentor Samurai")
if st.button("📜 Gerar Análise Semanal com IA", use_container_width=True):
    with st.spinner("O Mentor está analisando seus dados da semana..."):
        prompt_ia = f"Atue como um mentor samurai sábio e direto. Aqui estão os dados da semana do usuário:\n- Score de Burnout: {score:.0f}/100\n- Média de Energia: {metricas['avg_energy']:.1f}\n- Média de Sono: {metricas['avg_sleep']:.1f}h\n- Média de Estresse: {metricas['avg_stress']:.1f}\n- Taxa de conclusão de hábitos: {metricas['taxa']*100:.0f}%\n\nEscreva um relatório semanal curto (max 3 parágrafos), motivador e realista. Se o burnout estiver alto (>60), aconselhe descanso. Se estiver baixo, parabenize e incentive a manter a disciplina. Mantenha o tom sério, mas encorajador."
        relatorio_ia = ask_gemini(prompt_ia)
        
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 15px;">
            <div class="titulo">Visão do Mestre</div>
            <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{relatorio_ia}</div>
        </div>""", unsafe_allow_html=True)

```


## `ui/pages/08_Religiao.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("🕊️ Religião")
st.caption("Cultivando a fé e a conexão com Deus.")

hoje = date.today().isoformat()

# --- HÁBITOS RELIGIOSOS ---
st.subheader("🙏 Práticas Espirituais")

habits = query_all(
    """
    SELECT h.id, h.name, COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.pillar = 'Religião' AND h.active = 1
    ORDER BY h.name
    """,
    (hoje,),
)

alterou = False
for h in habits:
    novo = st.checkbox(h["name"], value=bool(h["done"]), key=f"rel_{h['id']}")
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """,
            (h["id"], hoje, 1 if novo else 0),
        )
        alterou = True

if alterou:
    st.rerun()

st.divider()

# --- VERSÍCULO DO DIA ---
st.subheader("📖 Versículo do Dia")

VERSICULOS = [
    ("Salmos 23:1", "O Senhor é o meu pastor; nada me faltará."),
    ("Filipenses 4:13", "Posso todas as coisas naquele que me fortalece."),
    ("Josué 1:9", "Sê forte e corajoso; não temas, nem te espantes, porque o Senhor, teu Deus, é contigo."),
    ("Provérbios 3:5", "Confia no Senhor de todo o teu coração e não te estribes no teu próprio entendimento."),
    ("Isaías 41:10", "Não temas, porque eu sou contigo; não te assombres, porque eu sou o teu Deus."),
    ("Salmos 119:105", "Lâmpada para os meus pés é tua palavra e luz, para o meu caminho."),
    ("Romanos 8:28", "E sabemos que todas as coisas contribuem juntamente para o bem daqueles que amam a Deus."),
]

# Escolhe o versículo baseado no dia do ano
v = VERSICULOS[date.today().toordinal() % len(VERSICULOS)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
        <div class="titulo">{v[0]}</div>
        <div class="valor" style="font-size: 1.1rem; font-style: italic; color: #F2F2F2;">"{v[1]}"</div>
    </div>""",
    unsafe_allow_html=True,
)

st.divider()
st.subheader("✍️ Diário Espiritual")

with st.form("form_diario_espiritual"):
    texto = st.text_area("O que Deus falou com você hoje?", placeholder="Escreva uma oração, um agradecimento ou um aprendizado...")
    submitted = st.form_submit_button("Salvar no Diário", use_container_width=True)

if submitted and texto.strip():
    execute(
        "INSERT INTO journal_entries (entry_date, prompt, content) VALUES (?, ?, ?)",
        (date.today().isoformat(), "Diário Espiritual", texto.strip())
    )
    st.success("Registro salvo.")
    st.rerun()

```


## `ui/pages/09_Biblia.py`

```python
import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db

init_db()

st.title("📖 Bíblia")
st.caption("Plano de leitura em 1 ano — Almeida Corrigida Fiel (ACF)")

proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")

if not proximo:
    st.success("🎉 Parabéns! Você concluiu a leitura da Bíblia em 1 ano!")
    st.balloons()
else:
    day = proximo["day"]
    st.subheader(f"Dia {day} de 365")

    plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
    if plano:
        start_id = plano["start_verse_id"]
        end_id = plano["end_verse_id"]

        versiculos = query_all(
            "SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id",
            (start_id, end_id)
        )

        if versiculos:
            primeiro = versiculos[0]
            ultimo = versiculos[-1]
            
            if primeiro["book_name"] == ultimo["book_name"]:
                if primeiro["chapter"] == ultimo["chapter"]:
                    ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']}-{ultimo['verse']}"
                else:
                    ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']} a {ultimo['chapter']}:{ultimo['verse']}"
            else:
                ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']} a {ultimo['book_name']} {ultimo['chapter']}:{ultimo['verse']}"

            st.markdown(f"**Leitura de hoje:** {ref}")

            # Monta o texto formatado de forma segura (sem f-string)
            texto_limpo = ""
            for v in versiculos:
                # Escapa chaves para não quebrar o HTML/Markdown
                safe_text = str(v['text']).replace("{", "{{").replace("}", "}}")
                texto_limpo += f"**{v['verse']}** {safe_text}  \n"

            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 500px; overflow-y: auto;">
                    <div style="color: #F2F2F2; font-size: 1rem; line-height: 1.8;">
                        {texto_limpo}
                    </div>
                </div>""",
                unsafe_allow_html=True
            )

            if st.button("✅ Confirmar Leitura e Avançar", use_container_width=True):
                execute("UPDATE reading_progress SET completed = 1 WHERE day = ?", (day,))
                st.success(f"Leitura do Dia {day} concluída! Avançando...")
                st.rerun()
        else:
            st.error("Erro ao carregar os versículos. O plano pode estar corrompido.")
    else:
        st.error(f"Plano para o dia {day} não encontrado.")

```


## `ui/pages/__init__.py`

```python
"""Páginas do Projeto Samurai."""

```

```


## `requirements.txt`

```text
streamlit>=1.38.0
pandas>=2.2.0
yfinance>=0.2.40
requests>=2.31.0
feedparser>=6.0.10
google-generativeai>=0.5.0
pymupdf>=1.24.0

```


## `services/__init__.py`

```python
"""Serviços externos (IA, yfinance, notícias, etc.)."""

```


## `services/ai.py`

```python
import google.generativeai as genai
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

def get_api_key() -> str:
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("gemini_api_key", "")
        except Exception:
            pass
    return ""

def ask_gemini(prompt: str) -> str:
    api_key = get_api_key()
    if not api_key or api_key == "COLE_SUA_CHAVE_AQUI":
        return "⚠️ API Key não configurada. Abra o arquivo 'config.json' na raiz do projeto e insira sua chave do Gemini."
    
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-3.5-flash-lite')  # MODELO FIXADO - NÃO ALTERAR
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Erro na IA: {str(e)}"

def ask_gemini_vision(image_bytes: bytes, prompt: str) -> str:
    api_key = get_api_key()
    if not api_key or api_key == "COLE_SUA_CHAVE_AQUI":
        return "⚠️ API Key não configurada."
    
    genai.configure(api_key=api_key)
    try:
        # Usamos o 1.5-flash para visão pois ele é excelente em OCR
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])
        return response.text
    except Exception as e:
        return f"⚠️ Erro na IA (Visão): {str(e)}"

```


## `ui/__init__.py`

```python
"""Camada de interface Streamlit."""

```


## `ui/pages/00_Home.py`

```python
"""Dojo — resumo do dia, hábitos pendentes e energia."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date

import streamlit as st

from core.database import query_all, query_one

today_iso = date.today().isoformat()

st.title("🏯 Dojo")
DIAS_SEMANA = {
    "Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"
}
dia_ingles = date.today().strftime('%A')
dia_pt = DIAS_SEMANA.get(dia_ingles, dia_ingles)
st.caption(f"Hoje é {dia_pt}, {date.today().strftime('%d/%m/%Y')}")

checkin = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

col1, col2, col3 = st.columns(3)
if checkin:
    with col1:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Energia</div>
                <div class="valor">{checkin['energy']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Sono</div>
                <div class="valor">{checkin['sleep_hours']}h</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Estresse</div>
                <div class="valor">{checkin['stress']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("⚡ Nenhum check-in hoje. Vá em **Consistência** e registre sua energia.")

st.subheader("🎯 Hábitos pendentes hoje")

rows = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

pendentes = [r for r in rows if not r["done"]]
concluidos = [r for r in rows if r["done"]]

if not pendentes:
    st.success("🥋 Todos os hábitos foram cumpridos. Disciplina exemplar.")
else:
    for r in pendentes:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">{r['pillar']}</div>
                <div class="valor" style="font-size:1.1rem;">{r['name']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if concluidos:
    st.divider()
    st.caption(f"✅ {len(concluidos)} hábito(s) já cumprido(s) hoje")

st.divider()
if st.button("📝 Fazer check-in diário agora", use_container_width=True):
    st.switch_page("ui/pages/07_Consistencia.py")

```


## `ui/pages/01_Corpo.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()  # Garante que a tabela exista antes de qualquer consulta

st.title("💪 Corpo")
st.caption("Treino calistênico progressivo e mobilidade.")
hoje = date.today().isoformat()

EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

st.subheader("🥋 Treino de Hoje")
st.write("Registre suas repetições para acompanhar sua evolução.")

# Busca treinos de hoje
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}", label_visibility="collapsed")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}", label_visibility="collapsed")
            
            novos_valores[ex] = {"reps": reps, "sets": sets}

    submitted = st.form_submit_button("💾 Salvar Treino", use_container_width=True)

if submitted:
    for ex, val in novos_valores.items():
        if val["reps"] > 0:
            execute(
                """
                INSERT INTO exercise_logs (log_date, exercise_name, reps, sets)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(log_date, exercise_name) DO UPDATE SET
                    reps = excluded.reps, sets = excluded.sets
                """,
                (hoje, ex, val["reps"], val["sets"])
            )
    st.success("[OK] Treino registrado com sucesso!")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Mobilidade")
mob = query_all("SELECT done FROM habit_logs WHERE log_date = ? AND habit_id = (SELECT id FROM habits WHERE name = 'Mobilidade')", (hoje,))
mob_done = bool(mob[0]["done"]) if mob else False

nova_mob = st.checkbox("Concluí os 10 min de mobilidade hoje", value=mob_done)
if nova_mob != mob_done:
    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done)
        VALUES ((SELECT id FROM habits WHERE name = 'Mobilidade'), ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (hoje, 1 if nova_mob else 0)
    )
    st.rerun()

```


## `ui/pages/02_Mente.py`

```python
import streamlit as st
import sys
from pathlib import Path
import re
import fitz  # PyMuPDF

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
    
    # A opção mágica para PDFs de editoras
    usar_ocr = st.checkbox("Usar OCR com IA (Recomendado se o texto sair embaralhado)", value=False, 
                           help="O app vai transformar as páginas em imagens e pedir para o Gemini ler. Demora um pouco mais, mas o texto fica perfeito.")
    
    if uploaded_file and st.button("Processar PDF e Criar Plano"):
        with st.spinner("Extraindo texto..."):
            try:
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                full_text = ""
                
                if usar_ocr:
                    st.warning("A IA está lendo cada página. Por favor, aguarde (pode levar alguns minutos)...")
                    progresso = st.progress(0)
                    total_paginas = len(doc)
                    
                    for i, page in enumerate(doc):
                        # Converte a página em imagem
                        pix = page.get_pixmap(dpi=150) # 150 DPI é suficiente para ler texto
                        img_bytes = pix.tobytes("jpeg")
                        
                        # Pede para a IA extrair o texto
                        prompt = "Extraia exatamente o texto desta imagem, mantendo a pontuação e parágrafos. Não adicione comentários, retorne apenas o texto do livro."
                        texto_pagina = ask_gemini_vision(img_bytes, prompt)
                        
                        # Remove mensagens de erro da IA caso ocorram
                        if "⚠️ Erro na IA" not in texto_pagina and "⚠️ API Key" not in texto_pagina:
                            full_text += texto_pagina + " "
                            
                        progresso.progress((i + 1) / total_paginas)
                else:
                    # Método tradicional (para PDFs normais)
                    for page in doc:
                        extracted = page.get_text("text")
                        if extracted:
                            full_text += extracted + " "
                
                # Limpeza básica
                full_text = re.sub(r'\s+', ' ', full_text)
                palavras = full_text.split()
                
                if len(palavras) < 100:
                    st.error("O PDF não pôde ser lido. Verifique se a API Key está configurada ou se o PDF é válido.")
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
                    import time
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
                st.session_state["resumo_pdf"] = "" # Limpa o resumo anterior
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

```


## `ui/pages/03_Informacao.py`

```python
import streamlit as st
import sys
from pathlib import Path
import yfinance as yf
import requests
import feedparser

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db

init_db()

st.title("📰 Informação")
st.caption("Mundo, Brasil, Macaé, Legislativo e Finanças.")

# --- FINANÇAS ---
st.subheader("📈 Finanças (Tempo Real)")
col1, col2, col3 = st.columns(3)
tickers = {"Dólar": "BRL=X", "IBOVESPA": "^BVSP", "Bitcoin": "BTC-USD"}
cols = [col1, col2, col3]

for i, (nome, ticker) in enumerate(tickers.items()):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            preco = data['Close'].iloc[-1]
            with cols[i]:
                st.markdown(
                    f"""<div class="samurai-card">
                        <div class="titulo">{nome}</div>
                        <div class="valor">R$ {preco:,.2f}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    except Exception:
        with cols[i]:
            st.error(f"Erro ao carregar {nome}")

st.divider()

# --- NOTÍCIAS ---
st.subheader("🗞️ Últimas Notícias (G1)")
try:
    url = "https://g1.globo.com/rss/g1/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() # Levanta um erro se a requisição falhar
    
    feed = feedparser.parse(response.content)
    
    if feed.entries:
        for entry in feed.entries[:5]:
            st.markdown(f"- [{entry.title}]({entry.link})")
    else:
        st.warning("O feed de notícias está vazio no momento.")
except requests.exceptions.RequestException:
    st.warning("Não foi possível carregar as notícias (servidor do G1 fora do ar ou bloqueando a conexão).")
except Exception as e:
    st.warning("Erro inesperado ao carregar as notícias.")

st.divider()
st.subheader("⚖️ Legislativo")
st.info("🚧 Integração com APIs do Senado, Câmara, ALERJ e Câmara de Macaé será implementada na Sprint 4.")

```


## `ui/pages/04_Patrimonio.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("💎 Patrimônio")
st.caption("Ações, notícias e controle de gastos.")

# --- AÇÕES ---
st.subheader("📊 Ações e FIIs")
col1, col2 = st.columns([2, 1])
with col1:
    ticker_input = st.text_input("Digite o ticker (ex: PETR4.SA, VALE3.SA, HGLG11.SA):", value="PETR4.SA")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    buscar = st.button("Buscar Cotação", use_container_width=True)

if buscar or ticker_input:
    try:
        ticker = yf.Ticker(ticker_input)
        data = ticker.history(period="5d")
        if not data.empty:
            preco_atual = data['Close'].iloc[-1]
            variacao = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
            
            cor = "#4CAF50" if variacao >= 0 else "#F44336"
            
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: {cor};">
                    <div class="titulo">{ticker_input}</div>
                    <div class="valor">R$ {preco_atual:.2f}</div>
                    <div class="detalhe" style="color: {cor};">Variação (5d): {variacao:+.2f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )
            
            with st.expander("Ver Notícias do Ticker"):
                noticias = ticker.news
                if noticias:
                    for n in noticias[:3]:
                        st.markdown(f"- [{n['title']}]({n['link']})")
                else:
                    st.write("Nenhuma notícia recente encontrada.")
        else:
            st.error("Ticker não encontrado ou sem dados.")
    except Exception:
        st.error("Erro ao buscar dados. Verifique o ticker digitado.")

st.divider()

# --- GASTOS ---
st.subheader("💸 Registro de Gastos")

with st.form("form_gasto"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        descricao = st.text_input("Descrição")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
    with col3:
        categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Outros"])
    
    submitted = st.form_submit_button("Registrar Gasto", use_container_width=True)

if submitted:
    if descricao and valor > 0:
        execute(
            "INSERT INTO expenses (expense_date, description, amount, category) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), descricao, valor, categoria)
        )
        st.success("Gasto registrado!")
        st.rerun()
    else:
        st.error("Preencha a descrição e um valor maior que zero.")

# Listar gastos
gastos = query_all("SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 10")
if gastos:
    st.markdown("### Últimos Gastos")
    for g in gastos:
        st.markdown(
            f"""<div class="samurai-card" style="border-left-color: #171717; padding: 10px;">
                <div style="display: flex; justify-content: space-between; color: #CCC;">
                    <span>{g['description']}</span>
                    <span>R$ {g['amount']:.2f} ({g['category']})</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )

```


## `ui/pages/05_Descanso.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

st.title("🌿 Descanso & Lazer")
st.caption("Sugestões semanais para recarregar as energias.")

# Pegar a semana do ano para alternar as sugestões
semana_ano = date.today().isocalendar()[1]

MACAÉ = [
    {"local": "Praia dos Cavaleiros", "dica": "Caminhada na orla e um açaí no fim da tarde."},
    {"local": "Lagoa de Imboassica", "dica": "Passeio de caiaque ou pedalinho, ótimo para desacelerar."},
    {"local": "Pico do Frade", "dica": "Trilha leve com vista panorâmica da cidade. Leve água."},
    {"local": "Praia do Pecado", "dica": "Lugar mais reservado para ler um livro e relaxar."},
    {"local": "Parque Municipal da Lagoa", "dica": "Caminhada e contato com a natureza."},
]

ARREDORES = [
    {"local": "Búzios - Rua das Pedras", "dica": "Almoço, caminhada e fim de tarde na praia de Geribá."},
    {"local": "Cabo Frio - Praia do Forte", "dica": "Visitar as dunas e a Fortaleza de São Mateus."},
    {"local": "Arraial do Cabo - Pontal do Atalaia", "dica": "Levar água e preparar para o visual mais bonito da região."},
    {"local": "Lumiar (Nova Friburgo)", "dica": "Pousada, cachoeiras e gastronomia mineira."},
    {"local": "Rio das Ostras - Costazul", "dica": "Feira de artesanato e passeio na lagoa."},
]

sugestao_macae = MACAÉ[semana_ano % len(MACAÉ)]
sugestao_arredores = ARREDORES[semana_ano % len(ARREDORES)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão em Macaé</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_macae['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_macae['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-bottom: 20px;">
        <div class="titulo" style="color: #F2F2F2; font-size: 0.9rem;">Sugestão nos Arredores</div>
        <div class="valor" style="font-size: 1.4rem;">{sugestao_arredores['local']}</div>
        <div class="detalhe" style="font-size: 1rem;">{sugestao_arredores['dica']}</div>
    </div>""",
    unsafe_allow_html=True,
)

st.info("💡 Lembre-se de usar o **Cartão Macaé** nos estabelecimentos parceiros da cidade.")

```


## `ui/pages/06_Autoconhecimento.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()

st.title("🪞 Autoconhecimento")
st.caption("Diário reflexivo e meditação.")

PROMPTS = [
    "O que drenou minha energia hoje e por quê?",
    "Qual pequena vitória eu tive hoje?",
    "O que eu faria diferente se pudesse recomeçar o dia?",
    "Pelo que sou grato neste exato momento?",
    "Qual pensamento negativo eu posso deixar ir embora?",
    "Como eu tratei as pessoas ao meu redor hoje?",
    "O que aprendi sobre mim mesmo nesta semana?",
]

prompt_do_dia = PROMPTS[date.today().toordinal() % len(PROMPTS)]

st.subheader("📝 Diário Reflexivo")
st.markdown(f"**Prompt de hoje:** *{prompt_do_dia}*")

with st.form("form_journal"):
    texto = st.text_area("Sua reflexão:", height=150, placeholder="Escreva livremente...")
    submitted = st.form_submit_button("Salvar e Refletir com IA", use_container_width=True)

if submitted and texto.strip():
    with st.spinner("O Mentor Samurai está refletindo sobre suas palavras..."):
        prompt_ia = f"Atue como um mentor samurai sábio e empático. O usuário escreveu a seguinte reflexão sobre o prompt '{prompt_do_dia}':\n\n'{texto.strip()}'\n\nForneça uma resposta curta (máximo 2 parágrafos) validando os sentimentos dele e oferecendo uma perspectiva focada em disciplina, evolução e paz interior. Fale de forma direta e acolhedora."
        reflexao_ia = ask_gemini(prompt_ia)
        
        execute(
            "INSERT INTO journal_entries (entry_date, prompt, content, ai_reflection) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), prompt_do_dia, texto.strip(), reflexao_ia)
        )
    st.success("Reflexão salva e analisada.")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Meditação Curta")
st.markdown("""
**Respiração Box (5 minutos):**
1. Inspire contando até **4**.
2. Segure a respiração contando até **4**.
3. Expire lentamente contando até **4**.
4. Aguarde contando até **4**.
5. Repita por 5 minutos.
""")

st.divider()
st.subheader("📚 Histórico de Reflexões")

entries = query_all("SELECT * FROM journal_entries ORDER BY entry_date DESC, id DESC LIMIT 5")
if not entries:
    st.info("Nenhuma reflexão registrada ainda.")
else:
    for e in entries:
        with st.expander(f"📅 {e['entry_date']} — {e['prompt']}"):
            st.markdown(f"**Sua reflexão:**\n{e['content']}")
            if e['ai_reflection']:
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 10px; padding: 10px;">
                    <div style="color: #F2F2F2; font-size: 0.9rem; font-style: italic;">
                        <b>Mentor Samurai:</b><br>{e['ai_reflection']}
                    </div>
                </div>""", unsafe_allow_html=True)

```


## `ui/pages/07_Consistencia.py`

```python
"""Consistência — check-in diário, marcação de hábitos e score anti-burnout."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date, timedelta

import streamlit as st

from core.database import execute, query_all, query_one
from services.ai import ask_gemini

today = date.today()
today_iso = today.isoformat()

def calcular_burnout() -> tuple[float, dict]:
    week_ago = (today - timedelta(days=7)).isoformat()

    checkins = query_all("SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?", (week_ago,))
    total_habits = query_one("SELECT COUNT(*) AS c FROM habits WHERE active = 1")["c"] or 0
    logs = query_all("SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,))
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    total = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return total, {
        "avg_energy": avg_energy,
        "avg_stress": avg_stress,
        "avg_sleep": avg_sleep,
        "taxa": taxa,
    }

def classificar_burnout(score: float) -> tuple[str, str]:
    if score < 30:
        return "🟢 Baixo", "#2E7D32"
    if score < 60:
        return "🟡 Médio", "#F9A825"
    if score < 80:
        return "🟠 Alto", "#EF6C00"
    return "🔴 Crítico", "#C62828"

st.title("🎯 Consistência")
st.caption("Disciplina diária é o que forja o samurai.")

st.subheader("📝 Check-in do dia")
existente = query_one("SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,))
MOOD_OPTIONS = ["Ótimo", "Bom", "Neutro", "Cansado", "Estressado", "Ansioso"]
mood_default = (MOOD_OPTIONS.index(existente["mood"]) if existente and existente["mood"] in MOOD_OPTIONS else 2)

with st.form("form_checkin", clear_on_submit=False):
    energy = st.slider("Energia (1–10)", 1, 10, int(existente["energy"]) if existente else 6)
    sleep_hours = st.number_input("Horas de sono", min_value=0.0, max_value=16.0, step=0.5, value=float(existente["sleep_hours"]) if existente else 7.0)
    mood = st.selectbox("Humor", MOOD_OPTIONS, index=mood_default)
    stress = st.slider("Estresse (1–10)", 1, 10, int(existente["stress"]) if existente else 5)
    notes = st.text_area("Notas (opcional)", value=existente["notes"] if existente and existente["notes"] else "")
    submit = st.form_submit_button("💾 Salvar check-in", use_container_width=True)

if submit:
    execute(
        """
        INSERT INTO daily_checkins (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy = excluded.energy, sleep_hours = excluded.sleep_hours, mood = excluded.mood, stress = excluded.stress, notes = excluded.notes
        """,
        (today_iso, energy, sleep_hours, mood, stress, notes or None),
    )
    st.success("[OK] Check-in registrado.")
    st.rerun()

st.divider()
st.subheader("🥋 Hábitos de hoje")
habits = query_all(
    """
    SELECT h.id, h.name, h.pillar, COALESCE(l.done, 0) AS done
    FROM habits h LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1 ORDER BY h.pillar, h.name
    """, (today_iso,),
)
alterou = False
for h in habits:
    novo = st.checkbox(f"**{h['pillar']}** · {h['name']}", value=bool(h["done"]), key=f"habit_{h['id']}")
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """, (h["id"], today_iso, 1 if novo else 0),
        )
        alterou = True
if alterou: st.rerun()

st.divider()
st.subheader("🔥 Score Anti-Burnout (7 dias)")
score, metricas = calcular_burnout()
label, cor = classificar_burnout(score)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color:{cor};">
        <div class="titulo">Risco atual</div>
        <div class="valor" style="color:{cor};">{score:.0f}/100 — {label}</div>
        <div class="detalhe">
            Média energia: {metricas['avg_energy']:.1f} · Sono: {metricas['avg_sleep']:.1f}h · Estresse: {metricas['avg_stress']:.1f} · Hábitos: {metricas['taxa']*100:.0f}%
        </div>
    </div>""", unsafe_allow_html=True,
)
st.progress(min(1.0, score / 100.0))

if score >= 80:
    st.error("⚠️ Risco crítico. Priorize descanso hoje. Nenhum treino vale um colapso.")
elif score >= 60:
    st.warning("Atenção: sinais de sobrecarga. Reduza intensidade e priorize sono.")

st.divider()
st.subheader("🧠 Relatório do Mentor Samurai")
if st.button("📜 Gerar Análise Semanal com IA", use_container_width=True):
    with st.spinner("O Mentor está analisando seus dados da semana..."):
        prompt_ia = f"Atue como um mentor samurai sábio e direto. Aqui estão os dados da semana do usuário:\n- Score de Burnout: {score:.0f}/100\n- Média de Energia: {metricas['avg_energy']:.1f}\n- Média de Sono: {metricas['avg_sleep']:.1f}h\n- Média de Estresse: {metricas['avg_stress']:.1f}\n- Taxa de conclusão de hábitos: {metricas['taxa']*100:.0f}%\n\nEscreva um relatório semanal curto (max 3 parágrafos), motivador e realista. Se o burnout estiver alto (>60), aconselhe descanso. Se estiver baixo, parabenize e incentive a manter a disciplina. Mantenha o tom sério, mas encorajador."
        relatorio_ia = ask_gemini(prompt_ia)
        
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 15px;">
            <div class="titulo">Visão do Mestre</div>
            <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{relatorio_ia}</div>
        </div>""", unsafe_allow_html=True)

```


## `ui/pages/08_Religiao.py`

```python
import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("🕊️ Religião")
st.caption("Cultivando a fé e a conexão com Deus.")

hoje = date.today().isoformat()

# --- HÁBITOS RELIGIOSOS ---
st.subheader("🙏 Práticas Espirituais")

habits = query_all(
    """
    SELECT h.id, h.name, COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.pillar = 'Religião' AND h.active = 1
    ORDER BY h.name
    """,
    (hoje,),
)

alterou = False
for h in habits:
    novo = st.checkbox(h["name"], value=bool(h["done"]), key=f"rel_{h['id']}")
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """,
            (h["id"], hoje, 1 if novo else 0),
        )
        alterou = True

if alterou:
    st.rerun()

st.divider()

# --- VERSÍCULO DO DIA ---
st.subheader("📖 Versículo do Dia")

VERSICULOS = [
    ("Salmos 23:1", "O Senhor é o meu pastor; nada me faltará."),
    ("Filipenses 4:13", "Posso todas as coisas naquele que me fortalece."),
    ("Josué 1:9", "Sê forte e corajoso; não temas, nem te espantes, porque o Senhor, teu Deus, é contigo."),
    ("Provérbios 3:5", "Confia no Senhor de todo o teu coração e não te estribes no teu próprio entendimento."),
    ("Isaías 41:10", "Não temas, porque eu sou contigo; não te assombres, porque eu sou o teu Deus."),
    ("Salmos 119:105", "Lâmpada para os meus pés é tua palavra e luz, para o meu caminho."),
    ("Romanos 8:28", "E sabemos que todas as coisas contribuem juntamente para o bem daqueles que amam a Deus."),
]

# Escolhe o versículo baseado no dia do ano
v = VERSICULOS[date.today().toordinal() % len(VERSICULOS)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
        <div class="titulo">{v[0]}</div>
        <div class="valor" style="font-size: 1.1rem; font-style: italic; color: #F2F2F2;">"{v[1]}"</div>
    </div>""",
    unsafe_allow_html=True,
)

st.divider()
st.subheader("✍️ Diário Espiritual")

with st.form("form_diario_espiritual"):
    texto = st.text_area("O que Deus falou com você hoje?", placeholder="Escreva uma oração, um agradecimento ou um aprendizado...")
    submitted = st.form_submit_button("Salvar no Diário", use_container_width=True)

if submitted and texto.strip():
    execute(
        "INSERT INTO journal_entries (entry_date, prompt, content) VALUES (?, ?, ?)",
        (date.today().isoformat(), "Diário Espiritual", texto.strip())
    )
    st.success("Registro salvo.")
    st.rerun()

```


## `ui/pages/09_Biblia.py`

```python
import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db

init_db()

st.title("📖 Bíblia")
st.caption("Plano de leitura em 1 ano — Almeida Corrigida Fiel (ACF)")

proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")

if not proximo:
    st.success("🎉 Parabéns! Você concluiu a leitura da Bíblia em 1 ano!")
    st.balloons()
else:
    day = proximo["day"]
    st.subheader(f"Dia {day} de 365")

    plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
    if plano:
        start_id = plano["start_verse_id"]
        end_id = plano["end_verse_id"]

        versiculos = query_all(
            "SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id",
            (start_id, end_id)
        )

        if versiculos:
            primeiro = versiculos[0]
            ultimo = versiculos[-1]
            
            if primeiro["book_name"] == ultimo["book_name"]:
                if primeiro["chapter"] == ultimo["chapter"]:
                    ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']}-{ultimo['verse']}"
                else:
                    ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']} a {ultimo['chapter']}:{ultimo['verse']}"
            else:
                ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']} a {ultimo['book_name']} {ultimo['chapter']}:{ultimo['verse']}"

            st.markdown(f"**Leitura de hoje:** {ref}")

            # Monta o texto formatado de forma segura (sem f-string)
            texto_limpo = ""
            for v in versiculos:
                # Escapa chaves para não quebrar o HTML/Markdown
                safe_text = str(v['text']).replace("{", "{{").replace("}", "}}")
                texto_limpo += f"**{v['verse']}** {safe_text}  \n"

            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 500px; overflow-y: auto;">
                    <div style="color: #F2F2F2; font-size: 1rem; line-height: 1.8;">
                        {texto_limpo}
                    </div>
                </div>""",
                unsafe_allow_html=True
            )

            if st.button("✅ Confirmar Leitura e Avançar", use_container_width=True):
                execute("UPDATE reading_progress SET completed = 1 WHERE day = ?", (day,))
                st.success(f"Leitura do Dia {day} concluída! Avançando...")
                st.rerun()
        else:
            st.error("Erro ao carregar os versículos. O plano pode estar corrompido.")
    else:
        st.error(f"Plano para o dia {day} não encontrado.")

```


## `ui/pages/__init__.py`

```python
"""Páginas do Projeto Samurai."""

```
