import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf
import pandas as pd

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()

# CORREÇÃO: Cria a tabela de Renda Fixa na hora, se não existir
execute("CREATE TABLE IF NOT EXISTS patrimony_fixed_income (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, rate TEXT)")

st.title("💎 Patrimônio")

tab_ia, tab_acoes, tab_rf = st.tabs(["🤖 Consultor IA", "📊 Ações/FIIs", "🏦 Renda Fixa"])

with tab_ia:
    st.header("Mentor Financeiro (CFP)")
    acoes_db = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE 'RF:%'")
    rf_db = query_all("SELECT * FROM patrimony_fixed_income")
    
    texto_acoes = "".join([f"- {a['ticker']}: {a['quantity']} cotas (PM: R$ {a['average_price']})\n" for a in acoes_db])
    texto_rf = "".join([f"- {r['name']}: R$ {r['amount']} (Taxa: {r['rate']})\n" for r in rf_db])
    
    with st.expander("Ver Carteira Atual (Base para a IA)"):
        st.markdown(f"**Ações:**\n{texto_acoes if texto_acoes else 'Vazio'}")
        st.markdown(f"**Renda Fixa:**\n{texto_rf if texto_rf else 'Vazio'}")
    
    with st.form("form_aporte"):
        aporte = st.number_input("Quanto você tem para investir este mês? (R$)", min_value=0.0, step=100.0)
        if st.form_submit_button("Gerar Plano de Alocação", use_container_width=True) and aporte > 0:
            with st.spinner("Analisando o mercado e sua carteira..."):
                prompt = f"""Atue como um Consultor Financeiro (CFP) sênior. 
Eu tenho R$ {aporte:.2f} para investir este mês.
Minha carteira atual:
AÇÕES/FIIs (NUNCA vender, são perenes):
{texto_acoes}
RENDA FIXA/RESERVA:
{texto_rf}

Sua missão:
1. Analise se as ações atuais estão em bom preço (descontadas). Se houver oportunidade, direcione parte do aporte para comprá-las.
2. Se não houver oportunidades claras, distribua o valor entre novas ações perenes, renda fixa (Tesouro Selic, CDBs) e reserva de oportunidade.
3. Detalhe exatamente onde alocar cada centavo (Ex: R$ 300 em PETR4, R$ 400 no Tesouro Selic, R$ 300 na reserva).
4. Justifique brevemente cada escolha."""
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Plano de Alocação do Mês</div><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)

with tab_acoes:
    carteira = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE 'RF:%'")
    with st.expander("➕ Adicionar Ação"):
        with st.form("f_a"):
            t = st.text_input("Ticker (ex: PETR4.SA)").upper()
            q = st.number_input("Qtd", min_value=1, value=100)
            p = st.number_input("Preço Médio", min_value=0.01, value=30.00)
            if st.form_submit_button("Salvar"):
                execute("INSERT INTO portfolio (ticker, quantity, average_price) VALUES (?, ?, ?) ON CONFLICT(ticker) DO UPDATE SET quantity=excluded.quantity, average_price=excluded.average_price", (t, q, p))
                st.rerun()
    for a in carteira:
        st.markdown(f"""<div class="samurai-card" style="padding: 10px;"><b>{a['ticker']}</b> - {a['quantity']} cotas @ R$ {a['average_price']:.2f}</div>""", unsafe_allow_html=True)

with tab_rf:
    st.subheader("Adicionar Renda Fixa")
    with st.form("f_rf"):
        n = st.text_input("Nome do Título (ex: CDB Banco X, Tesouro IPCA 2029)")
        v = st.number_input("Valor Investido (R$)", min_value=0.0, step=100.0)
        
        col1, col2 = st.columns(2)
        with col1:
            tipo_taxa = st.selectbox("Indexador", ["% do CDI", "% a.a.", "IPCA +"])
        with col2:
            valor_taxa = st.number_input("Valor da Taxa", min_value=0.0, step=0.1, help="Apenas o número. Ex: 110 para 110% do CDI ou 12.5 para 12,5% a.a.")
        
        taxa_final = f"{valor_taxa} {tipo_taxa}"
        
        if st.form_submit_button("Adicionar Renda Fixa"):
            execute("INSERT INTO patrimony_fixed_income (name, amount, rate) VALUES (?, ?, ?)", (n, v, taxa_final))
            st.success("Adicionado com sucesso!")
            st.rerun()
            
    st.divider()
    st.subheader("Seus Títulos")
    rf_db = query_all("SELECT * FROM patrimony_fixed_income")
    for rf in rf_db:
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;"><b>{rf['name']}</b> - R$ {rf['amount']:.2f} ({rf['rate']})</div>""", unsafe_allow_html=True)
