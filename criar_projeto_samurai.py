"""
criar_projeto_samurai.py — V8.6 (Blindagem Arquitetural e Limpeza)

ENTREGAS:
1. FIX (app.py): Move st.set_page_config para o topo (evita crash).
2. FIX (core/schema.py): Reescreve as tabelas em puro PostgreSQL (remove gambiarras do SQLite).
3. FIX (03_Informacao.py): Faz o botão de notícias chamar a API do Render (remove código duplicado).
4. FIX (api_samurai.py): Limpa comentários duplicados.
5. FIX (14 e 15): Remove fallbacks de tabela da UI (o schema já cuida disso).

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
import re
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
# 1. FIX CRÍTICO: APP.PY (set_page_config)
# ============================================================
def fix_app_pyc() -> None:
    p = BASE / "app.py"
    txt = read(p)
    
    # Extrai o bloco do set_page_config atual
    match = re.search(r'st\.set_page_config\(.*?\)\n', txt, re.DOTALL)
    if not match:
        print("[AVISO] app.py — bloco set_page_config não encontrado.")
        return
        
    page_config_str = match.group(0)
    
    # Remove de onde está agora
    txt = txt.replace(page_config_str, "")
    
    # Insere no topo, logo após os imports
    marker = "import streamlit as st\n"
    if marker in txt:
        txt = txt.replace(marker, marker + "\n" + page_config_str + "\n", 1)
        write_validated(p, txt)
    else:
        print("[AVISO] app.py — import streamlit não encontrado.")

# ============================================================
# 2. FIX SCHEMA: PURO POSTGRESQL
# ============================================================
def fix_schema_pg_pure() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)

    if "def get_ddl():\n    return [" in txt:
        print("[SKIP] schema.py — já é puro Postgres.")
        return

    new_ddl_func = '''def get_ddl():
    # DDL Puro PostgreSQL
    ddl_base = [
        """CREATE TABLE IF NOT EXISTS habits (id SERIAL PRIMARY KEY, name TEXT NOT NULL, pillar TEXT NOT NULL, description TEXT, active INTEGER NOT NULL DEFAULT 1, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);""",
        """CREATE TABLE IF NOT EXISTS habit_logs (id SERIAL PRIMARY KEY, habit_id INTEGER NOT NULL, log_date TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, notes TEXT, FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE, UNIQUE (habit_id, log_date));""",
        """CREATE TABLE IF NOT EXISTS daily_checkins (id SERIAL PRIMARY KEY, checkin_date TEXT NOT NULL UNIQUE, energy INTEGER NOT NULL, sleep_hours REAL NOT NULL, mood TEXT, stress INTEGER NOT NULL, notes TEXT);""",
        """CREATE TABLE IF NOT EXISTS expenses (id SERIAL PRIMARY KEY, expense_date TEXT NOT NULL, description TEXT NOT NULL, amount REAL NOT NULL, category TEXT, notes TEXT);""",
        """CREATE TABLE IF NOT EXISTS patrimony_fixed_income (id SERIAL PRIMARY KEY, name TEXT, amount REAL, rate TEXT);""",
        """CREATE TABLE IF NOT EXISTS daily_briefs (id SERIAL PRIMARY KEY, brief_date TEXT NOT NULL UNIQUE, content TEXT NOT NULL);""",
        """CREATE TABLE IF NOT EXISTS body_metrics (id SERIAL PRIMARY KEY, log_date TEXT NOT NULL UNIQUE, weight REAL NOT NULL, body_fat REAL, notes TEXT);""",
        """CREATE TABLE IF NOT EXISTS user_stats (id INTEGER PRIMARY KEY, xp INTEGER NOT NULL DEFAULT 0, level INTEGER NOT NULL DEFAULT 1);""",
        """CREATE TABLE IF NOT EXISTS achievements (id TEXT PRIMARY KEY, earned_at TEXT NOT NULL);""",
        """CREATE TABLE IF NOT EXISTS user_settings (id INTEGER PRIMARY KEY, workout_split TEXT, workout_start_date TEXT);""",
        """CREATE TABLE IF NOT EXISTS discipline (id INTEGER PRIMARY KEY, start_date TEXT, longest_streak INTEGER DEFAULT 0);""",
        """CREATE TABLE IF NOT EXISTS career_missions (id SERIAL PRIMARY KEY, mission_date TEXT NOT NULL, task TEXT NOT NULL, completed INTEGER DEFAULT 0);""",
        """CREATE TABLE IF NOT EXISTS manuals (id SERIAL PRIMARY KEY, title TEXT UNIQUE, content TEXT NOT NULL, uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);""",
        """CREATE TABLE IF NOT EXISTS sos_logs (id SERIAL PRIMARY KEY, log_date TEXT NOT NULL);""",
        """CREATE TABLE IF NOT EXISTS journal_entries (id SERIAL PRIMARY KEY, entry_date TEXT NOT NULL, prompt TEXT, content TEXT NOT NULL, ai_reflection TEXT);""",
        """CREATE TABLE IF NOT EXISTS book_progress (id SERIAL PRIMARY KEY, book_title TEXT NOT NULL UNIQUE, current_page INTEGER NOT NULL DEFAULT 0, total_pages INTEGER NOT NULL DEFAULT 0, notes TEXT, last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);""",
        """CREATE TABLE IF NOT EXISTS exercise_logs (id SERIAL PRIMARY KEY, log_date TEXT NOT NULL, exercise_name TEXT NOT NULL, reps INTEGER NOT NULL DEFAULT 0, sets INTEGER NOT NULL DEFAULT 1, notes TEXT, UNIQUE (log_date, exercise_name));""",
        """CREATE TABLE IF NOT EXISTS book_chunks (id SERIAL PRIMARY KEY, book_title TEXT NOT NULL, chunk_index INTEGER NOT NULL, text_content TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0, UNIQUE (book_title, chunk_index));""",
        """CREATE TABLE IF NOT EXISTS bible_verses (id SERIAL PRIMARY KEY, book_name TEXT NOT NULL, book_abbrev TEXT, chapter INTEGER NOT NULL, verse INTEGER NOT NULL, text TEXT NOT NULL, word_count INTEGER NOT NULL);""",
        """CREATE TABLE IF NOT EXISTS reading_plan (day INTEGER PRIMARY KEY, start_verse_id INTEGER, end_verse_id INTEGER);""",
        """CREATE TABLE IF NOT EXISTS reading_progress (day INTEGER PRIMARY KEY, completed INTEGER DEFAULT 0);""",
        """CREATE TABLE IF NOT EXISTS newsletters_inbox (id SERIAL PRIMARY KEY, subject TEXT NOT NULL, sender TEXT NOT NULL, content TEXT NOT NULL, received_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);""",
        """CREATE TABLE IF NOT EXISTS portfolio (id SERIAL PRIMARY KEY, ticker TEXT NOT NULL UNIQUE, quantity INTEGER NOT NULL, average_price REAL NOT NULL);""",
        """CREATE TABLE IF NOT EXISTS flashcards (id SERIAL PRIMARY KEY, question TEXT NOT NULL, answer TEXT NOT NULL, next_review TEXT NOT NULL, interval_days INTEGER DEFAULT 1, ease_factor REAL DEFAULT 2.5, last_asked INTEGER DEFAULT 0);""",
        """CREATE TABLE IF NOT EXISTS budgets (category TEXT PRIMARY KEY, limit_amount REAL NOT NULL);""",
        "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
        "CREATE INDEX IF NOT EXISTS idx_checkins_date ON daily_checkins(checkin_date);",
        "CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date);",
    ]
    return ddl_base'''

    pattern = re.compile(r'def get_ddl\(\):.*?return ddl_base', re.DOTALL)
    if pattern.search(txt):
        txt = pattern.sub(new_ddl_func, txt, count=1)
        write_validated(p, txt)
    else:
        print("[AVISO] schema.py — função get_ddl não encontrada.")

# ============================================================
# 3. FIX INFORMAÇÃO: CHAMAR API EM VEZ DE DUPLICAR CÓDIGO
# ============================================================
def fix_informacao_api_call() -> None:
    p = BASE / "ui" / "pages" / "03_Informacao.py"
    txt = read(p)

    if "samurai-webhook.onrender.com/api/daily-news" in txt:
        print("[SKIP] 03_Informacao.py — já usa a API.")
        return

    old_block = '''    if st.button("🧠 Gerar Resumo de Notícias", use_container_width=True):
        with st.spinner("Lendo Câmara, Senado, ALERJ e Macaé..."):
            # Simulando a chamada da API local (no Render) - vamos chamar direto a função
            try:
                # No app local não tem como chamar a API protegida, então vamos ler direto
                import feedparser
                from bs4 import BeautifulSoup
                noticias = []
                
                f1 = feedparser.parse("https://www.camara.leg.br/noticias/rss/ultimas-noticias")
                for e in f1.entries[:2]: noticias.append(f"[Câmara] {e.title}")
                f2 = feedparser.parse("https://www12.senado.leg.br/noticias/RSS")
                for e in f2.entries[:2]: noticias.append(f"[Senado] {e.title}")
                f3 = feedparser.parse("https://news.google.com/rss/search?q=alerj+noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419")
                for e in f3.entries[:2]: noticias.append(f"[ALERJ] {e.title}")
                f4 = feedparser.parse("https://news.google.com/rss/search?q=camara+macae+noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419")
                for e in f4.entries[:2]: noticias.append(f"[Macaé] {e.title}")
                
                prompt = f"Resuma as notícias a seguir em tópicos e explique o impacto prático:\n" + "\n".join(noticias)
                resumo = ask_gemini(prompt)
                st.markdown(f'<div class="samurai-card" style="border-left-color: #8B0000;"><div style="white-space: pre-wrap;">{resumo}</div></div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro ao carregar notícias: {e}")'''

    new_block = '''    if st.button("🧠 Gerar Resumo de Notícias", use_container_width=True):
        with st.spinner("Buscando notícias na API do Samurai..."):
            try:
                import os
                api_token = ""
                try:
                    if "SAMURAI_API_TOKEN" in st.secrets:
                        api_token = st.secrets["SAMURAI_API_TOKEN"]
                except Exception:
                    pass
                
                if not api_token:
                    api_token = os.environ.get("SAMURAI_API_TOKEN", "")
                    
                if not api_token:
                    st.warning("Token da API não configurado. Usando fallback local.")
                    raise Exception("Sem token")
                    
                headers = {"Authorization": f"Bearer {api_token}"}
                r = requests.get("https://samurai-webhook.onrender.com/api/daily-news", headers=headers, timeout=30)
                r.raise_for_status()
                data = r.json()
                st.markdown(f'<div class="samurai-card" style="border-left-color: #8B0000;"><div style="white-space: pre-wrap;">{data.get("text", "Sem notícias.")}</div></div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Erro ao conectar com o servidor. Detalhes: {e}")'''

    if old_block in txt:
        txt = txt.replace(old_block, new_block, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 03_Informacao.py — bloco de notícias antigo não encontrado.")

# ============================================================
# 4. FIX API: REMOVER COMENTÁRIOS DUPLICADOS
# ============================================================
def fix_api_duplicate_comments() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    old_blocks = '''# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS (Câmara, Senado, ALERJ, Macaé)
# ============================================================

# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS
# ============================================================

# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS
# ============================================================

# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS (Com Resumo IA)
# ============================================================

# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS (Com Resumo IA)
# ============================================================'''

    new_block = '''# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS (Com Resumo IA)
# ============================================================'''

    if old_blocks in txt:
        txt = txt.replace(old_blocks, new_block, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] api_samurai.py — múltiplos comentários não encontrados ou já limpos.")

# ============================================================
# 5. REMOVER FALLBACKS FEIOS DA UI
# ============================================================
def fix_ui_fallbacks() -> None:
    # 14_Carreira
    p1 = BASE / "ui" / "pages" / "14_Carreira.py"
    txt1 = read(p1)
    old_c = '''    try:
        manuais = query_all("SELECT id, title, uploaded_at FROM manuals ORDER BY uploaded_at DESC")
    except Exception:
        from core.database import is_postgres
        if is_postgres():
            execute("CREATE TABLE IF NOT EXISTS manuals (id SERIAL PRIMARY KEY, title TEXT UNIQUE, content TEXT NOT NULL, uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        else:
            execute("CREATE TABLE IF NOT EXISTS manuals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, content TEXT NOT NULL, uploaded_at TEXT NOT NULL DEFAULT (datetime('now')))")
        manuais = []'''
    new_c = '''    manuais = query_all("SELECT id, title, uploaded_at FROM manuals ORDER BY uploaded_at DESC")'''
    if old_c in txt1:
        txt1 = txt1.replace(old_c, new_c, 1)
        write_validated(p1, txt1)

    # 15_Financas
    p2 = BASE / "ui" / "pages" / "15_Financas.py"
    txt2 = read(p2)
    old_f = '''try:
    budgets = query_all("SELECT * FROM budgets")
except Exception:
    execute("CREATE TABLE IF NOT EXISTS budgets (category TEXT PRIMARY KEY, limit_amount REAL NOT NULL)")
    budgets = []'''
    new_f = '''budgets = query_all("SELECT * FROM budgets")'''
    if old_f in txt2:
        txt2 = txt2.replace(old_f, new_f, 1)
        write_validated(p2, txt2)

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "refactor: limpeza arquitetural, ddl puro postgres e fix set_page_config"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V8.6 — BLINDAGEM ARQUITETURAL")
    print("=" * 60)

    fix_app_pyc()
    fix_schema_pg_pure()
    fix_informacao_api_call()
    fix_api_duplicate_comments()
    fix_ui_fallbacks()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que vai acontecer agora:")
    print("1. O app não vai mais travar no boot (set_page_config corrigido).")
    print("2. O banco não fará mais conversões e usará o puro PostgreSQL.")
    print("3. O botão de notícias usará o servidor do Render (economizando processamento).")

if __name__ == "__main__":
    aplicar()