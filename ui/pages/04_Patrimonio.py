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

st.title("💎 Patrimônio")
tab_ia, tab_chat, tab_acoes, tab_rf = st.tabs(["🤖 Consultor Quantamental", "💬 Chat com Analista", "📊 Ações/FIIs", "🏦 Renda Fixa"])

def obter_metricas_profundas(ticker):
    ticker_busca = ticker if ".SA" in ticker else f"{ticker}.SA"
    try:
        info = yf.Ticker(ticker_busca).info
        fco = info.get("operatingCashflow")
        lucro = info.get("netIncomeToCommon")
        qualidade_lucro = (fco / lucro) if fco and lucro and lucro != 0 else None
        
        ebitda = info.get("ebitda")
        divida_liquida = info.get("totalDebt") - info.get("cash", 0) if info.get("totalDebt") and info.get("cash") else None
        divida_ebitda = (divida_liquida / ebitda) if divida_liquida and ebitda and ebitda > 0 else None
        
        dy = info.get("dividendYield")
        dividendos_pagos = (info.get("dividendRate", 0) * info.get("sharesOutstanding", 1)) if info.get("dividendRate") else None
        cobertura_dividendos = (fco / dividendos_pagos) if fco and dividendos_pagos and dividendos_pagos > 0 else None
        
        setor = info.get("sector", "Desconhecido")
        
        return {
            "qualidade_lucro": f"{qualidade_lucro:.2f}" if qualidade_lucro else "N/A",
            "divida_ebitda": f"{divida_ebitda:.2f}x" if divida_ebitda else "N/A",
            "cobertura_dividendos": f"{cobertura_dividendos:.2f}x" if cobertura_dividendos else "N/A",
            "setor": setor
        }
    except Exception:
        return {"qualidade_lucro": "N/A", "divida_ebitda": "N/A", "cobertura_dividendos": "N/A", "setor": "N/A"}

with tab_ia:
    st.header("Mentor Quantamental (Qualidade e Risco)")
    acoes_db = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE 'RF:%'")
    rf_db = query_all("SELECT * FROM patrimony_fixed_income")

    texto_acoes = ""
    for a in acoes_db:
        ticker = a['ticker']
        ticker_busca = ticker if ".SA" in ticker else f"{ticker}.SA"
        try:
            data = yf.Ticker(ticker_busca).history(period="5d")
            if data.empty: data = yf.Ticker(ticker_busca).history(period="max")
            if not data.empty:
                preco_atual = float(data['Close'].iloc[-1])
                m = obter_metricas_profundas(ticker)
                texto_acoes += f"- {ticker} (Setor: {m['setor']}) | Preço: R$ {preco_atual:.2f} | Qualidade Lucro: {m['qualidade_lucro']} | Dívida/EBITDA: {m['divida_ebitda']} | Cobertura Div: {m['cobertura_dividendos']}\n"
            else:
                texto_acoes += f"- {ticker}: Cotação indisponível.\n"
        except Exception:
            texto_acoes += f"- {ticker}: Erro ao buscar dados.\n"

    texto_rf = "".join([f"- {r['name']}: R$ {r['amount']} ({r['rate']})\n" for r in rf_db])

    with st.expander("Ver Métricas de Qualidade e Risco"):
        st.markdown(f"**Ações:**\n{texto_acoes if texto_acoes else 'Vazio'}")

    with st.form("form_aporte"):
        aporte = st.number_input("Aporte Mensal (R$)", min_value=0.0, step=100.0)
        if st.form_submit_button("Gerar Análise de Risco e Alocação", use_container_width=True) and aporte > 0:
            with st.spinner("Analisando qualidade, risco e definindo os Tickers exatos..."):
                prompt = f"""Atue como um Gestor de Risco e Analista Quantamental Sênior.
Aporte: R$ {aporte:.2f}.
Carteira:
{texto_acoes}
Renda Fixa:
{texto_rf}

Sua missão OBRIGATÓRIA (Seja direto e cirúrgico):
1. **Auditoria:** Avalie minhas ações atuais usando as métricas fornecidas (Qualidade Lucro, Dívida/EBITDA, Cobertura Div). Se alguma estiver com dados ruins, diga que não vai aportar nela.
2. **Escolha das Novas Ações (PROIBIDO USAR "OU"):** Você deve escolher EXATAMENTE 3 TICKERS de ações perenes em SETORES DIFERENTES (ex: Energia, Saneamento, Seguros, Consumo). 
   - NÃO dê opções como "TAEE11 ou ENEV". Escolha UM e justifique com base no histórico de dividendos, monopólio e resiliência.
3. **Alocação Centavo por Centavo:** Divida o aporte de R$ {aporte:.2f}. Diga exatamente quanto vai em Renda Fixa, quanto na Reserva e quanto em CADA UMA das 3 ações escolhidas (cite o ticker exato e o valor: "Compre R$ 300,00 de TAEE11.SA").
4. **Eficiência Fiscal:** Priorize o aporte de caixa novo. Só sugira venda se for extremamente necessário, lembrando da isenção de R$ 20 mil.
5. **Justificativa:** Para cada ação escolhida, explique o porquê (ex: "Escolhi CXSE3 porque tem baixo uso de capital e alto dividend yield").

Mantenha um tom profissional e focado em longo prazo."""
                st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Análise de Risco e Alocação</div><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>', unsafe_allow_html=True)

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
        st.markdown(f'<div class="samurai-card" style="padding: 10px;"><b>{a["ticker"]}</b> - {a["quantity"]} cotas @ R$ {a["average_price"]:.2f}</div>', unsafe_allow_html=True)

with tab_rf:
    st.subheader("Adicionar Renda Fixa")
    with st.form("f_rf"):
        n = st.text_input("Nome (ex: CDB Banco X)")
        v = st.number_input("Valor (R$)", min_value=0.0, step=100.0)
        col1, col2 = st.columns(2)
        with col1: tipo = st.selectbox("Indexador", ["% do CDI", "% a.a.", "IPCA +"])
        with col2: taxa = st.number_input("Taxa", min_value=0.0, step=0.1)
        if st.form_submit_button("Adicionar"):
            execute("INSERT INTO patrimony_fixed_income (name, amount, rate) VALUES (?, ?, ?)", (n, v, f"{taxa} {tipo}"))
            st.rerun()
    st.divider()
    for rf in query_all("SELECT * FROM patrimony_fixed_income"):
        st.markdown(f'<div class="samurai-card" style="border-left-color: #2196F3;"><b>{rf["name"]}</b> - R$ {rf["amount"]:.2f} ({rf["rate"]})</div>', unsafe_allow_html=True)

# ==============================================================================
# ABA CHAT: Analista Quantamental
# ==============================================================================
with tab_chat:
    st.header("💬 Chat com o Mentor Financeiro")
    st.write("Pergunte sobre ações específicas, dividendos, riscos ou peça conselhos sobre a sua carteira.")
    
    # Pega a carteira atual para dar contexto à IA
    acoes_db = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE 'RF:%'")
    rf_db = query_all("SELECT * FROM patrimony_fixed_income")
    
    ctx_carteira = "CARTEIRA ATUAL DO USUÁRIO:\n"
    if acoes_db:
        ctx_carteira += "Ações/FIIs:\n"
        for a in acoes_db:
            ctx_carteira += f"- {a['ticker']}: {a['quantity']} cotas, Preço Médio R$ {a['average_price']:.2f}\n"
    else:
        ctx_carteira += "Ações: Carteira vazia.\n"
        
    if rf_db:
        ctx_carteira += "Renda Fixa:\n"
        for r in rf_db:
            ctx_carteira += f"- {r['name']}: R$ {r['amount']} ({r['rate']})\n"
    else:
        ctx_carteira += "Renda Fixa: Carteira vazia.\n"

    if "fin_chat" not in st.session_state:
        st.session_state.fin_chat = []

    # Exibe o histórico
    for msg in st.session_state.fin_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input do usuário
    if prompt_user := st.chat_input("Ex: Vale a pena comprar CXSE3 agora? Ou: Analise minha carteira."):
        st.session_state.fin_chat.append({"role": "user", "content": prompt_user})
        with st.chat_message("user"):
            st.markdown(prompt_user)

        with st.chat_message("assistant"):
            with st.spinner("Analisando fundamentos e carteira..."):
                # Pega as últimas 10 mensagens para dar contexto (memória)
                historico_recente = ""
                for msg in st.session_state.fin_chat[-10:]:
                    role = "Usuário" if msg["role"] == "user" else "Mentor"
                    historico_recente += f"{role}: {msg['content']}\n\n"

                prompt_ia = f"""Atue como o Mentor Financeiro Samurai, um Analista Quantamental Sênior focado em valor, dividendos e proteção patrimonial.

{ctx_carteira}

HISTÓRICO DA CONVERSA (Para você manter o contexto):
{historico_recente}

O usuário perguntou agora: "{prompt_user}"

Sua missão:
1. Responda de forma direta, profissional e focada no longo prazo, dando CONTINUIDADE à conversa anterior.
2. **Atenção às Listas:** Se o usuário pedir uma lista de ações, sugestões ou disser "quero uma lista dos 1%", você DEVE listar explicitamente os tickers específicos que se encaixam na sua filosofia de valor (ex: TAEE11, BBAS3, CXSE3, SAPR11, ALUP11, etc.) e explicar o porquê de forma resumida. Não devolva a pergunta para o usuário.
3. Se ele perguntar sobre uma ação específica, analise os fundamentos e dê uma opinião CRAVADA (comprar, manter ou vender). NUNCA use "ou" para dar opções; escolha o melhor caminho.
4. Se ele pedir para analisar a carteira, verifique a diversificação setorial e aponte pontos de melhoria.
5. Lembre-se da filosofia Samurai: disciplina e consistência vencem a emoção do mercado. Não faça alucinações com cotações atuais; foque nos fundamentos.
"""
                resposta = ask_gemini(prompt_ia)
                st.markdown(resposta)
                
        st.session_state.fin_chat.append({"role": "assistant", "content": resposta})
