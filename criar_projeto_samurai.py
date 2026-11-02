"""
criar_projeto_samurai.py — V2.3 (Hotfix: Imports, Tabelas e UI da Marmita)

ENTREGAS:
1. FIX (00_Home.py): Importa 'execute' corretamente.
2. FIX (01_Corpo.py): Cria a tabela body_metrics se ela não existir (evita erro no SQLite).
3. FIX (11_Alimentacao.py): Faz a interface dos pratos reagir à escolha de Marmita.

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

def _git_run_safe(args: list[str]) -> subprocess.CompletedProcess:
    r = subprocess.run(["git"] + args, cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if r.stdout is None: r.stdout = ""
    if r.stderr is None: r.stderr = ""
    return r

def read(p: Path) -> str: return p.read_text(encoding="utf-8")
def write_validated(p: Path, content: str) -> None:
    if p.suffix == ".py":
        try: ast.parse(content, filename=str(p))
        except SyntaxError as e:
            print(f"[ABORTA] Sintaxe quebrada em {p}: {e}"); sys.exit(1)
    p.write_text(content, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")

# ============================================================
# 1. HOME (Import execute)
# ============================================================
def fix_home_import() -> None:
    p = BASE / "ui" / "pages" / "00_Home.py"
    txt = read(p)
    if "from core.database import query_all, query_one, execute" in txt:
        print("[SKIP] 00_Home.py — import execute já existe.")
        return

    old_imp = "from core.database import query_all, query_one"
    new_imp = "from core.database import query_all, query_one, execute"
    if old_imp in txt:
        txt = txt.replace(old_imp, new_imp, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 00_Home.py — marcador de import não encontrado.")

# ============================================================
# 2. CORPO (Rede de segurança para body_metrics)
# ============================================================
def fix_corpo_table() -> None:
    p = BASE / "ui" / "pages" / "01_Corpo.py"
    txt = read(p)

    if "# Busca o peso mais recente" not in txt:
        print("[SKIP] 01_Corpo.py — não tem o bloco de peso.")
        return

    old_metric = '''# Busca o peso mais recente para a IA
_metric = query_one("SELECT weight, body_fat FROM body_metrics ORDER BY log_date DESC LIMIT 1")
peso_atual = _metric["weight"] if _metric else 70.0
bf_atual = _metric["body_fat"] if _metric else "N/A"'''

    new_metric = '''# Busca o peso mais recente para a IA
try:
    _metric = query_one("SELECT weight, body_fat FROM body_metrics ORDER BY log_date DESC LIMIT 1")
except Exception:
    # Fallback caso a tabela não exista no SQLite local ainda
    execute("CREATE TABLE IF NOT EXISTS body_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, log_date TEXT NOT NULL UNIQUE, weight REAL NOT NULL, body_fat REAL, notes TEXT)")
    _metric = None

peso_atual = _metric["weight"] if _metric else 70.0
bf_atual = _metric["body_fat"] if _metric else "N/A"'''

    if old_metric in txt:
        txt = txt.replace(old_metric, new_metric, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 01_Corpo.py — bloco _metric não encontrado exatamente.")

# ============================================================
# 3. ALIMENTAÇÃO (UI Reativa à Marmita)
# ============================================================
def fix_alimentacao_ui() -> None:
    p = BASE / "ui" / "pages" / "11_Alimentacao.py"
    txt = read(p)

    if "marmita_info = " in txt:
        print("[SKIP] 11_Alimentacao.py — UI reativa já implementada.")
        return

    # O texto original que renderiza o card do prato
    old_card = '''    det = next(o for o in opcoes if o["prato"] == escolha)
    st.markdown(f'<div class="samurai-card" style="padding: 15px; border-left-color: #F9A825;"><b>🛒 Ingredientes:</b><br>{det["ing"]}<br><br><b>👨‍🍳 Modo de Preparo:</b><br>{det["prep"]}<br><br><b style="color: #4CAF50;">💪 Por que é bom para Ectomorfo?</b><br>{det["porque"]}</div>', unsafe_allow_html=True)'''

    new_card = '''    det = next(o for o in opcoes if o["prato"] == escolha)
    
    marmita_info = ""
    if "marmita" in tipo_refeicao.lower():
        marmita_info = "<br><br><b style='color: #2196F3;'>🍱 Dica de Marmita:</b> Espere esfriar, guarde em potes de vidro fechados. Dura até 3 dias na geladeira. Ao reaquecer, adicione 1 colher de água para não secar."
        
    st.markdown(f'<div class="samurai-card" style="padding: 15px; border-left-color: #F9A825;"><b>🛒 Ingredientes:</b><br>{det["ing"]}<br><br><b>👨‍🍳 Modo de Preparo:</b><br>{det["prep"]}{marmita_info}<br><br><b style="color: #4CAF50;">💪 Por que é bom para Ectomorfo?</b><br>{det["porque"]}</div>', unsafe_allow_html=True)'''

    if old_card in txt:
        txt = txt.replace(old_card, new_card, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 11_Alimentacao.py — bloco de renderização do card não encontrado.")

# ============================================================
# SYNC GIT
# ============================================================
def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    
    msg = "fix: resolve import execute, cria tabela fallback e reatividade da marmita"
    _git_run_safe(["commit", "-m", msg])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

# ============================================================
# MAIN
# ============================================================
def aplicar() -> None:
    print("=" * 60)
    print("V2.3 — HOTFIX: IMPORTS E UI MARMITA")
    print("=" * 60)

    etapas = [
        ("Corrigir import execute (00_Home.py)", fix_home_import),
        ("Garantir tabela body_metrics (01_Corpo.py)", fix_corpo_table),
        ("Conectar UI de marmita (11_Alimentacao.py)", fix_alimentacao_ui),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nRecarregue a página do app local (localhost:8501).")
    print("1. A Home não deve mais quebrar.")
    print("2. A tela de Corpo deve carregar o peso normalmente.")
    print("3. Em Alimentação, mude para 'Marmita' e veja a dica azul aparecer nos pratos.")

if __name__ == "__main__":
    aplicar()