"""
Conexão de Banco de Dados Híbrida com Pooling para PostgreSQL.
"""
from __future__ import annotations
import sqlite3
import threading
import streamlit as st
from pathlib import Path

try:
    import psycopg2
    import psycopg2.extras
    from psycopg2 import pool
    HAS_PG = True
except ImportError:
    HAS_PG = False

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "samurai.db"

_lock = threading.RLock()
_pg_pool = None

def get_db_url():
    try:
        if "SUPABASE_URL" in st.secrets:
            return st.secrets["SUPABASE_URL"]
    except Exception:
        pass
    return None

def get_pg_pool():
    global _pg_pool
    if _pg_pool is None and HAS_PG:
        db_url = get_db_url()
        if db_url:
            try:
                _pg_pool = pool.ThreadedConnectionPool(1, 20, db_url)
            except Exception as e:
                print(f"Erro ao criar pool: {e}")
    return _pg_pool

def is_postgres() -> bool:
    try:
        return "SUPABASE_URL" in st.secrets and HAS_PG
    except Exception:
        return False

def adapt_sql(sql: str, is_pg: bool) -> str:
    if is_pg:
        sql = sql.replace("?", "%s")
        sql = sql.replace("datetime('now')", "CURRENT_TIMESTAMP")
        sql = sql.replace("AUTOINCREMENT", "SERIAL")
    return sql

def get_connection():
    is_pg = is_postgres()
    if is_pg:
        p = get_pg_pool()
        if p:
            return p.getconn(), True
        else:
            return psycopg2.connect(get_db_url()), True
    else:
        conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn, False

def close_connection(conn, is_pg):
    if is_pg:
        p = get_pg_pool()
        if p:
            p.putconn(conn)
        else:
            conn.close()
    else:
        conn.close()

def execute(sql: str, params: tuple = ()) -> int:
    with _lock:
        conn, is_pg = get_connection()
        sql = adapt_sql(sql, is_pg)
        try:
            if is_pg:
                sql_upper = sql.upper().strip()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                if sql_upper.startswith("INSERT") and "RETURNING" not in sql_upper:
                    # === PATCH SAMURAI: RETURNING ===
                    # Tenta RETURNING id; se a tabela nao tem 'id'
                    # (reading_plan/reading_progress usam 'day' como PK),
                    # refaz o INSERT sem RETURNING.
                    try:
                        cur.execute(sql + " RETURNING id", params)
                        conn.commit()
                        try:
                            res = cur.fetchone()
                            return res["id"] if res else 0
                        except Exception:
                            return 0
                    except psycopg2.errors.UndefinedColumn:
                        conn.rollback()
                        cur.execute(sql, params)
                        conn.commit()
                        return 0
                else:
                    cur.execute(sql, params)
                    conn.commit()
                    try:
                        res = cur.fetchone()
                        if res:
                            try:
                                return res["id"]
                            except (KeyError, TypeError):
                                return 0
                        return 0
                    except Exception:
                        return 0
            else:
                cur = conn.execute(sql, params)
                conn.commit()
                return cur.lastrowid
        finally:
            close_connection(conn, is_pg)

def query_all(sql: str, params: tuple = ()) -> list[dict]:
    with _lock:
        conn, is_pg = get_connection()
        sql = adapt_sql(sql, is_pg)
        try:
            if is_pg:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(sql, params)
                return cur.fetchall()
            else:
                return [dict(row) for row in conn.execute(sql, params).fetchall()]
        finally:
            close_connection(conn, is_pg)

def query_one(sql: str, params: tuple = ()) -> dict | None:
    with _lock:
        conn, is_pg = get_connection()
        sql = adapt_sql(sql, is_pg)
        try:
            if is_pg:
                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(sql, params)
                return cur.fetchone()
            else:
                row = conn.execute(sql, params).fetchone()
                return dict(row) if row else None
        finally:
            close_connection(conn, is_pg)
