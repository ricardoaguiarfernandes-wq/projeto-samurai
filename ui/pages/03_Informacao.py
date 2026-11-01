import streamlit as st
import sys
from pathlib import Path
import yfinance as yf
import requests
import feedparser

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db

init_db()

st.title("📰 Informação")
st.caption("Mundo, Brasil, Macaé, Legislativo e Finanças.")

# --- FINANÇAS ---
st.subheader("📈 Finanças (Tempo Real)")
col1, col2, col3 = st.columns(3)
tickers = {"Dólar": "BRL=X", "IBOVESPA": "^BVSP", "Bitcoin": "BTC-USD"}
cols = [col1, col2, col3]

for i, (nome, ticker) in enumerate(tickers.items()):
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            preco = data['Close'].iloc[-1]
            with cols[i]:
                st.markdown(
                    f"""<div class="samurai-card">
                        <div class="titulo">{nome}</div>
                        <div class="valor">R$ {preco:,.2f}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )
    except Exception:
        with cols[i]:
            st.error(f"Erro ao carregar {nome}")

st.divider()

# --- NOTÍCIAS ---
st.subheader("🗞️ Últimas Notícias (G1)")
try:
    url = "https://g1.globo.com/rss/g1/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status() # Levanta um erro se a requisição falhar
    
    feed = feedparser.parse(response.content)
    
    if feed.entries:
        for entry in feed.entries[:5]:
            st.markdown(f"- [{entry.title}]({entry.link})")
    else:
        st.warning("O feed de notícias está vazio no momento.")
except requests.exceptions.RequestException:
    st.warning("Não foi possível carregar as notícias (servidor do G1 fora do ar ou bloqueando a conexão).")
except Exception as e:
    st.warning("Erro inesperado ao carregar as notícias.")

st.divider()
st.subheader("⚖️ Legislativo")
st.info("🚧 Integração com APIs do Senado, Câmara, ALERJ e Câmara de Macaé será implementada na Sprint 4.")
