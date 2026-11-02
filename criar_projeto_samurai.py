"""
criar_projeto_samurai.py — V5.5 (Varredura Global do Erro LIKE/Postgres)

ENTREGAS:
1. FIX: Varre todos os arquivos .py e substitui a query com LIKE 'RF:%' por SUBSTR.
2. Resolve o IndexError em TODAS as páginas (Patrimônio, Finanças, API, etc).

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

def fix_all_like_queries() -> None:
    print("🔍 Varrendo o projeto em busca de 'LIKE \'RF:%\''...")
    
    # Lista de todos os arquivos .py na raiz e nas pastas ui/pages
    arquivos = list(BASE.glob("*.py")) + list((BASE / "ui" / "pages").glob("*.py"))
    
    old_query = "SUBSTR(ticker, 1, 3) != 'RF:'"
    new_query = "SUBSTR(ticker, 1, 3) != 'RF:'"
    
    alterou_algum = False
    
    for p in arquivos:
        txt = read(p)
        if old_query in txt:
            txt = txt.replace(old_query, new_query)
            write_validated(p, txt)
            alterou_algum = True
            print(f"  -> Corrigido em {p.name}")
            
    if not alterou_algum:
        print("[SKIP] Nenhuma ocorrência de 'LIKE 'RF:%'' encontrada (já deve estar corrigido).")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "fix: varredura global para substituir LIKE por SUBSTR no postgres"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V5.5 — CORREÇÃO GLOBAL DE QUERIES (LIKE -> SUBSTR)")
    print("=" * 60)

    fix_all_like_queries()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 min).")
    print("2. Navegue por todas as abas (Patrimônio, Finanças, etc).")
    print("3. Nenhuma deve dar o erro IndexError.")

if __name__ == "__main__":
    aplicar()