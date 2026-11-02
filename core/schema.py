"""
Criação das tabelas e seed inicial.
Idempotente: pode rodar em todo boot sem duplicar nada.
"""
from __future__ import annotations

import requests
from core.database import execute, query_one, query_all

def get_ddl():
    from core.database import is_postgres
    is_pg = is_postgres()

    ddl_base = [
        """CREATE TABLE IF NOT EXISTS habits (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, pillar TEXT NOT NULL, description TEXT, active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT (datetime('now')));""",
        """CREATE TABLE IF NOT EXISTS habit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER NOT NULL, log_date TEXT NOT NULL, done INTEGER NOT NULL DEFAULT 0, notes TEXT, FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE, UNIQUE (habit_id, log_date));""",
        """CREATE TABLE IF NOT EXISTS daily_checkins (id INTEGER PRIMARY KEY AUTOINCREMENT, checkin_date TEXT NOT NULL UNIQUE, energy INTEGER NOT NULL, sleep_hours REAL NOT NULL, mood TEXT, stress INTEGER NOT NULL, notes TEXT);""",
        """CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, expense_date TEXT NOT NULL, description TEXT NOT NULL, amount REAL NOT NULL, category TEXT, notes TEXT);""",
        """CREATE TABLE IF NOT EXISTS patrimony_fixed_income (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, rate TEXT);""",
        """CREATE TABLE IF NOT EXISTS body_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, log_date TEXT NOT NULL UNIQUE, weight REAL NOT NULL, body_fat REAL, notes TEXT);""",
        """CREATE TABLE IF NOT EXISTS user_stats (id INTEGER PRIMARY KEY, xp INTEGER NOT NULL DEFAULT 0, level INTEGER NOT NULL DEFAULT 1);""",
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

    if not query_one("SELECT id FROM user_stats WHERE id = 1"):
        execute("INSERT INTO user_stats (id, xp, level) VALUES (1, 0, 1)")
