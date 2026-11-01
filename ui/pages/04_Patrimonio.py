import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf
import pandas as pd

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db
from services.ai import ask_gemini

init_db()

st.title("💎 Patrimônio")
st.caption("Sua corretora pessoal e consultor financeiro IA.")

# ==============================================================================
# 1. MINHA CARTEIRA (AÇÕES E FIIs)
# ==============================================================================
st.subheader("📊 Minha Carteira")

# Busca os ativos no banco
carteira_db = query_all("SELECT * FROM portfolio ORDER BY ticker")

# Formulário para adicionar/atualizar ativo
with st.expander("➕ Adicionar / Editar Ativo"):
    with st.form("form_ativo"):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            ticker_input = st.text_input("Ticker (ex: PETR4.SA, HGLG11.SA)").upper()
        with col2:
            qtd = st.number_input("Quantidade", min_value=1, step=1, value=100)
        with col3:
            preco_medio = st.number_input("Preço Médio (R$)", min_value=0.01, step=0.01, value=30.00)
            
        submit_ativo = st.form_submit_button("Salvar Ativo", use_container_width=True)
        
        if submit_ativo and ticker_input:
            execute(
                """
                INSERT INTO portfolio (ticker, quantity, average_price)
                VALUES (?, ?, ?)
                ON CONFLICT(ticker) DO UPDATE SET
                    quantity = excluded.quantity,
                    average_price = excluded.average_price
                """, (ticker_input, qtd, preco_medio)
            )
            st.success(f"Ativo {ticker_input} salvo!")
            st.rerun()

# Exibição da carteira e cálculo de lucro/prejuízo
if not carteira_db:
    st.info("Sua carteira está vazia. Adicione seu primeiro ativo acima.")
else:
    total_investido = 0.0
    total_atual = 0.0
    
    for ativo in carteira_db:
        ticker = ativo["ticker"]
        qtd = ativo["quantity"]
        preco_medio = ativo["average_price"]
        
        try:
            # Busca cotação atual
            data = yf.Ticker(ticker).history(period="1d")
            if not data.empty:
                preco_atual = data['Close'].iloc[-1]
            else:
                preco_atual = preco_medio # Fallback
        except Exception:
            preco_atual = preco_medio
            
        valor_investido = qtd * preco_medio
        valor_atual = qtd * preco_atual
        lucro = valor_atual - valor_investido
        rentabilidade = (lucro / valor_investido) * 100 if valor_investido > 0 else 0
        
        total_investido += valor_investido
        total_atual += valor_atual
        
        cor = "#4CAF50" if lucro >= 0 else "#F44336"
        
        # Exibe o card do ativo
        st.markdown(
            f"""<div class="samurai-card" style="border-left-color: {cor}; padding: 12px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <div class="titulo">{ticker}</div>
                        <div class="valor" style="font-size: 1.2rem;">R$ {preco_atual:.2f}</div>
                        <div class="detalhe">{qtd} cotas @ R$ {preco_medio:.2f}</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: {cor}; font-weight: bold; font-size: 1.1rem;">
                            {'+' if lucro >= 0 else ''}{lucro:.2f} R$
                        </div>
                        <div style="color: {cor}; font-size: 0.85rem;">({rentabilidade:+.2f}%)</div>
                        <div style="font-size: 0.75rem; color: #888;">Total: R$ {valor_atual:.2f}</div>
                    </div>
                </div>
            </div>""",
            unsafe_allow_html=True
        )

    # Resumo da Carteira
    st.divider()
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.metric("Total Investido", f"R$ {total_investido:.2f}")
    with col_t2:
        st.metric("Valor Atual", f"R$ {total_atual:.2f}")
    with col_t3:
        rent_total = ((total_atual - total_investido) / total_investido) * 100 if total_investido > 0 else 0
        st.metric("Rentabilidade", f"{rent_total:+.2f}%", delta=f"R$ {total_atual - total_investido:.2f}")

    # ==============================================================================
    # 2. CONSULTOR IA
    # ==============================================================================
    st.divider()
    st.subheader("🧠 Consultor de Patrimônio IA")
    if st.button("📜 Gerar Sugestão Diária com IA", use_container_width=True):
        with st.spinner("O Mentor está analisando o mercado e sua carteira..."):
            # Monta o texto da carteira para a IA
            texto_carteira = ""
            for ativo in carteira_db:
                texto_carteira += f"- {ativo['ticker']}: {ativo['quantity']} cotas, preço médio R$ {ativo['average_price']:.2f}\n"
            
            prompt = f"""Atue como um consultor de investimentos sênior e estrategista financeiro. 
O usuário possui a seguinte carteira de ações/FIIs:
{texto_carteira}
Valor total investido: R$ {total_investido:.2f}
Valor atual: R$ {total_atual:.2f}
Rentabilidade: {rent_total:+.2f}%

Com base nesses dados e no cenário macroeconômico atual, forneça uma análise curta (máximo 3 parágrafos) e direta. 
Dê uma sugestão prática para o dia de hoje (ex: aportar em X, manter, realizar lucro em Y). 
Mantenha um tom sério, profissional e focado no longo prazo e na disciplina financeira."""
            
            conselho = ask_gemini(prompt)
            
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
                    <div class="titulo">Análise do Consultor</div>
                    <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{conselho}</div>
                </div>""",
                unsafe_allow_html=True
            )

# ==============================================================================
# 3. REGISTRO DE GASTOS (Mantido do original)
# ==============================================================================
st.divider()
st.subheader("💸 Registro de Gastos")

with st.form("form_gasto"):
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        descricao = st.text_input("Descrição")
    with col2:
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
    with col3:
        categoria = st.selectbox("Categoria", ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Outros"])
    
    submitted = st.form_submit_button("Registrar Gasto", use_container_width=True)

if submitted:
    if descricao and valor > 0:
        execute(
            "INSERT INTO expenses (expense_date, description, amount, category) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), descricao, valor, categoria)
        )
        st.success("Gasto registrado!")
        st.rerun()
    else:
        st.error("Preencha a descrição e um valor maior que zero.")

gastos = query_all("SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 5")
if gastos:
    st.markdown("### Últimos Gastos")
    for g in gastos:
        st.markdown(
            f"""<div class="samurai-card" style="border-left-color: #171717; padding: 10px;">
                <div style="display: flex; justify-content: space-between; color: #CCC;">
                    <span>{g['description']}</span>
                    <span>R$ {g['amount']:.2f} ({g['category']})</span>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
