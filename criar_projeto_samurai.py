"""
criar_projeto_samurai.py — V5.3 (Dashboard Financeiro e Metas de Investimento)

ENTREGAS:
1. NAVEGAÇÃO (app.py): Adiciona a nova aba "💸 Finanças" no menu.
2. UI (15_Financas.py): Cria gráficos de gastos (Pie chart), histórico de comprovantes e um medidor de meta de 20 ativos.
3. IA: Adiciona um botão de análise financeira que cruza a carteira com os gastos do mês.

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
# 1. NAVEGAÇÃO (app.py)
# ============================================================
def fix_app_nav_financas() -> None:
    p = BASE / "app.py"
    txt = read(p)
    if "15_Financas.py" in txt:
        print("[SKIP] app.py — navegação de finanças já existe.")
        return

    old_nav = 'carreira = st.Page("ui/pages/14_Carreira.py", title="💼 Carreira")'
    new_nav = old_nav + '\nfinancas = st.Page("ui/pages/15_Financas.py", title="💸 Finanças")'

    old_dict = '"⚔️ Comando": [home, consistencia, disciplina, carreira],'
    new_dict = '"⚔️ Comando": [home, consistencia, disciplina, carreira, financas],'

    if old_nav in txt and old_dict in txt:
        txt = txt.replace(old_nav, new_nav, 1)
        txt = txt.replace(old_dict, new_dict, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] app.py — estrutura de navegação não encontrada.")

# ============================================================
# 2. UI DA PÁGINA DE FINANÇAS
# ============================================================
def create_financas_page() -> None:
    p = BASE / "ui" / "pages" / "15_Financas.py"
    if p.exists():
        print("[SKIP] 15_Financas.py — página já existe.")
        return

    content = '''import streamlit as st
import sys
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("💸 Finanças & Gastos")
st.caption("Controle de gastos capturados via Telegram e acompanhamento da meta de investimentos.")

hoje = date.today().isoformat()
mes_atual = hoje[:7] # Formato YYYY-MM

# --- BUSCA DE DADOS ---
gastos = query_all("SELECT * FROM expenses ORDER BY expense_date DESC")
acoes = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE 'RF:%'")
rf = query_all("SELECT * FROM patrimony_fixed_income")

# Calcula total de gastos no mês
gastos_mes = [g for g in gastos if g['expense_date'].startswith(mes_atual)]
total_mes = sum(g['amount'] for g in gastos_mes)

# --- VISÃO GERAL ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class="samurai-card" style="border-left-color: #F44336;"><div class="titulo">Gastos do Mês</div><div class="valor">R$ {total_mes:.2f}</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;"><div class="titulo">Ativos na Carteira</div><div class="valor">{len(acoes)} / 20</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="samurai-card" style="border-left-color: #4CAF50;"><div class="titulo">Renda Fixa</div><div class="valor">{len(rf)} ativos</div></div>""", unsafe_allow_html=True)

st.divider()

# --- GRÁFICO DE GASTOS ---
st.subheader("🍕 Para onde o dinheiro está indo?")
if not gastos:
    st.info("Nenhum gasto registrado ainda. Envie uma foto de comprovante no Telegram!")
else:
    df = pd.DataFrame(gastos)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    
    # Agrupa por categoria
    df_cat = df.groupby('category')['amount'].sum().reset_index()
    
    fig = px.pie(df_cat, values='amount', names='category', hole=0.4, 
                 color_discrete_sequence=px.colors.sequential.Reds_r)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#F2F2F2'))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📄 Ver Histórico de Gastos Detalhado"):
        st.dataframe(df[['expense_date', 'description', 'amount', 'category']], use_container_width=True)

st.divider()

# --- METAS E ANÁLISE IA ---
st.subheader("🎯 Meta de Diversificação Global")
st.write("Seu objetivo é ter 15 a 20 ativos (B3, BDRs e ETFs) + Renda Fixa Global.")

progresso = min(len(acoes) / 20.0, 1.0)
st.progress(progresso)
st.caption(f"Progresso da meta: {len(acoes)} de 20 ações cadastradas.")

if st.button("🧠 Gerar Análise de Gastos e Investimentos com IA", use_container_width=True):
    with st.spinner("Analisando suas finanças..."):
        # Contexto para a IA
        resumo_gastos = ""
        if gastos_mes:
            for g in gastos_mes[:10]: # Pega os últimos 10
                resumo_gastos += f"- {g['description']} (R$ {g['amount']}) [{g['category']}]\\n"
        else:
            resumo_gastos = "Nenhum gasto registrado este mês."

        ctx_acoes = ", ".join([a['ticker'] for a in acoes]) if acoes else "Nenhuma ação cadastrada."
        ctx_rf = ", ".join([r['name'] for r in rf]) if rf else "Nenhuma renda fixa cadastrada."

        prompt = f"""Atue como o Mentor Financeiro do Projeto Samurai.
O usuário quer chegar a 20 ações globais e diversificar a renda fixa.

CARTEIRA ATUAL:
- Ações: {ctx_acoes}
- Renda Fixa: {ctx_rf}

GASTOS DO MÊS (Capturados via OCR):
{resumo_gastos}

Sua missão:
1. Avalie os gastos: Ele está gastando com futilidades que atrasam o investimento? Ou os gastos são saudáveis?
2. Analise a carteira: Está diversificada? Faltam setores ou proteção cambial (BDRs/ETFs)?
3. Dê 2 conselhos práticos para o próximo mês, focando em cortar o excesso e alocar o dinheiro na meta das 20 ações.
Mantenha o tom firme, direto e sem enrolação.
"""
        analise = ask_gemini(prompt)
        st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Visão do Mentor Financeiro</div><div style="white-space: pre-wrap;">{analise}</div></div>', unsafe_allow_html=True)
'''
    write_validated(p, content)

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: cria dashboard financeiro com graficos de gastos e meta de acoes"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V5.3 — DASHBOARD FINANCEIRO E METAS")
    print("=" * 60)

    etapas = [
        ("Adicionar página no menu (app.py)", fix_app_nav_financas),
        ("Criar interface de finanças (15_Financas.py)", create_financas_page),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 min).")
    print("2. Clique na nova aba '💸 Finanças' no menu esquerdo.")
    print("3. Veja o gráfico de pizza com os gastos que você enviou pelo Telegram.")
    print("4. Clique em 'Gerar Análise de Gastos e Investimentos com IA' para ver o veredito do Mentor.")

if __name__ == "__main__":
    aplicar()