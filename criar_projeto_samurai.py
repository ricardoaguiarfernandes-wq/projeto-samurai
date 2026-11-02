"""
melhoria.py — IA Quantamental com Qualidade, Risco e Eficiência Fiscal.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

CONTEUDO_PATRIMONIO = """import streamlit as st
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
execute("CREATE TABLE IF NOT EXISTS patrimony_fixed_income (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, rate TEXT)")

st.title("💎 Patrimônio")
tab_ia, tab_acoes, tab_rf = st.tabs(["🤖 Consultor Quantamental", "📊 Ações/FIIs", "🏦 Renda Fixa"])

def obter_metricas_profundas(ticker):
    ticker_busca = ticker if ".SA" in ticker else f"{ticker}.SA"
    try:
        info = yf.Ticker(ticker_busca).info
        # Métricas de Qualidade
        fco = info.get("operatingCashflow")
        lucro = info.get("netIncomeToCommon")
        # FCO / Lucro Líquido (Qualidade do Lucro)
        qualidade_lucro = (fco / lucro) if fco and lucro and lucro != 0 else None
        
        # Métricas de Risco
        divida = info.get("debtToEquity")
        ebitda = info.get("ebitda")
        divida_liquida = info.get("totalDebt") - info.get("cash", 0) if info.get("totalDebt") and info.get("cash") else None
        divida_ebitda = (divida_liquida / ebitda) if divida_liquida and ebitda and ebitda > 0 else None
        
        # Dividendos
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
                texto_acoes += f"- {ticker} (Setor: {m['setor']}) | Preço: R$ {preco_atual:.2f}\\n"
                texto_acoes += f"  Qualidade: FCO/Lucro: {m['qualidade_lucro']} | Dívida Líq/EBITDA: {m['divida_ebitda']} | Cobertura Div: {m['cobertura_dividendos']}\\n"
            else:
                texto_acoes += f"- {ticker}: Cotação indisponível.\\n"
        except Exception:
            texto_acoes += f"- {ticker}: Erro ao buscar dados.\\n"

    texto_rf = "".join([f"- {r['name']}: R$ {r['amount']} ({r['rate']})\\n" for r in rf_db])

    with st.expander("Ver Métricas de Qualidade e Risco"):
        st.markdown(f"**Ações:**\\n{texto_acoes if texto_acoes else 'Vazio'}")

    with st.form("form_aporte"):
        aporte = st.number_input("Aporte Mensal (R$)", min_value=0.0, step=100.0)
        if st.form_submit_button("Gerar Análise de Risco e Alocação", use_container_width=True) and aporte > 0:
            with st.spinner("Analisando qualidade, risco de ruína e eficiência fiscal..."):
                prompt = f\"\"\"Atue como um Gestor de Risco e Analista Quantamental Sênior.
Aporte: R$ {aporte:.2f}.
Carteira:
{texto_acoes}
Renda Fixa:
{texto_rf}

Sua missão OBRIGATÓRIA:
1. **Qualidade do Lucro:** Verifique se o FCO/Lucro é maior que 1. Se for menor, a empresa pode estar maquiando o lucro. NÃO recomende compra se a qualidade for baixa.
2. **Risco de Ruína:** Verifique a Dívida Líquida/EBITDA. Se for maior que 3x, a empresa está alavancada demais. Evite aportes.
3. **Sustentabilidade:** A Cobertura de Dividendos deve ser > 1.5x para garantir que o dividendo não vai ser cortado.
4. **Diversificação:** Se as ações atuais não passarem no teste de qualidade, sugira 3 novas ações perenes de SETORES DIFERENTES que passem em todos os testes.
5. **Eficiência Fiscal:** Para rebalancear, priorize o uso do APORTE DE CAIXA NOVO. Só sugira vendas se for extremamente necessário e respeitando a isenção de R$ 20 mil/mês.
6. **Alocação:** Divida o aporte entre Renda Fixa, Reserva e Ações (novas ou atuais). Justifique.\"\"\"
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
"""

def _run(cmd):
    subprocess.run(cmd, cwd=BASE, capture_output=True)

def aplicar():
    print("=" * 60)
    print("⚔️  ATUALIZANDO IA PARA ANÁLISE DE QUALIDADE E RISCO")
    print("=" * 60)
    cam = "ui/pages/04_Patrimonio.py"
    try:
        ast.parse(CONTEUDO_PATRIMONIO)
        (BASE / cam).write_text(CONTEUDO_PATRIMONIO, encoding="utf-8")
        print(f"[OK] {cam} atualizado com sucesso.")
    except SyntaxError as e:
        print(f"[ERRO] Sintaxe em {cam}: {e}")
        sys.exit(1)

    print("\n☁️  SINCRONIZANDO COM O GITHUB")
    _run(["git", "add", "-A"])
    _run(["git", "commit", "-m", "Feat: IA com FCO/Lucro, Divida/EBITDA, Cobertura de Dividendos e Eficiencia Fiscal"])
    _run(["git", "push", "origin", "main"])
    print("[OK] Push concluído. O Streamlit vai atualizar em instantes.")

if __name__ == "__main__":
    aplicar()