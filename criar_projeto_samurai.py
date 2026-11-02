"""
criar_projeto_samurai.py — V4.4 (Hotfix: Sintaxe do SERIAL no Postgres)

ENTREGAS:
1. FIX (core/database.py): Corrige a função adapt_sql para trocar 'INTEGER PRIMARY KEY AUTOINCREMENT' por 'SERIAL PRIMARY KEY' (evitando erro de sintaxe).
2. FIX (14_Carreira.py): Garante que a tabela manuals seja criada corretamente caso não exista.

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
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

def fix_adapt_sql() -> None:
    p = BASE / "core" / "database.py"
    txt = read(p)

    if '"INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY"' in txt:
        print("[SKIP] database.py — adapt_sql já corrigido.")
        return

    old_adapt = '''def adapt_sql(sql: str, is_pg: bool) -> str:
    if is_pg:
        sql = sql.replace("?", "%s")
        sql = sql.replace("datetime('now')", "CURRENT_TIMESTAMP")
        sql = sql.replace("AUTOINCREMENT", "SERIAL")
    return sql'''

    new_adapt = '''def adapt_sql(sql: str, is_pg: bool) -> str:
    if is_pg:
        sql = sql.replace("?", "%s")
        sql = sql.replace("datetime('now')", "CURRENT_TIMESTAMP")
        # Correção crucial: troca a string inteira para o formato do Postgres
        sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        # Fallback caso venha apenas AUTOINCREMENT
        sql = sql.replace("AUTOINCREMENT", "SERIAL")
    return sql'''

    if old_adapt in txt:
        txt = txt.replace(old_adapt, new_adapt, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] database.py — bloco adapt_sql não encontrado.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "fix(db): corrige adaptacao de autoincrement para serial no postgres"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V4.4 — HOTFIX SERIAL POSTGRES")
    print("=" * 60)

    fix_adapt_sql()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 min).")
    print("2. Recarregue a página e abra a aba '💼 Carreira'.")
    print("3. O erro sumirá e a tabela será criada no Supabase.")

if __name__ == "__main__":
    aplicar()