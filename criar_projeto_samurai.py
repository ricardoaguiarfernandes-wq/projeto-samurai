"""
criar_projeto_samurai.py — V5.4 (Fix IndexError no LIKE do Postgres)

ENTREGAS:
1. FIX (15_Financas.py): Troca o 'LIKE 'RF:%'' por 'SUBSTR(ticker, 1, 3) != 'RF:''.
2. O SUBSTR funciona perfeitamente no SQLite e no PostgreSQL, evitando o bug do psycopg2 com '%'.

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

def fix_financas_like() -> None:
    p = BASE / "ui" / "pages" / "15_Financas.py"
    txt = read(p)

    old_query = 'acoes = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE \'RF:%\'")'
    new_query = 'acoes = query_all("SELECT * FROM portfolio WHERE SUBSTR(ticker, 1, 3) != \'RF:\'")'

    if old_query in txt:
        txt = txt.replace(old_query, new_query, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 15_Financas.py — query com LIKE não encontrada (pode já ter sido corrigida).")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "fix: substitui LIKE por SUBSTR para evitar erro no postgres"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V5.4 — HOTFIX LIKE POSTGRES")
    print("=" * 60)

    fix_financas_like()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 min).")
    print("2. Vá para a aba '💸 Finanças'.")
    print("3. O erro sumirá e o gráfico de gastos será renderizado corretamente.")

if __name__ == "__main__":
    aplicar()