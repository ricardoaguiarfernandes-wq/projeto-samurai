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
