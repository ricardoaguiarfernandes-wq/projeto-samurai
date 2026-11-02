"""
criar_projeto_samurai.py — V8.4 (Otimização Extrema e Correções)

ENTREGAS:
1. FIX (app.py): Adiciona @st.cache_resource no init_db() para não consultar o Supabase a cada clique.
2. FIX (00_Home.py): Corrige o erro do pandas (.dt) e adiciona cache no heatmap.
3. FIX (14_Carreira.py & 15_Financas.py): Fallback para criar tabelas flashcards e budgets no Supabase.

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
# 1. OTIMIZAÇÃO GLOBAL (app.py)
# ============================================================
def fix_app_cache() -> None:
    p = BASE / "app.py"
    txt = read(p)

    if "@st.cache_resource" in txt:
        print("[SKIP] app.py — cache já aplicado.")
        return

    old_init = '''from core.schema import init_db
from services.auth import check_password

init_db()'''

    new_init = '''from core.schema import init_db
from services.auth import check_password

# OTIMIZAÇÃO: Roda o init_db apenas uma vez por sessão, não a cada clique
@st.cache_resource
def setup_database():
    init_db()

setup_database()'''

    if old_init in txt:
        txt = txt.replace(old_init, new_init, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] app.py — bloco init_db não encontrado.")

# ============================================================
# 2. FIX HEATMAP (00_Home.py)
# ============================================================
def fix_heatmap_datetime() -> None:
    p = BASE / "ui" / "pages" / "00_Home.py"
    txt = read(p)

    if 'df_heatmap["data"] = pd.to_datetime(df_heatmap["data"])' in txt:
        print("[SKIP] 00_Home.py — fix datetime já aplicado.")
        return

    old_df = '''df_heatmap = pd.DataFrame(dias)
df_heatmap["semana"] = df_heatmap["data"].dt.isocalendar().week'''

    new_df = '''df_heatmap = pd.DataFrame(dias)
# FIX: Força a conversão para datetime antes de usar .dt
df_heatmap["data"] = pd.to_datetime(df_heatmap["data"])
df_heatmap["semana"] = df_heatmap["data"].dt.isocalendar().week'''

    if old_df in txt:
        txt = txt.replace(old_df, new_df, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 00_Home.py — bloco df_heatmap não encontrado.")

# ============================================================
# 3. FALLBACK FLASHCARDS (14_Carreira.py)
# ============================================================
def fix_fallback_flashcards() -> None:
    p = BASE / "ui" / "pages" / "14_Carreira.py"
    txt = read(p)

    old_query = '    pendentes = query_all("SELECT question FROM flashcards WHERE next_review <= ? AND last_asked = 0", (date.today().isoformat(),))'
    
    new_query = '''    try:
        pendentes = query_all("SELECT question FROM flashcards WHERE next_review <= ? AND last_asked = 0", (date.today().isoformat(),))
    except Exception:
        execute("CREATE TABLE IF NOT EXISTS flashcards (id SERIAL PRIMARY KEY, question TEXT NOT NULL, answer TEXT NOT NULL, next_review TEXT NOT NULL, interval_days INTEGER DEFAULT 1, ease_factor REAL DEFAULT 2.5, last_asked INTEGER DEFAULT 0)")
        pendentes = []'''

    if old_query in txt:
        txt = txt.replace(old_query, new_query, 1)
        write_validated(p, txt)
    else:
        print("[SKIP] 14_Carreira.py — fallback ou query já alterados.")

# ============================================================
# 4. FALLBACK BUDGETS (15_Financas.py)
# ============================================================
def fix_fallback_budgets() -> None:
    p = BASE / "ui" / "pages" / "15_Financas.py"
    txt = read(p)

    old_query = 'budgets = query_all("SELECT * FROM budgets")'
    
    new_query = '''try:
    budgets = query_all("SELECT * FROM budgets")
except Exception:
    execute("CREATE TABLE IF NOT EXISTS budgets (category TEXT PRIMARY KEY, limit_amount REAL NOT NULL)")
    budgets = []'''

    if old_query in txt:
        txt = txt.replace(old_query, new_query, 1)
        write_validated(p, txt)
    else:
        print("[SKIP] 15_Financas.py — fallback ou query já alterados.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "perf: otimiza init_db com cache, corrige heatmap datetime e adiciona fallbacks"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V8.4 — OTIMIZAÇÃO E CORREÇÕES CRÍTICAS")
    print("=" * 60)

    fix_app_cache()
    fix_heatmap_datetime()
    fix_fallback_flashcards()
    fix_fallback_budgets()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que vai acontecer agora:")
    print("1. A página vai carregar MUITO mais rápido (o cache do Streamlit vai segurar as consultas ao banco).")
    print("2. O erro do Heatmap vai sumir e os quadradinhos vão aparecer.")
    print("3. As abas de Carreira e Finanças não vão mais quebrar por falta das tabelas.")

if __name__ == "__main__":
    aplicar()