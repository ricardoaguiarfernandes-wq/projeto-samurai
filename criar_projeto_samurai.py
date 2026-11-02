"""
aplicar_melhoria.py — IA Quantamental: Análise profunda com métricas fundamentalistas.
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
    \"\"\"Busca um pacote completo de métricas fundamentalistas para a IA.\"\"\"
    ticker_busca = ticker if ".SA" in ticker else f"{ticker}.SA"
    try:
        info = yf.Ticker(ticker_busca).info
        # Extrai as métricas de forma segura
        pl = info.get("trailingPE")
        pvp = info.get("priceToBook")
        dy = info.get("dividendYield")
        roe = info.get("returnOnEquity")
        divida = info.get("debtToEquity")
        margem = info.get("profitMargins")
        setor = info.get("sector", "Desconhecido")
        
        # Formata para porcentagem e arredonda
        return {
            "pl": f"{pl:.2f}" if pl else "N/A",
            "pvp": f"{pvp:.2f}" if pvp else "N/A",
            "dy": f"{dy*100:.2f}%" if dy else "N/A",
            "roe": f"{roe*100:.2f}%" if roe else "N/A",
            "divida": f"{divida:.2f}%" if divida else "N/A",
            "margem": f"{margem*100:.2f}%" if margem else "N/A",
            "setor": setor
        }
    except Exception:
        return {"pl": "N/A", "pvp": "N/A", "dy": "N/A", "roe": "N/A", "divida": "N/A", "margem": "N/A", "setor": "N/A"}

with tab_ia:
    st.header("Mentor Financeiro Quantamental")
    st.write("A IA agora analisa múltiplos fundamentalistas reais (P/L, P/VP, ROE, Dívida/Patrimônio) para decidir se um ativo está realmente descontado.")
    
    acoes_db = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE 'RF:%'")
    rf_db = query_all("SELECT * FROM patrimony_fixed_income")

    texto_acoes = ""
    for a in acoes_db:
        ticker = a['ticker']
        ticker_busca = ticker if ".SA" in ticker else f"{ticker}.SA"
        
        try:
            ticker_obj = yf.Ticker(ticker_busca)
            data = ticker_obj.history(period="5d")
            if data.empty: data = ticker_obj.history(period="max")
            
            if not data.empty:
                preco_atual = float(data['Close'].iloc[-1])
                lucro_pct = ((preco_atual / a['average_price']) - 1) * 100
                m = obter_metricas_profundas(ticker)
                
                texto_acoes += f"- {ticker} (Setor: {m['setor']}): {a['quantity']} cotas | PM: R$ {a['average_price']:.2f} | Atual: R$ {preco_atual:.2f} | Rent: {lucro_pct:.2f}%\\n"
                texto_acoes += f"  Métricas: P/L: {m['pl']} | P/VP: {m['pvp']} | DY: {m['dy']} | ROE: {m['roe']} | Dívida/Patrimônio: {m['divida']} | Margem Líq: {m['margem']}\\n"
            else:
                texto_acoes += f"- {ticker}: Cotação indisponível (PM: R$ {a['average_price']:.2f})\\n"
        except Exception:
            texto_acoes += f"- {ticker}: Erro ao buscar dados (PM: R$ {a['average_price']:.2f})\\n"

    texto_rf = "".join([f"- {r['name']}: R$ {r['amount']} (Taxa: {r['rate']})\\n" for r in rf_db])

    with st.expander("Ver Carteira Atual e Métricas"):
        st.markdown(f"**Ações:**\\n{texto_acoes if texto_acoes else 'Vazio'}")
        st.markdown(f"**Renda Fixa:**\\n{texto_rf if texto_rf else 'Vazio'}")

    with st.form("form_aporte"):
        aporte = st.number_input("Quanto você tem para investir este mês? (R$)", min_value=0.0, step=100.0)
        if st.form_submit_button("Gerar Análise Quantamental e Alocação", use_container_width=True) and aporte > 0:
            with st.spinner("Cruzando dados fundamentalistas e analisando o mercado..."):
                
                prompt = f\"\"\"Atue como um Analista Quantamental Sênior (unindo análise quantitativa e fundamentalista).
Tenho R$ {aporte:.2f} para investir.
Minha carteira (estratégia Buy and Hold, ativos perenes, NUNCA vender):
{texto_acoes}
Renda Fixa:
{texto_rf}

Sua missão OBRIGATÓRIA:
1. Analise minhas ações atuais usando as métricas fornecidas. Uma ação está "descontada" se o P/L for baixo para o setor, o DY for alto e o ROE for consistente. NÃO invente dados que não estão no texto.
2. Se as ações atuais NÃO estiverem baratas, sugira EXATAMENTE 3 NOVAS AÇÕES PERENES.
3. **REGRA DE OURO DA DIVERSIFICAÇÃO:** As 3 ações DEVEM ser de setores DIFERENTES (ex: Energia, Saneamento, Bancos, Papel). Nunca 3 do mesmo setor.
4. Para cada nova ação, justifique citando P/L, DY e ROE estimados, e por que é um bom momento de compra.
5. Faça a divisão exata do aporte de R$ {aporte:.2f} entre Renda Fixa, Reserva de Oportunidade e as Ações (novas ou atuais). Justifique centavo por centavo.

Seja cirúrgico, profissional e focado em resultados de longo prazo.\"\"\"
                
                st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Análise Quantamental</div><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>', unsafe_allow_html=True)

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
"""

def _run(cmd):
    subprocess.run(cmd, cwd=BASE, capture_output=True)

def aplicar():
    print("=" * 60)
    print("⚔️  ATUALIZANDO IA PARA ANÁLISE QUANTAMENTAL")
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
    _run(["git", "commit", "-m", "Feat: IA Quantamental com metricas profundas e regra de diversificacao"])
    _run(["git", "push", "origin", "main"])
    print("[OK] Push concluído. O Streamlit vai atualizar em instantes.")
    print("=" * 60)

if __name__ == "__main__":
    aplicar()