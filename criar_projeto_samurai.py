"""
criar_projeto_samurai.py — V8.5 (Otimização Extrema de Latência)

ENTREGAS:
1. FIX: Remove init_db() de TODAS as páginas (ui/pages/*.py). Ele só deve rodar no app.py.
2. PERF (core/database.py): Aplica st.cache_resource no pool de conexões do Supabase.
3. PERF (app.py): Garante que o init_db() rode apenas 1x por sessão.

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
# 1. REMOVER init_db() DAS PÁGINAS
# ============================================================
def fix_pages_init_db() -> None:
    print("🔍 Removendo init_db() das páginas para evitar lentidão...")
    pages_dir = BASE / "ui" / "pages"
    
    for p in pages_dir.glob("*.py"):
        txt = read(p)
        alterou = False
        
        # Remove a chamada direta
        if re.search(r"^init_db\(\)\n", txt, re.MULTILINE):
            txt = re.sub(r"^init_db\(\)\n", "", txt, flags=re.MULTILINE)
            alterou = True
            
        # Remove o import do init_db se ele não for mais usado
        if "from core.schema import init_db" in txt:
            # Checa se init_db ainda é chamado no arquivo
            if not re.search(r"init_db\(", txt):
                txt = txt.replace("from core.schema import init_db\n", "")
                alterou = True
                
        if alterou:
            write_validated(p, txt)

# ============================================================
# 2. OTIMIZAR POOL DE CONEXÃO (core/database.py)
# ============================================================
def fix_database_pool_cache() -> None:
    p = BASE / "core" / "database.py"
    txt = read(p)

    if "@st.cache_resource" in txt:
        print("[SKIP] database.py — pool já está em cache.")
        return

    old_pool = '''def get_pg_pool():
    global _pg_pool
    if _pg_pool is None and HAS_PG:
        db_url = get_db_url()
        if db_url:
            try:
                _pg_pool = pool.ThreadedConnectionPool(1, 20, db_url)
            except Exception as e:
                print(f"Erro ao criar pool: {e}")
    return _pg_pool'''

    new_pool = '''# OTIMIZAÇÃO: Mantém o pool de conexões vivo entre os cliques (evita reconectar ao Supabase toda hora)
@st.cache_resource
def get_pg_pool():
    db_url = get_db_url()
    if db_url and HAS_PG:
        try:
            return pool.ThreadedConnectionPool(1, 20, db_url)
        except Exception as e:
            print(f"Erro ao criar pool: {e}")
    return None'''

    if old_pool in txt:
        txt = txt.replace(old_pool, new_pool, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] database.py — bloco do pool não encontrado.")

# ============================================================
# 3. GARANTIR CACHE NO APP.PY
# ============================================================
def fix_app_cache() -> None:
    p = BASE / "app.py"
    txt = read(p)

    if "@st.cache_resource\ndef setup_database():" in txt:
        print("[SKIP] app.py — setup_database já está em cache.")
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

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "perf: otimizacao extrema de latencia (remove init_db redundante e cacheia pool)"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V8.5 — OTIMIZAÇÃO EXTREMA DE LATÊNCIA")
    print("=" * 60)

    fix_pages_init_db()
    fix_database_pool_cache()
    fix_app_cache()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\n🚨 COMO TESTAR A VELOCIDADE AGORA:")
    print("1. Feche o terminal do Streamlit no seu PC (Ctrl+C).")
    print("2. Rode o INICIAR.bat novamente.")
    print("3. Navegue entre as abas. A primeira página (Home) pode demorar uns 3 segundos (para criar o cache do pool).")
    print("4. A partir da segunda página, o carregamento deve ser quase instantâneo (menos de 1 segundo).")

if __name__ == "__main__":
    aplicar()