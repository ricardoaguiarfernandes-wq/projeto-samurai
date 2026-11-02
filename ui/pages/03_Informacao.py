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
from core.database import query_all, execute
from services.ai import ask_gemini

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
    st.subheader("🗞️ Últimas Newsletters recebidas")
    emails = query_all("SELECT subject, sender, content, received_at FROM newsletters_inbox ORDER BY received_at DESC LIMIT 5")
    
    if not emails:
        st.info("Nenhuma newsletter recebida ainda. (O Pipedream enviará assim que chegar um e-mail).")
    else:
        for e in emails:
            with st.expander(f"✉️ {e['subject']} (De: {e['sender']})"):
                st.caption(f"Recebido em: {e['received_at']}")
                # Mostra os primeiros 1500 caracteres (já limpos pelo backend)
                st.markdown(f"<div style='max-height: 300px; overflow-y: auto;'>{e['content'][:1500]}...</div>", unsafe_allow_html=True)

with tab_newsletter:
    st.subheader("📜 Histórico do Samurai Brief")
    try:
        briefs = query_all("SELECT * FROM daily_briefs ORDER BY brief_date DESC LIMIT 7")
    except Exception:
        execute("CREATE TABLE IF NOT EXISTS daily_briefs (id INTEGER PRIMARY KEY AUTOINCREMENT, brief_date TEXT NOT NULL UNIQUE, content TEXT NOT NULL)")
        briefs = []
    
    if not briefs:
        st.info("Nenhum Brief gerado ainda. O Telegram deve enviar o primeiro amanhã às 6h.")
    else:
        for b in briefs:
            with st.expander(f"📅 Brief de {b['brief_date']}"):
                st.markdown(f'<div class="samurai-card" style="border-left-color: #8B0000;"><div style="white-space: pre-wrap;">{b["content"]}</div></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("📥 Caixa de Entrada (E-mails Brutos)")
    emails = query_all("SELECT * FROM newsletters_inbox ORDER BY received_at DESC LIMIT 5")
    if not emails:
        st.caption("Nenhum e-mail recebido via Power Automate.")
    else:
        for e in emails:
            with st.expander(f"✉️ {e['subject']}"):
                st.markdown(f"<div style='max-height: 300px; overflow-y: auto;'>{e['content']}</div>", unsafe_allow_html=True)
