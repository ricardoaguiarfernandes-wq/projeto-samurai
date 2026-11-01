"""
melhoria.py — Corrige o ImportError da Bíblia.
Reescreve o core/schema.py garantindo a função setup_biblia e todas as tabelas.
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
PADROES_SECRETOS = [
    re.compile(r"AQ\.Ab8RN6[A-Za-z0-9_\-]{20,}"),
    re.compile(r"postgresql://[^:\s]+:[^@\s]+@"),
]
ARQUIVOS_PROIBIDOS = {"config.json", ".env", "secrets.toml"}

# =============================================================================
# CONTEÚDO DO SCHEMA.PY (COM SETUP_BIBLIA GARANTIDO)
# =============================================================================
NOVO_SCHEMA = '''"""
Criação das tabelas e seed inicial.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

import requests
from core.database import execute, query_one, query_all

def get_ddl():
    is_pg = False
    try:
        import streamlit as st
        is_pg = "SUPABASE_URL" in st.secrets
    except Exception: pass

    ddl_base = [
        """CREATE TABLE IF NOT EXISTS habits (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, pillar TEXT NOT NULL, description TEXT, active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT (datetime('now')));""",
        """CREATE TABLE IF NOT EXISTS habit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER NOT NULL, log_date TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, notes TEXT, FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE, UNIQUE (habit_id, log_date));""",
        """CREATE TABLE IF NOT EXISTS daily_checkins (id INTEGER PRIMARY KEY AUTOINCREMENT, checkin_date TEXT NOT NULL UNIQUE, energy INTEGER NOT NULL, sleep_hours REAL NOT NULL, mood TEXT, stress INTEGER NOT NULL, notes TEXT);""",
        """CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, expense_date TEXT NOT NULL, description TEXT NOT NULL, amount REAL NOT NULL, category TEXT, notes TEXT);""",
        """CREATE TABLE IF NOT EXISTS journal_entries (id INTEGER PRIMARY KEY AUTOINCREMENT, entry_date TEXT NOT NULL, prompt TEXT, content TEXT NOT NULL, ai_reflection TEXT);""",
        """CREATE TABLE IF NOT EXISTS book_progress (id INTEGER PRIMARY KEY AUTOINCREMENT, book_title TEXT NOT NULL UNIQUE, current_page INTEGER NOT NULL DEFAULT 0, total_pages INTEGER NOT NULL DEFAULT 0, notes TEXT, last_update TEXT NOT NULL DEFAULT (datetime('now')));""",
        """CREATE TABLE IF NOT EXISTS exercise_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, log_date TEXT NOT NULL, exercise_name TEXT NOT NULL, reps INTEGER NOT NULL DEFAULT 0, sets INTEGER NOT NULL DEFAULT 1, notes TEXT, UNIQUE (log_date, exercise_name));""",
        """CREATE TABLE IF NOT EXISTS book_chunks (id INTEGER PRIMARY KEY AUTOINCREMENT, book_title TEXT NOT NULL, chunk_index INTEGER NOT NULL, text_content TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0, UNIQUE (book_title, chunk_index));""",
        """CREATE TABLE IF NOT EXISTS bible_verses (id INTEGER PRIMARY KEY AUTOINCREMENT, book_name TEXT NOT NULL, book_abbrev TEXT, chapter INTEGER NOT NULL, verse INTEGER NOT NULL, text TEXT NOT NULL, word_count INTEGER NOT NULL);""",
        """CREATE TABLE IF NOT EXISTS reading_plan (day INTEGER PRIMARY KEY, start_verse_id INTEGER, end_verse_id INTEGER);""",
        """CREATE TABLE IF NOT EXISTS reading_progress (day INTEGER PRIMARY KEY, completed INTEGER DEFAULT 0);""",
        """CREATE TABLE IF NOT EXISTS newsletters_inbox (id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT NOT NULL, sender TEXT NOT NULL, content TEXT NOT NULL, received_at TEXT NOT NULL DEFAULT (datetime('now')));""",
        """CREATE TABLE IF NOT EXISTS portfolio (id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT NOT NULL UNIQUE, quantity INTEGER NOT NULL, average_price REAL NOT NULL);""",
        "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
        "CREATE INDEX IF NOT EXISTS idx_checkins_date ON daily_checkins(checkin_date);",
        "CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date);",
    ]

    if is_pg:
        return [d.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY").replace("datetime('now')", "CURRENT_TIMESTAMP") for d in ddl_base]
    return ddl_base

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

def setup_biblia():
    """Baixa e popula a Bíblia se estiver vazia."""
    count = query_one("SELECT COUNT(*) AS c FROM bible_verses")["c"]
    if count == 0:
        url = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/pt_acf.json"
        try:
            response = requests.get(url, timeout=30)
            data = response.json()
            for book in data:
                for chap_idx, chapter in enumerate(book["chapters"], start=1):
                    for verse_idx, verse_text in enumerate(chapter, start=1):
                        execute("INSERT INTO bible_verses (book_name, book_abbrev, chapter, verse, text, word_count) VALUES (?, ?, ?, ?, ?, ?)", (book["name"], book["abbrev"], chap_idx, verse_idx, verse_text, len(verse_text.split())))
        except Exception as e:
            print(f"Erro ao baixar a Bíblia: {e}")
            return

    count_plan = query_one("SELECT COUNT(*) AS c FROM reading_plan")["c"]
    if count_plan == 0:
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

    count_prog = query_one("SELECT COUNT(*) AS c FROM reading_progress")["c"]
    if count_prog == 0:
        for day in range(1, 366):
            execute("INSERT INTO reading_progress (day, completed) VALUES (?, 0)", (day,))

def init_db() -> None:
    for ddl in get_ddl():
        execute(ddl)
    for name, pillar, desc in SEED_HABITS:
        if not query_one("SELECT id FROM habits WHERE name = ?", (name,)):
            execute("INSERT INTO habits (name, pillar, description) VALUES (?, ?, ?)", (name, pillar, desc))
'''

# =============================================================================
# CORREÇÃO DA BÍBLIA (UI)
# =============================================================================
NOVO_BIBLIA = '''import streamlit as st
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
        setup_biblia()  # Agora a função existe e vai popular tudo!
    st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["📖 Plano Anual", "🇺🇸 Devocional Bilíngue", "🎵 Inglês com Louvores", "🔑 Palavras-Chave (1.500)"])

with tab1:
    proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")
    if not proximo:
        st.success("🎉 Parabéns! Você concluiu a leitura da Bíblia em 1 ano!")
    else:
        day = proximo["day"]
        st.subheader(f"Dia {day} de 365")
        plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
        
        if not plano:
            st.warning("O plano de leitura não foi gerado corretamente.")
            if st.button("🔄 Gerar Plano Agora", use_container_width=True):
                with st.spinner("Gerando (pode levar 1-2 min)..."):
                    setup_biblia()
                st.rerun()
        else:
            versiculos = query_all("SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id", (plano["start_verse_id"], plano["end_verse_id"]))
            if versiculos:
                primeiro = versiculos[0]
                ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']}"
                st.markdown(f"**Leitura de hoje:** {ref}")
                texto_limpo, texto_bruto = "", ""
                for v in versiculos:
                    safe_text = str(v['text']).replace("{", "{{").replace("}", "}}")
                    texto_limpo += f"**{v['verse']}** {safe_text}  \\n"
                    texto_bruto += f"{v['verse']} {v['text']} "
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 300px; overflow-y: auto;">
                    <div style="color: #F2F2F2; font-size: 1rem; line-height: 1.8;">{texto_limpo}</div>
                </div>""", unsafe_allow_html=True)
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

with tab2:
    st.header("Devocional Diário Automático")
    temas = ["Amor ao Próximo", "Integridade e Caráter", "Fé em Tempos Difíceis", "Sabedoria e Decisões", "Gratidão e Contentamento"]
    tema_hoje = temas[date.today().toordinal() % len(temas)]
    st.info(f"**Tema de Hoje:** {tema_hoje}")
    @st.cache_data(ttl=86400, show_spinner=False)
    def gerar_devocional(tema):
        prompt = f"Atue como um mentor cristão bilíngue. Crie um devocional curto sobre o tema '{tema}'. Estrutura: 1. Versículo Base (PT/EN) 2. Reflexão (PT) 3. English Practice."
        return ask_gemini(prompt)
    if st.button("🪄 Gerar Devocional de Hoje", use_container_width=True):
        with st.spinner("Preparando..."):
            dev = gerar_devocional(tema_hoje)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Devocional: {tema_hoje}</div><div style="color: #F2F2F2; white-space: pre-wrap;">{dev}</div></div>""", unsafe_allow_html=True)

with tab3:
    st.header("Aprenda Inglês com Louvores")
    if "louvores" not in st.session_state:
        st.session_state["louvores"] = ["Because He Lives", "How Great Thou Art", "I Speak Jesus", "Holy Forever"]
    with st.expander("➕ Adicionar Novo Louvor"):
        nova = st.text_input("Nome da música:")
        if st.button("Adicionar") and nova:
            st.session_state["louvores"].append(nova)
            st.rerun()
    musica = st.selectbox("Escolha um louvor:", st.session_state["louvores"])
    if st.button("🎵 Analisar Louvor com IA", use_container_width=True):
        with st.spinner("Analisando..."):
            prompt = f"Atue como professor de inglês e teólogo. Analise o louvor '{musica}'. Forneça: 1. Refrão em inglês; 2. 4 palavras-chave; 3. Teologia da música; 4. Explicação gramatical."
            analise = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;"><div class="titulo">Aula Musical: {musica}</div><div style="color: #F2F2F2; white-space: pre-wrap;">{analise}</div></div>""", unsafe_allow_html=True)

with tab4:
    st.header("Plano de Palavras-Chave (Inglês)")
    blocos = {1: "Bloco 1: Fé e Amor", 2: "Bloco 2: Graça e Paz", 3: "Bloco 3: Sabedoria e Luz", 4: "Bloco 4: Força e Coragem", 5: "Bloco 5: Misericórdia e Perdão"}
    bloco_escolhido = st.radio("Selecione o bloco:", list(blocos.values()))
    if st.button("📖 Estudar Versículos do Bloco", use_container_width=True):
        with st.spinner("Buscando..."):
            prompt = f"Atue como guia bilíngue. Gere 3 versículos famosos em inglês e PT contendo palavras do bloco '{bloco_escolhido}'. Inclua referência, texto EN, tradução PT e uma pergunta reflexiva."
            estudo = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000;"><div class="titulo">{bloco_escolhido}</div><div style="color: #F2F2F2; white-space: pre-wrap;">{estudo}</div></div>""", unsafe_allow_html=True)
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
    print("⚔️  CORRIGINDO ERRO CRÍTICO (SCHEMA E BÍBLIA)")
    print("=" * 60)

    # 1. Atualizar core/schema.py
    arq_schema = BASE / "core" / "schema.py"
    try:
        ast.parse(NOVO_SCHEMA)
        arq_schema.write_text(NOVO_SCHEMA, encoding="utf-8")
        print("[OK] core/schema.py corrigido e completo.")
    except SyntaxError as e:
        print(f"[ERRO] Sintaxe em core/schema.py: {e}")
        sys.exit(1)

    # 2. Atualizar ui/pages/09_Biblia.py
    arq_biblia = BASE / "ui" / "pages" / "09_Biblia.py"
    try:
        ast.parse(NOVO_BIBLIA)
        arq_biblia.write_text(NOVO_BIBLIA, encoding="utf-8")
        print("[OK] 09_Biblia.py atualizado.")
    except SyntaxError as e:
        print(f"[ERRO] Sintaxe em 09_Biblia.py: {e}")
        sys.exit(1)

    # 3. Sincronização com GitHub
    print("\n☁️  SINCRONIZANDO COM O SERVIDOR (GitHub)")
    _run(["git", "add", "-A"])
    _run(["git", "rm", "--cached", "PROJETO_SAMURAI*.md"])
    
    try:
        _verificar_stage()
    except RuntimeError as e:
        _run(["git", "reset"])
        print(e)
        sys.exit(1)

    code, out = _run(["git", "commit", "-m", "Fix: Corrige ImportError (setup_biblia) e restaura schema"])
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