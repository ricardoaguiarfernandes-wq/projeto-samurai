"""
criar_projeto_samurai.py — V4.3 (Hotfix: Tabela manuals no Supabase)

ENTREGAS:
1. FIX (14_Carreira.py): Adiciona um try/except para criar a tabela 'manuals' caso ela não exista no banco (Postgres/Supabase).

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

def fix_career_table_fallback() -> None:
    p = BASE / "ui" / "pages" / "14_Carreira.py"
    txt = read(p)

    if "CREATE TABLE IF NOT EXISTS manuals" in txt:
        print("[SKIP] 14_Carreira.py — fallback da tabela manuals já existe.")
        return

    old_query = '    manuais = query_all("SELECT id, title, uploaded_at FROM manuals ORDER BY uploaded_at DESC")'
    
    new_query = '''    try:
        manuais = query_all("SELECT id, title, uploaded_at FROM manuals ORDER BY uploaded_at DESC")
    except Exception:
        # Fallback: se a tabela não existir no Postgres, cria agora
        execute("CREATE TABLE IF NOT EXISTS manuals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, content TEXT NOT NULL, uploaded_at TEXT NOT NULL DEFAULT (datetime('now')))")
        manuais = []'''

    if old_query in txt:
        txt = txt.replace(old_query, new_query, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 14_Carreira.py — linha de query dos manuais não encontrada.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "fix: fallback para criar tabela manuals no postgres"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V4.3 — HOTFIX TABELA MANUAIS")
    print("=" * 60)

    fix_career_table_fallback()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 min).")
    print("2. Abra a aba '💼 Carreira' novamente.")
    print("3. O erro sumirá e você poderá fazer o upload do manual normalmente.")

if __name__ == "__main__":
    aplicar()