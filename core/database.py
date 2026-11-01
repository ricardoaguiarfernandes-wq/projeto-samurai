"""
Conexão de Banco de Dados Híbrida:
- Usa Supabase (PostgreSQL) se a URL estiver configurada nos Secrets (Nuvem).
- Usa SQLite local como fallback (PC offline ou testes).
"""
from __future__ import annotations
import sqlite3
import threading
import streamlit as st
from pathlib import Path

try:
    import psycopg2
    import psycopg2.extras
    HAS_PG = True
except ImportError:
    HAS_PG = False

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "samurai.db"

_lock = threading.RLock()

def get_db_connection():
    """Retorna a conexão ativa (Postgres se disponível, senão SQLite)."""
    db_url = None
    try:
        if "SUPABASE_URL" in st.secrets:
            db_url = st.secrets["SUPABASE_URL"]
    except Exception:
        pass
        
    if db_url and HAS_PG:
        conn = psycopg2.connect(db_url)
        return conn, True  # True indica que é Postgres
    else:
        conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn, False

def is_postgres() -> bool:
    try:
        return "SUPABASE_URL" in st.secrets and HAS_PG
    except Exception:
        return False

def adapt_sql(sql: str, is_pg: bool) -> str:
    """Adapta a sintaxe do SQLite (?) e funções de data para PostgreSQL."""
    if is_pg:
        sql = sql.replace("?", "%s")
        sql = sql.replace("datetime('now')", "CURRENT_TIMESTAMP")
        sql = sql.replace("AUTOINCREMENT", "SERIAL")
    return sql

def execute(sql: str, params: tuple = ()) -> int:
    with _lock:
        conn, is_pg = get_db_connection()
        sql = adapt_sql(sql, is_pg)
        try:
            if is_pg:
                sql_upper = sql.upper()
                if sql_upper.strip().startswith("INSERT") and "RETURNING" not in sql_upper:
                    sql += " RETURNING id"
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(sql, params)
                conn.commit()
                try:
                    res = cur.fetchone()
                    return res["id"] if res else 0
                except Exception:
                    return 0
            else:
                cur = conn.execute(sql, params)
                conn.commit()
                return cur.lastrowid
        finally:
            conn.close()

def executemany(sql: str, seq_params: list[tuple]) -> None:
    with _lock:
        conn, is_pg = get_db_connection()
        sql = adapt_sql(sql, is_pg)
        try:
            if is_pg:
                cur = conn.cursor()
                cur.executemany(sql, seq_params)
            else:
                conn.executemany(sql, seq_params)
            conn.commit()
        finally:
            conn.close()

def query_all(sql: str, params: tuple = ()) -> list[dict]:
    with _lock:
        conn, is_pg = get_db_connection()
        sql = adapt_sql(sql, is_pg)
        try:
            if is_pg:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(sql, params)
                return cur.fetchall()  # Retorna lista de dicionários
            else:
                return [dict(row) for row in conn.execute(sql, params).fetchall()]
        finally:
            conn.close()

def query_one(sql: str, params: tuple = ()) -> dict | None:
    with _lock:
        conn, is_pg = get_db_connection()
        sql = adapt_sql(sql, is_pg)
        try:
            if is_pg:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(sql, params)
                return cur.fetchone()  # Retorna um dicionário
            else:
                row = conn.execute(sql, params).fetchone()
                return dict(row) if row else None
        finally:
            conn.close()
