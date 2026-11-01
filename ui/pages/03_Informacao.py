import streamlit as st
import sys
from pathlib import Path
import yfinance as yf
import requests
import feedparser
import readtime
import re
import trafilatura
from concurrent.futures import ThreadPoolExecutor

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db
from core.database import query_all

init_db()

st.title("📰 Informação & Notícias")
tab_financas, tab_newsletter = st.tabs(["📈 Finanças & Notícias Diárias", "⚡ The Samurai Brief"])

with tab_financas:
    st.subheader("Cotações (Tempo Real)")
    col1, col2, col3 = st.columns(3)
    tickers = {"Dólar": "BRL=X", "IBOVESPA": "^BVSP", "Bitcoin": "BTC-USD"}
    for i, (nome, ticker) in enumerate(tickers.items()):
        try:
            data = yf.Ticker(ticker).history(period="1d")
            if not data.empty:
                preco = data['Close'].iloc[-1]
                with [col1, col2, col3][i]:
                    st.markdown(f"""<div class="samurai-card"><div class="titulo">{nome}</div><div class="valor">R$ {preco:,.2f}</div></div>""", unsafe_allow_html=True)
        except: pass

    st.divider()
    st.subheader("🗞️ Últimas Notícias (G1)")
    try:
        url = "https://g1.globo.com/rss/g1/"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        feed = feedparser.parse(response.content)
        for entry in feed.entries[:5]: st.markdown(f"- [{entry.title}]({entry.link})")
    except: st.warning("Erro ao carregar notícias.")

with tab_newsletter:
    emails = query_all("SELECT * FROM newsletters_inbox ORDER BY received_at DESC LIMIT 5")
    if not emails:
        st.info("Nenhuma newsletter recebida ainda.")
    else:
        if st.button("📰 Gerar 'The Samurai Brief' do Dia (IA)", use_container_width=True):
            with st.spinner("Resumindo newsletters..."):
                from bs4 import BeautifulSoup
                texto = ""
                for e in emails[:3]:
                    soup = BeautifulSoup(e['content'], "html.parser")
                    texto += f"--- {e['subject']} ---\n{soup.get_text(strip=True)}\n"
                prompt = f"Atue como editor da newsletter The Hustle. Resuma os pontos principais:\n{texto}"
                resumo = ask_gemini(prompt)
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Edição de Hoje</div><div style="white-space: pre-wrap;">{resumo}</div></div>""", unsafe_allow_html=True)
        
        for e in emails:
            with st.expander(f"✉️ {e['subject']}"):
                st.markdown(f"<div style='max-height: 400px; overflow-y: auto;'>{e['content']}</div>", unsafe_allow_html=True)
