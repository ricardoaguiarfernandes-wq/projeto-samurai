"""
criar_projeto_samurai.py — V2.1 (Fixes + Peso + Marmita)

ENTREGAS:
1. FIX: Importa ask_gemini em ui/pages/03_Informacao.py (resolve NameError).
2. DB: Cria a tabela 'body_metrics' em core/schema.py.
3. UI (Corpo): Adiciona formulário de peso/gordura e envia o peso para a IA Treino.
4. UI (Alimentação): Adiciona a opção de 'Na hora' vs 'Marmita' e ajusta o Chef IA.

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

def scan_stage_secrets() -> list[str]:
    problemas = []
    r = _git_run_safe(["diff", "--cached", "--name-only"])
    for f in (r.stdout or "").splitlines():
        f = f.strip()
        if not f: continue
        if Path(f).name in {".env", "config.json", "secrets.toml"} or f in {".streamlit/secrets.toml", ".streamlit/config.toml"}:
            problemas.append(f"Arquivo sensível: {f}")
    r = _git_run_safe(["diff", "--cached", "--unified=0"])
    for linha in (r.stdout or "").splitlines():
        if not linha.startswith("+") or linha.startswith("+++"): continue
        if re.search(r"postgres(?:ql)?://[^:]+:[^@\s]+@", linha):
            problemas.append(f"URL Postgres no diff: {linha[:80]}")
    return problemas

def read(p: Path) -> str: return p.read_text(encoding="utf-8")
def write_validated(p: Path, content: str) -> None:
    if p.suffix == ".py":
        try: ast.parse(content, filename=str(p))
        except SyntaxError as e:
            print(f"[ABORTA] Sintaxe quebrada em {p}: {e}"); sys.exit(1)
    p.write_text(content, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")

# ============================================================
# 1. FIX INFORMAÇÃO (Import ask_gemini)
# ============================================================
def fix_informacao_import() -> None:
    p = BASE / "ui" / "pages" / "03_Informacao.py"
    txt = read(p)
    if "from services.ai import ask_gemini" in txt:
        print("[SKIP] 03_Informacao.py — import já existe.")
        return
    
    old_imp = "from core.schema import init_db\nfrom core.database import query_all"
    new_imp = "from core.schema import init_db\nfrom core.database import query_all\nfrom services.ai import ask_gemini"
    if old_imp in txt:
        txt = txt.replace(old_imp, new_imp, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 03_Informacao.py — marcador de import não encontrado.")

# ============================================================
# 2. SCHEMA — Tabela de Peso
# ============================================================
def fix_schema_metrics() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)
    if "body_metrics" in txt:
        print("[SKIP] schema.py — body_metrics já existe.")
        return
    
    marker = '"""CREATE TABLE IF NOT EXISTS patrimony_fixed_income (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, rate TEXT);""",'
    nova_linha = marker + '\n        """CREATE TABLE IF NOT EXISTS body_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, log_date TEXT NOT NULL UNIQUE, weight REAL NOT NULL, body_fat REAL, notes TEXT);""",'
    if marker in txt:
        txt = txt.replace(marker, nova_linha, 1)
        write_validated(p, txt)

# ============================================================
# 3. CORPO — UI de Peso e Prompt de Treino
# ============================================================
def fix_corpo_weight() -> None:
    p = BASE / "ui" / "pages" / "01_Corpo.py"
    txt = read(p)

    if "Atualizar Peso" in txt:
        print("[SKIP] 01_Corpo.py — UI de peso já existe.")
        return

    # 3.1 Inserir UI de Peso
    old_title = 'st.title("💪 Corpo")\nst.caption("Treino progressivo com carga, histórico e cronômetro interativo.")'
    new_title = '''st.title("💪 Corpo")
st.caption("Treino progressivo com carga, histórico e cronômetro interativo.")

with st.expander("⚖️ Atualizar Peso e Composição Corporal"):
    with st.form("form_peso"):
        c1, c2 = st.columns(2)
        peso = c1.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
        bf = c2.number_input("Gordura Corporal (%)", min_value=1.0, max_value=50.0, value=15.0, step=0.1)
        if st.form_submit_button("Salvar Medidas", use_container_width=True):
            execute("INSERT INTO body_metrics (log_date, weight, body_fat) VALUES (?, ?, ?) ON CONFLICT(log_date) DO UPDATE SET weight=excluded.weight, body_fat=excluded.body_fat", (date.today().isoformat(), peso, bf))
            st.success("Medidas atualizadas! A IA agora usará esses dados.")
            st.rerun()

# Busca o peso mais recente para a IA
_metric = query_one("SELECT weight, body_fat FROM body_metrics ORDER BY log_date DESC LIMIT 1")
peso_atual = _metric["weight"] if _metric else 70.0
bf_atual = _metric["body_fat"] if _metric else "N/A"'''

    if old_title in txt:
        txt = txt.replace(old_title, new_title, 1)

    # 3.2 Atualizar Prompt da IA
    old_prompt = 'prompt = f"Atue como treinador de musculação/calistenia. Aluno ectomorfo. Divisão: {divisao}. Histórico:\\n{ctx}\\n\\nSugira a ficha de hoje focando em progressão.'
    new_prompt = 'prompt = f"Atue como treinador de musculação/calistenia. Aluno ectomorfo. Peso atual: {peso_atual}kg, Gordura: {bf_atual}%. Divisão: {divisao}. Histórico:\\n{ctx}\\n\\nSugira a ficha de hoje focando em progressão.'

    if old_prompt in txt:
        txt = txt.replace(old_prompt, new_prompt, 1)
    
    write_validated(p, txt)

# ============================================================
# 4. ALIMENTAÇÃO — Opção Marmita
# ============================================================
def fix_alimentacao_marmita() -> None:
    p = BASE / "ui" / "pages" / "11_Alimentacao.py"
    txt = read(p)

    if "Para agora" in txt:
        print("[SKIP] 11_Alimentacao.py — opção de marmita já existe.")
        return

    # 4.1 Adicionar seletor global
    old_sub = 'st.subheader("🤖 Chef Samurai (Criar Nova Receita)")'
    new_sub = '''st.subheader("🤖 Chef Samurai (Criar Nova Receita)")
tipo_refeicao = st.radio("O destino desta refeição é:", ["Para agora (Na hora)", "Para marmita (Dura +3 dias)"], horizontal=True)'''

    if old_sub in txt:
        txt = txt.replace(old_sub, new_sub, 1)

    # 4.2 Atualizar Prompt do Chef
    old_prompt = 'prompt = f"Crie uma receita hipercalórica para {ref}. Ingredientes: {ing}. Formate com Ingredientes, Preparo e Por que é bom para ectomorfos."'
    new_prompt = 'prompt = f"Crie uma receita hipercalórica para {ref}. O formato é: {tipo_refeicao}. Ingredientes: {ing}. Se for marmita, foque em ingredientes que aguentam dias na geladeira e expliquem como armazenar. Formate com Ingredientes, Preparo e Por que é bom para ectomorfos."'

    if old_prompt in txt:
        txt = txt.replace(old_prompt, new_prompt, 1)
    
    write_validated(p, txt)

# ============================================================
# 5. SYNC GIT
# ============================================================
def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    
    problemas = scan_stage_secrets()
    if problemas:
        print("\n[ABORTA] SEGREDOS DETECTADOS:")
        for p_ in problemas: print(f"  X {p_}")
        _git_run_safe(["reset"])
        sys.exit(1)
    print("[OK] Varredura de segredos: limpa")

    msg = "feat(v2.1): fix import ask_gemini, metricas corporais (peso/bf) e suporte a marmita"
    _git_run_safe(["commit", "-m", msg])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído! O Streamlit Cloud vai atualizar automaticamente.")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

# ============================================================
# MAIN
# ============================================================
def aplicar() -> None:
    print("=" * 60)
    print("V2.1 — FIXES + PESO + MARMITA")
    print("=" * 60)

    etapas = [
        ("Corrigir import em 03_Informacao.py", fix_informacao_import),
        ("Criar tabela body_metrics (schema.py)", fix_schema_metrics),
        ("Adicionar peso e atualizar IA (01_Corpo.py)", fix_corpo_weight),
        ("Adicionar opção de marmita (11_Alimentacao.py)", fix_alimentacao_marmita),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora no app Streamlit (pode levar 1-2 min para atualizar):")
    print("1. Acesse a aba 'Informação' e clique no botão de gerar brief (deve funcionar sem erro).")
    print("2. Acesse 'Corpo' e preencha o seu peso/gordura no topo. Depois gere a ficha de treino com IA e veja se ela cita o seu peso.")
    print("3. Acesse 'Alimentação', escolha a opção 'Marmita' e gere uma receita. O Chef vai adaptar a receita.")

if __name__ == "__main__":
    aplicar()