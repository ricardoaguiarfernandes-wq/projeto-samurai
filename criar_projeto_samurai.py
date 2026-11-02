"""
criar_projeto_samurai.py — V2.5 (Hotfix: Fallback SQLite e UI Marmita Reativa)

ENTREGAS:
1. FIX (03_Informacao.py): Fallback de segurança para criar a tabela 'daily_briefs' no SQLite local.
2. FIX (11_Alimentacao.py): O modo de preparo agora muda dinamicamente dependendo da escolha.

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
# 1. INFORMAÇÃO (Fallback da tabela daily_briefs)
# ============================================================
def fix_informacao_db() -> None:
    p = BASE / "ui" / "pages" / "03_Informacao.py"
    txt = read(p)

    if "try:\n        briefs = query_all" in txt:
        print("[SKIP] 03_Informacao.py — fallback já implementado.")
        return

    # Garante o import do execute
    if "from core.database import query_all" in txt and "execute" not in txt:
        txt = txt.replace("from core.database import query_all", "from core.database import query_all, execute")

    old_briefs = '    briefs = query_all("SELECT * FROM daily_briefs ORDER BY brief_date DESC LIMIT 7")'
    new_briefs = '''    try:
        briefs = query_all("SELECT * FROM daily_briefs ORDER BY brief_date DESC LIMIT 7")
    except Exception:
        execute("CREATE TABLE IF NOT EXISTS daily_briefs (id INTEGER PRIMARY KEY AUTOINCREMENT, brief_date TEXT NOT NULL UNIQUE, content TEXT NOT NULL)")
        briefs = []'''

    if old_briefs in txt:
        txt = txt.replace(old_briefs, new_briefs, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 03_Informacao.py — bloco de query dos briefs não encontrado.")

# ============================================================
# 2. ALIMENTAÇÃO (Modo de Preparo Dinâmico)
# ============================================================
def fix_alimentacao_reativa() -> None:
    p = BASE / "ui" / "pages" / "11_Alimentacao.py"
    txt = read(p)

    if "prep_texto = det[\"prep\"]" in txt:
        print("[SKIP] 11_Alimentacao.py — modo de preparo dinâmico já existe.")
        return

    old_card = '''    marmita_info = ""
    if "marmita" in tipo_refeicao.lower():
        marmita_info = "<br><br><b style='color: #2196F3;'>🍱 Dica de Marmita:</b> Espere esfriar, guarde em potes de vidro fechados. Dura até 3 dias na geladeira. Ao reaquecer, adicione 1 colher de água para não secar."
        
    st.markdown(f'<div class="samurai-card" style="padding: 15px; border-left-color: #F9A825;"><b>🛒 Ingredientes:</b><br>{det["ing"]}<br><br><b>👨‍🍳 Modo de Preparo:</b><br>{det["prep"]}{marmita_info}<br><br><b style="color: #4CAF50;">💪 Por que é bom para Ectomorfo?</b><br>{det["porque"]}</div>', unsafe_allow_html=True)'''

    new_card = '''    prep_texto = det["prep"]
    if "marmita" in tipo_refeicao.lower():
        prep_texto += "<br><br><b style='color: #2196F3;'>🍱 PARA MARMITA:</b> Espere esfriar e guarde em potes herméticos na geladeira. Dura até 3 dias. Ao reaquecer, adicione 1 colher de água para não secar."
    else:
        prep_texto += "<br><br><b style='color: #4CAF50;'>🍽️ PARA AGORA:</b> Sirva imediatamente enquanto estiver quente e no ponto."

    st.markdown(f'<div class="samurai-card" style="padding: 15px; border-left-color: #F9A825;"><b>🛒 Ingredientes:</b><br>{det["ing"]}<br><br><b>👨‍🍳 Modo de Preparo:</b><br>{prep_texto}<br><br><b style="color: #4CAF50;">💪 Por que é bom para Ectomorfo?</b><br>{det["porque"]}</div>', unsafe_allow_html=True)'''

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
    _git_run_safe(["commit", "-m", "fix: fallback para daily_briefs no sqlite e modo de preparo dinamico"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

# ============================================================
# MAIN
# ============================================================
def aplicar() -> None:
    print("=" * 60)
    print("V2.5 — HOTFIX SQLITE E MARMITA")
    print("=" * 60)

    etapas = [
        ("Fallback tabela briefs (03_Informacao.py)", fix_informacao_db),
        ("Modo de preparo reativo (11_Alimentacao.py)", fix_alimentacao_reativa),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora no app local (localhost:8501):")
    print("1. A aba Informação vai carregar sem quebrar.")
    print("2. Em Alimentação, mude o botão de 'Para agora' para 'Para marmita' e veja o texto do card mudar na hora.")
    print("3. Depois que o Render atualizar (2 min), clique em 'Run workflow' no GitHub Actions.")
    print("4. O Brief vai aparecer no Streamlit!")

if __name__ == "__main__":
    aplicar()