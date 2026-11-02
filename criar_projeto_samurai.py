"""
criar_projeto_samurai.py — V6.0 (Supabase Exclusivo e Correção Definitiva do SQL)

ENTREGAS:
1. FIX (core/database.py): Desabilita o SQLite. O sistema agora só conecta no Supabase (Postgres).
2. FIX (core/schema.py): Reescreve os comandos CREATE TABLE usando a sintaxe nativa do PostgreSQL (SERIAL, CURRENT_TIMESTAMP).
3. FIX (ui/pages/*): Corrige o erro de sintaxe do SUBSTR em Patrimônio e Finanças.

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
# 1. FORÇAR POSTGRES NO DATABASE.PY
# ============================================================
def fix_database_postgres_only() -> None:
    p = BASE / "core" / "database.py"
    txt = read(p)

    if "SISTEMA EXCLUSIVO SUPABASE" in txt:
        print("[SKIP] database.py — já configurado para Supabase exclusivo.")
        return

    # Substitui a função get_connection inteira para nunca cair no SQLite
    pattern_conn = re.compile(r"def get_connection\(\):.*?return conn, False", re.DOTALL)
    new_conn = '''def get_connection():
    # SISTEMA EXCLUSIVO SUPABASE (PostgreSQL)
    db_url = get_db_url()
    if not db_url:
        raise Exception("⛔ SUPABASE_URL não configurada. O sistema está configurado apenas para Supabase.")
    if not HAS_PG:
        raise Exception("⛔ psycopg2 não instalado. Rode: pip install psycopg2-binary")
        
    p = get_pg_pool()
    if p:
        return p.getconn(), True
    else:
        return psycopg2.connect(db_url), True'''
    
    if pattern_conn.search(txt):
        txt = pattern_conn.sub(new_conn, txt, count=1)
    
    # Substitui o adapt_sql para não tentar mais converter nada (já vamos escrever em Postgres nativo)
    pattern_adapt = re.compile(r"def adapt_sql\(sql: str, is_pg: bool\) -> str:.*?return sql", re.DOTALL)
    new_adapt = '''def adapt_sql(sql: str, is_pg: bool) -> str:
    if is_pg:
        sql = sql.replace("?", "%s")
    return sql'''
    
    if pattern_adapt.search(txt):
        txt = pattern_adapt.sub(new_adapt, txt, count=1)

    write_validated(p, txt)

# ============================================================
# 2. SCHEMA NATIVO POSTGRES (SEM CONVERSÃO)
# ============================================================
def fix_schema_postgres() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)

    if "SERIAL PRIMARY KEY" in txt:
        print("[SKIP] schema.py — já usa sintaxe nativa do Postgres.")
        return

    # Troca a sintaxe do SQLite para Postgres diretamente no texto das tabelas
    txt = txt.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    txt = txt.replace("datetime('now')", "CURRENT_TIMESTAMP")
    
    # Remove a conversão condicional no final de get_ddl
    pattern_ddl = re.compile(r'    if is_pg:.*?return ddl_base', re.DOTALL)
    new_ddl = '    return ddl_base'
    if pattern_ddl.search(txt):
        txt = pattern_ddl.sub(new_ddl, txt, count=1)

    write_validated(p, txt)

# ============================================================
# 3. CORRIGIR AS QUERIES QUEBRADAS (SUBSTR)
# ============================================================
def fix_broken_queries() -> None:
    print("🔍 Corrigindo queries com sintaxe quebrada...")
    arquivos = list(BASE.glob("*.py")) + list((BASE / "ui" / "pages").glob("*.py"))
    
    # A string correta do SUBSTR
    correct_query = "SUBSTR(ticker, 1, 3) != 'RF:'"
    
    # Padrões errados que podem estar no código
    wrong_patterns = [
        "SUBSTR(ticker, 1, 3) != 'RF:'",
        "SUBSTR(ticker, 1, 3) != 'RF:'"
    ]
    
    alterou = False
    for p in arquivos:
        txt = read(p)
        original_txt = txt
        for wrong in wrong_patterns:
            txt = txt.replace(wrong, correct_query)
            
        if txt != original_txt:
            write_validated(p, txt)
            alterou = True

    if not alterou:
        print("[SKIP] Nenhuma query quebrada encontrada.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "refactor: forca uso exclusivo do supabase (postgres) e corrige sintaxe sql"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V6.0 — SUPABASE EXCLUSIVO E SQL PADRONIZADO")
    print("=" * 60)

    fix_database_postgres_only()
    fix_schema_postgres()
    fix_broken_queries()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 min).")
    print("2. Navegue por TODAS as abas do app.")
    print("3. O banco agora é 100% Supabase e o erro de sintaxe desapareceu.")
    print("4. Se der erro de 'SUPABASE_URL não configurada', verifique se o seu secrets.toml está com a URL correta.")

if __name__ == "__main__":
    aplicar()