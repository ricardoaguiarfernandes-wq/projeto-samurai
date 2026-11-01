import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf
import pandas as pd
import plotly.express as px

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()
st.title("💎 Patrimônio")

tab_acoes, tab_renda_fixa, tab_gastos = st.tabs(["📊 Ações/FIIs", "🏦 Renda Fixa", "💸 Gastos"])

with tab_acoes:
    carteira = query_all("SELECT * FROM portfolio ORDER BY ticker")
    with st.expander("➕ Adicionar Ação"):
        with st.form("form_ativo"):
            ticker = st.text_input("Ticker (ex: PETR4.SA)").upper()
            qtd = st.number_input("Qtd", min_value=1, value=100)
            pm = st.number_input("Preço Médio (R$)", min_value=0.01, value=30.00)
            if st.form_submit_button("Salvar"):
                execute("INSERT INTO portfolio (ticker, quantity, average_price) VALUES (?, ?, ?) ON CONFLICT(ticker) DO UPDATE SET quantity=excluded.quantity, average_price=excluded.average_price", (ticker, qtd, pm))
                st.rerun()
    
    if carteira:
        for a in carteira:
            try:
                data = yf.Ticker(a["ticker"]).history(period="1d")
                preco = data['Close'].iloc[-1] if not data.empty else a["average_price"]
            except: preco = a["average_price"]
            lucro = (preco - a["average_price"]) * a["quantity"]
            cor = "#4CAF50" if lucro >= 0 else "#F44336"
            st.markdown(f"""<div class="samurai-card" style="border-left-color: {cor};"><div style="display:flex; justify-content:space-between;"><div>{a['ticker']} ({a['quantity']} cotas)</div><div style="color:{cor};">R$ {lucro:.2f}</div></div></div>""", unsafe_allow_html=True)

with tab_renda_fixa:
    st.subheader("Seus Investimentos em Renda Fixa")
    st.info("Cadastre aqui Tesouro Direto, CDBs, LCI/LCA, etc.")
    with st.form("form_renda_fixa"):
        nome = st.text_input("Nome do Título (ex: Tesouro Selic 2029)")
        valor_investido = st.number_input("Valor Investido (R$)", min_value=0.0, step=100.0)
        taxa = st.text_input("Taxa (ex: 11% a.a ou 100% CDI)")
        if st.form_submit_button("Adicionar Renda Fixa"):
            # Como não criamos uma tabela nova, usamos a de portfolio com ticker customizado
            execute("INSERT INTO portfolio (ticker, quantity, average_price) VALUES (?, ?, ?) ON CONFLICT(ticker) DO UPDATE SET quantity=excluded.quantity, average_price=excluded.average_price", (f"RF: {nome} ({taxa})", 1, valor_investido))
            st.success("Adicionado!")
            st.rerun()
    
    renda_fixa_db = query_all("SELECT * FROM portfolio WHERE ticker LIKE 'RF:%'")
    for rf in renda_fixa_db:
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;"><div class="titulo">{rf['ticker']}</div><div class="valor">R$ {rf['average_price']:.2f}</div></div>""", unsafe_allow_html=True)

with tab_gastos:
    with st.form("form_gasto"):
        desc = st.text_input("Descrição")
        val = st.number_input("Valor (R$)", min_value=0.0)
        if st.form_submit_button("Registrar Gasto"):
            execute("INSERT INTO expenses (expense_date, description, amount) VALUES (?, ?, ?)", (date.today().isoformat(), desc, val))
            st.rerun()
    for g in query_all("SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 10"):
        st.markdown(f"- {g['description']}: R$ {g['amount']:.2f} ({g['expense_date']})")
