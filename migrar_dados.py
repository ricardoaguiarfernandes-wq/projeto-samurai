import sqlite3
import psycopg2
import psycopg2.extras
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "data" / "samurai.db"
CONFIG_PATH = BASE / "config.json"

def get_pg_url():
    # Tenta achar nos secrets do streamlit
    try:
        import streamlit as st
        if "SUPABASE_URL" in st.secrets:
            return st.secrets["SUPABASE_URL"]
    except Exception: pass
    # Tenta achar no config.json
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                return json.load(f).get("supabase_url", "")
        except: pass
    return input("Cole a URL do Supabase (jdbc:postgresql://...): ").strip()

def migrar():
    pg_url = get_pg_url()
    if not pg_url:
        print("❌ URL do Supabase não encontrada.")
        return

    print("Conectando ao SQLite local...")
    if not DB_PATH.exists():
        print("❌ Banco de dados local (samurai.db) não encontrado.")
        return
    sqlite_conn = sqlite3.connect(DB_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()

    print("Conectando ao Supabase...")
    try:
        pg_conn = psycopg2.connect(pg_url)
        pg_conn.autocommit = True
        pg_cursor = pg_conn.cursor()
    except Exception as e:
        print(f"❌ Erro ao conectar no Supabase: {e}")
        return

    # Busca todas as tabelas no SQLite
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tabelas = [row['name'] for row in cursor.fetchall()]

    for tabela in tabelas:
        print(f"Migrando tabela: {tabela}...")
        try:
            # Pega a estrutura da tabela no SQLite
            cursor.execute(f"PRAGMA table_info({tabela})")
            colunas = [col['name'] for col in cursor.fetchall()]
            
            # Busca dados
            cursor.execute(f"SELECT * FROM {tabela}")
            dados = cursor.fetchall()
            
            if not dados:
                print(f"  - Tabela {tabela} vazia. Pulando...")
                continue

            # Insere no Postgres
            col_names = ", ".join(colunas)
            placeholders = ", ".join(["%s"] * len(colunas))
            insert_query = f"INSERT INTO {tabela} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
            
            for row in dados:
                pg_cursor.execute(insert_query, tuple(row))
            
            print(f"  - {len(dados)} registros migrados.")
        except Exception as e:
            print(f"  - ⚠️ Erro ao migrar {tabela}: {e}")

    print("\n✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")

if __name__ == "__main__":
    migrar()
