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
    st.subheader("🏛️ Notícias Legislativas de Hoje")
    if st.button("🧠 Gerar Resumo de Notícias", use_container_width=True):
        with st.spinner("Lendo Câmara, Senado, ALERJ e Macaé..."):
            # Simulando a chamada da API local (no Render) - vamos chamar direto a função
            try:
                # No app local não tem como chamar a API protegida, então vamos ler direto
                import feedparser
                from bs4 import BeautifulSoup
                noticias = []
                
                f1 = feedparser.parse("https://www.camara.leg.br/noticias/rss/ultimas-noticias")
                for e in f1.entries[:2]: noticias.append(f"[Câmara] {e.title}")
                f2 = feedparser.parse("https://www12.senado.leg.br/noticias/RSS")
                for e in f2.entries[:2]: noticias.append(f"[Senado] {e.title}")
                f3 = feedparser.parse("https://news.google.com/rss/search?q=alerj+noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419")
                for e in f3.entries[:2]: noticias.append(f"[ALERJ] {e.title}")
                f4 = feedparser.parse("https://news.google.com/rss/search?q=camara+macae+noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419")
                for e in f4.entries[:2]: noticias.append(f"[Macaé] {e.title}")
                
                prompt = f"Resuma as notícias a seguir em tópicos e explique o impacto prático:\n" + "\n".join(noticias)
                resumo = ask_gemini(prompt)
                st.markdown(f'<div class="samurai-card" style="border-left-color: #8B0000;"><div style="white-space: pre-wrap;">{resumo}</div></div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro ao carregar notícias: {e}")
    st.divider()
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
    st.subheader("⚡ Consolidador de Notícias do Dia")
    st.write("A IA vai ler todas as newsletters que chegaram hoje, remover notícias repetidas e unificar as informações em um único resumo.")
    
    if st.button("🧠 Consolidar Notícias de Hoje", use_container_width=True):
        from datetime import date
        hoje = date.today().isoformat()
        
        # Busca todos os e-mails recebidos hoje
        emails_hoje = query_all("SELECT subject, content FROM newsletters_inbox WHERE received_at LIKE ?", (f"{hoje}%",))
        
        if not emails_hoje:
            st.warning("Nenhuma newsletter recebida hoje. O Pipedream precisa capturar algum e-mail primeiro.")
        else:
            with st.spinner(f"Lendo {len(emails_hoje)} newsletter(s) e consolidando com a IA..."):
                # Junta todos os textos
                texto_total = "\n\n".join([f"--- NEWSLETTER: {e['subject']} ---\n{e['content']}" for e in emails_hoje])
                
                prompt = f"""Atue como o Editor-Chefe do 'Samurai Brief', um boletim diário focado em alta performance, negócios, tecnologia e geopolítica.

Abaixo está a matéria-prima bruta de várias newsletters que chegaram hoje.
Sua missão OBRIGATÓRIA:
1. **Desduplicação:** Se duas ou mais newsletters trazem a mesma notícia, REMOVA as repetições.
2. **Enriquecimento:** Se houver informações complementares sobre o mesmo fato, mescle-as em um único parágrafo robusto.
3. **Curadoria:** Descarte fofocas irrelevantes ou notícias que não agregam valor estratégico (ex: celebridades, esportes, entretenimento raso).
4. **Estrutura:** Organize o texto final em tópicos com títulos atraentes (Ex: 🚀 Tech & Inovação, 💼 Negócios, 🌍 Geopolítica, 💡 Curiosidades).
5. **Tom:** Seja direto, ágil, provocativo e informativo (estilo The Hustle).
6. **Formatação:** Use Markdown (negrito, itálico, listas).

Aqui está o conteúdo de hoje:
{texto_total[:30000]}
"""
                resumo_unificado = ask_gemini(prompt)
                st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Samurai Brief Consolidado</div><div style="white-space: pre-wrap;">{resumo_unificado}</div></div>', unsafe_allow_html=True)
    
    st.divider()
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
