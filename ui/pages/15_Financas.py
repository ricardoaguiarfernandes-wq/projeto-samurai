import streamlit as st
import sys
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from services.ai import ask_gemini

st.title("💸 Finanças & Gastos")
st.caption("Controle de gastos capturados via Telegram e acompanhamento da meta de investimentos.")

hoje = date.today().isoformat()
mes_atual = hoje[:7] # Formato YYYY-MM

# --- BUSCA DE DADOS ---
gastos = query_all("SELECT * FROM expenses ORDER BY expense_date DESC")
acoes = query_all("SELECT * FROM portfolio WHERE SUBSTR(ticker, 1, 3) != 'RF:'")
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

# --- CONFIGURAÇÃO DE ORÇAMENTO ---
with st.expander("⚙️ Configurar Orçamento Mensal (Teto de Gastos)"):
    st.write("Defina o limite para cada categoria. O Mentor vai te avisar se você estourar.")
    with st.form("form_budget"):
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Saúde", "Outros"])
        val = c2.number_input("Limite Mensal (R$)", min_value=0.0, step=100.0)
        if st.form_submit_button("Salvar Limite"):
            execute("INSERT INTO budgets (category, limit_amount) VALUES (?, ?) ON CONFLICT(category) DO UPDATE SET limit_amount=excluded.limit_amount", (cat, val))
            st.success(f"Limite de R$ {val:.2f} salvo para {cat}.")
            st.rerun()

st.divider()

# --- BARRAS DE PROGRESSO DO ORÇAMENTO ---
st.subheader("📊 Orçamento em Tempo Real")
try:
    budgets = query_all("SELECT * FROM budgets")
except Exception:
    execute("CREATE TABLE IF NOT EXISTS budgets (category TEXT PRIMARY KEY, limit_amount REAL NOT NULL)")
    budgets = []
if budgets:
    for b in budgets:
        # Pega o total gasto nesta categoria no mês atual
        gasto_cat = sum([g['amount'] for g in gastos_mes if g['category'] == b['category']])
        perc = (gasto_cat / b['limit_amount']) * 100 if b['limit_amount'] > 0 else 0
        
        cor = "#4CAF50" if perc < 70 else ("#F9A825" if perc < 90 else "#F44336")
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
            <span><b>{b['category']}</b></span>
            <span>R$ {gasto_cat:.2f} / R$ {b['limit_amount']:.2f} ({perc:.0f}%)</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(perc / 100, 1.0))
        if perc >= 90:
            st.caption(f"⚠️ Cuidado! Você já usou {perc:.0f}% do seu limite em {b['category']}.")

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
                resumo_gastos += f"- {g['description']} (R$ {g['amount']}) [{g['category']}]\n"
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
