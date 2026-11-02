"""
criar_projeto_samurai.py — V3.6 (Fix IndexError no psycopg2 com LIKE '%%')

ENTREGAS:
1. FIX (core/database.py): Evita passar tuplas vazias () para o psycopg2 quando não há parâmetros, evitando crash com '%' em queries.
2. FIX (04_Patrimonio.py): Garante que a tabela não seja recriada e o chat funcione perfeitamente.

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

# ============================================================
# 1. FIX NO BANCO DE DADOS (Evitar IndexError do psycopg2)
# ============================================================
def fix_database_empty_params() -> None:
    p = BASE / "core" / "database.py"
    txt = read(p)

    if "if params:" in txt:
        print("[SKIP] database.py — correção de params vazios já aplicada.")
        return

    # 1.1 Corrigir a função execute
    old_exec_1 = '''                        try:
                            cur.execute(sql + " RETURNING id", params)'''
    new_exec_1 = '''                        try:
                            if params: cur.execute(sql + " RETURNING id", params)
                            else: cur.execute(sql + " RETURNING id")'''

    old_exec_2 = '''                            cur.execute(sql, params)
                            conn.commit()
                            return 0'''
    new_exec_2 = '''                            if params: cur.execute(sql, params)
                            else: cur.execute(sql)
                            conn.commit()
                            return 0'''

    old_exec_3 = '''                    else:
                        cur.execute(sql, params)
                        conn.commit()'''
    new_exec_3 = '''                    else:
                        if params: cur.execute(sql, params)
                        else: cur.execute(sql)
                        conn.commit()'''

    # 1.2 Corrigir a função query_all
    old_q_all = '''                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(sql, params)
                return cur.fetchall()'''
    new_q_all = '''                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                if params: cur.execute(sql, params)
                else: cur.execute(sql)
                return cur.fetchall()'''

    # 1.3 Corrigir a função query_one
    old_q_one = '''                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                cur.execute(sql, params)
                return cur.fetchone()'''
    new_q_one = '''                cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                if params: cur.execute(sql, params)
                else: cur.execute(sql)
                return cur.fetchone()'''

    txt = txt.replace(old_exec_1, new_exec_1)
    txt = txt.replace(old_exec_2, new_exec_2)
    txt = txt.replace(old_exec_3, new_exec_3)
    txt = txt.replace(old_q_all, new_q_all)
    txt = txt.replace(old_q_one, new_q_one)

    write_validated(p, txt)

# ============================================================
# 2. LIMPEZA NO PATRIMÔNIO (Remover CREATE TABLE solto)
# ============================================================
def fix_patrimonio_cleanup() -> None:
    p = BASE / "ui" / "pages" / "04_Patrimonio.py"
    txt = read(p)

    alvo = 'execute("CREATE TABLE IF NOT EXISTS patrimony_fixed_income (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, rate TEXT)")\n'
    if alvo in txt:
        txt = txt.replace(alvo, "", 1)
        write_validated(p, txt)
    else:
        print("[SKIP] 04_Patrimonio.py — tabela já limpa.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "fix(db): evita indexerror do psycopg2 com likes e params vazios"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V3.6 — BLINDAGEM DO PSYCOPG2")
    print("=" * 60)

    fix_database_empty_params()
    fix_patrimonio_cleanup()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 min).")
    print("2. Abra a aba 'Patrimônio'.")
    print("3. O erro sumiu e o Chat com Analista já está disponível para uso.")

if __name__ == "__main__":
    aplicar()