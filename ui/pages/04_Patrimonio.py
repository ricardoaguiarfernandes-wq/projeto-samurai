import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()

execute("CREATE TABLE IF NOT EXISTS patrimony_fixed_income (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, rate TEXT)")

st.title("💎 Patrimônio")
tab_ia, tab_acoes, tab_rf = st.tabs(["🤖 Consultor IA", "📊 Ações/FIIs", "🏦 Renda Fixa"])

with tab_ia:
    st.header("Mentor Financeiro (CFP)")
    acoes_db = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE 'RF:%'")
    rf_db = query_all("SELECT * FROM patrimony_fixed_income")

    # Busca a cotação real de cada ação
    texto_acoes = ""
    for a in acoes_db:
        ticker = a['ticker']
        # Garante que o ticker tenha o .SA para buscar no Yahoo Finance
        ticker_busca = ticker if ".SA" in ticker else f"{ticker}.SA"
        
        try:
            data = yf.Ticker(ticker_busca).history(period="1d")
            if not data.empty:
                preco_atual = data['Close'].iloc[-1]
                lucro_pct = ((preco_atual / a['average_price']) - 1) * 100
                texto_acoes += f"- {ticker}: {a['quantity']} cotas | Preço Médio: R$ {a['average_price']:.2f} | Cotação Atual: R$ {preco_atual:.2f} | Rentabilidade: {lucro_pct:.2f}%\n"
            else:
                texto_acoes += f"- {ticker}: {a['quantity']} cotas (PM: R$ {a['average_price']:.2f} | Cotação indisponível)\n"
        except Exception:
            texto_acoes += f"- {ticker}: {a['quantity']} cotas (PM: R$ {a['average_price']:.2f} | Erro na API)\n"

    texto_rf = "".join([f"- {r['name']}: R$ {r['amount']} (Taxa: {r['rate']})\n" for r in rf_db])

    with st.expander("Ver Carteira Atual (com cotações reais)"):
        st.markdown(f"**Ações:**\n{texto_acoes if texto_acoes else 'Vazio'}")
        st.markdown(f"**Renda Fixa:**\n{texto_rf if texto_rf else 'Vazio'}")

    with st.form("form_aporte"):
        aporte = st.number_input("Quanto você tem para investir este mês? (R$)", min_value=0.0, step=100.0)
        if st.form_submit_button("Gerar Plano de Alocação", use_container_width=True) and aporte > 0:
            with st.spinner("Analisando o mercado e buscando as melhores ações perenes..."):
                
                # Prompt reformulado para forçar a sugestão de 3 ações perenes
                prompt = f"""Atue como um Consultor Financeiro (CFP) sênior.
Tenho R$ {aporte:.2f} para investir este mês.
Minha carteira atual de ações perenes (Buy and Hold, NUNCA vender):
{texto_acoes}
Minha Renda Fixa:
{texto_rf}

Sua missão OBRIGATÓRIA:
1. Analise se as minhas ações atuais estão em bom preço de compra (descontadas).
2. Se as ações atuais NÃO estiverem descontadas, VOCÊ DEVE me apresentar EXATAMENTE 3 NOVAS AÇÕES PERENES (de setores como energia, saneamento, bancos, seguros, etc.) que estão atualmente com preço justo ou descontado.
3. Para cada uma das 3 ações sugeridas, explique em um parágrafo: Por que ela é perene (monopólio, moat, dividendos consistentes) e por que o preço está atrativo hoje.
4. Ao final, faça a divisão exata do aporte de R$ {aporte:.2f} entre Renda Fixa, Reserva de Oportunidade (para quedas futuras) e as Ações (seja nas atuais ou nas 3 novas sugeridas). Justifique a alocação centavo por centavo.

Mantenha um tom profissional, focado no longo prazo e na segurança do patrimônio."""
                
                st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Plano de Alocação</div><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>', unsafe_allow_html=True)

with tab_acoes:
    carteira = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE 'RF:%'")
    with st.expander("➕ Adicionar Ação"):
        with st.form("f_a"):
            t = st.text_input("Ticker (ex: PETR4.SA, BBAS3.SA)").upper()
            q = st.number_input("Qtd", min_value=1, value=100)
            p = st.number_input("Preço Médio", min_value=0.01, value=30.00)
            if st.form_submit_button("Salvar"):
                execute("INSERT INTO portfolio (ticker, quantity, average_price) VALUES (?, ?, ?) ON CONFLICT(ticker) DO UPDATE SET quantity=excluded.quantity, average_price=excluded.average_price", (t, q, p))
                st.rerun()
    for a in carteira:
        st.markdown(f'<div class="samurai-card" style="padding: 10px;"><b>{a["ticker"]}</b> - {a["quantity"]} cotas @ R$ {a["average_price"]:.2f}</div>', unsafe_allow_html=True)

with tab_rf:
    st.subheader("Adicionar Renda Fixa")
    with st.form("f_rf"):
        n = st.text_input("Nome (ex: CDB Banco X, Tesouro IPCA 2029)")
        v = st.number_input("Valor Investido (R$)", min_value=0.0, step=100.0)

        col1, col2 = st.columns(2)
        with col1: tipo_taxa = st.selectbox("Indexador", ["% do CDI", "% a.a.", "IPCA +"])
        with col2: valor_taxa = st.number_input("Valor da Taxa", min_value=0.0, step=0.1, help="Apenas o número. Ex: 110 para 110% do CDI.")

        taxa_final = f"{valor_taxa} {tipo_taxa}"
        if st.form_submit_button("Adicionar"):
            execute("INSERT INTO patrimony_fixed_income (name, amount, rate) VALUES (?, ?, ?)", (n, v, taxa_final))
            st.rerun()

    st.divider()
    rf_db = query_all("SELECT * FROM patrimony_fixed_income")
    for rf in rf_db:
        st.markdown(f'<div class="samurai-card" style="border-left-color: #2196F3;"><b>{rf["name"]}</b> - R$ {rf["amount"]:.2f} ({rf["rate"]})</div>', unsafe_allow_html=True)
