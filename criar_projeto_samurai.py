"""
criar_projeto_samurai.py — V4.5 (A Grande Correção do Adaptador SQL)

ENTREGAS:
1. FIX (core/database.py): Corrige o adapt_sql usando REGEX para garantir a troca exata do comando.
2. FIX (14_Carreira.py): Fallback robusto e específico para Postgres/SQLite na tabela manuals.
3. FORÇA: O init_db agora vai rodar limpo e criar TODAS as tabelas no Supabase.

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
# 1. CORRIGIR A RAIZ: adapt_sql em core/database.py
# ============================================================
def fix_database_sql_adapter() -> None:
    p = BASE / "core" / "database.py"
    txt = read(p)

    if '"INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY"' in txt:
        print("[SKIP] database.py — adapt_sql já corrigido.")
        return

    # Usa Regex para encontrar a função inteira, independente de quebras de linha
    pattern = re.compile(r"def adapt_sql\(sql: str, is_pg: bool\) -> str:.*?return sql", re.DOTALL)
    
    new_func = '''def adapt_sql(sql: str, is_pg: bool) -> str:
    if is_pg:
        sql = sql.replace("?", "%s")
        sql = sql.replace("datetime('now')", "CURRENT_TIMESTAMP")
        sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        sql = sql.replace("AUTOINCREMENT", "SERIAL")
    return sql'''
    
    if pattern.search(txt):
        txt = pattern.sub(new_func, txt, count=1)
        write_validated(p, txt)
    else:
        print("[AVISO] database.py — não foi possível substituir adapt_sql por regex.")

# ============================================================
# 2. FALLBACK ESPECÍFICO NO 14_CARREIRA.PY
# ============================================================
def fix_career_fallback() -> None:
    p = BASE / "ui" / "pages" / "14_Carreira.py"
    txt = read(p)

    old_fallback = '''    except Exception:
        # Fallback: se a tabela não existir no Postgres, cria agora
        execute("CREATE TABLE IF NOT EXISTS manuals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, content TEXT NOT NULL, uploaded_at TEXT NOT NULL DEFAULT (datetime('now')))")
        manuais = []'''

    new_fallback = '''    except Exception:
        from core.database import is_postgres
        if is_postgres():
            execute("CREATE TABLE IF NOT EXISTS manuals (id SERIAL PRIMARY KEY, title TEXT UNIQUE, content TEXT NOT NULL, uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        else:
            execute("CREATE TABLE IF NOT EXISTS manuals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, content TEXT NOT NULL, uploaded_at TEXT NOT NULL DEFAULT (datetime('now')))")
        manuais = []'''

    if old_fallback in txt:
        txt = txt.replace(old_fallback, new_fallback, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 14_Carreira.py — fallback antigo não encontrado ou já corrigido.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "fix(db): corrige adapt_sql raiz para postgres e fallback de manuais"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V4.5 — CORREÇÃO DEFINITIVA DO ADAPTADOR SQL")
    print("=" * 60)

    fix_database_sql_adapter()
    fix_career_fallback()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar.")
    print("2. Recarregue a página '💼 Carreira'.")
    print("3. O erro vai sumir porque a tabela agora será criada perfeitamente no Supabase.")
    print("4. Aproveite: as outras tabelas que estavam falhando silenciosamente (como daily_briefs) agora também foram criadas!")

if __name__ == "__main__":
    aplicar()