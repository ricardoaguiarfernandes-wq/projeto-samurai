import streamlit as st
import sys
from pathlib import Path
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

st.title("⚡ The Samurai Brief")
st.caption("Curadoria diária e sua caixa de entrada.")

# --- NOVA SEÇÃO: CAIXA DE ENTRADA (POWER AUTOMATE) ---
st.subheader("📥 Caixa de Entrada (Emails)")
emails = query_all("SELECT * FROM newsletters_inbox ORDER BY received_at DESC LIMIT 10")
if not emails:
    st.info("Nenhuma newsletter recebida via Power Automate ainda.")
else:
    for e in emails:
        with st.expander(f"✉️ {e['subject']} (De: {e['sender']})"):
            st.markdown(f"**Recebido em:** {e['received_at']}")
            st.markdown("---")
            # O conteúdo pode vir em HTML ou Texto. O Streamlit renderiza HTML se pedirmos.
            st.markdown(e['content'], unsafe_allow_html=True)

st.divider()

# --- LEITURA DE NOTÍCIAS (RSS) ---
st.subheader("📰 Notícias do Dia (RSS)")

FEEDS = {
    "🇺🇸 The Hustle": "https://thehustle.co/feed/",
    "💻 TechCrunch": "https://techcrunch.com/feed/",
    "📈 InfoMoney": "https://www.infomoney.com.br/feed/"
}

def extrair_texto_artigo(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            texto = trafilatura.extract(downloaded)
            return texto if texto else ""
    except Exception:
        pass
    return ""

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_noticias():
    artigos = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    urls_para_baixar = []
    
    for fonte, url in FEEDS.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:2]:
                resumo = entry.get('summary', '')
                resumo_limpo = re.sub('<[^<]+?>', '', resumo).strip()
                artigos.append({
                    "fonte": fonte, "titulo": entry.title, "link": entry.link,
                    "resumo": resumo_limpo[:200] + "...", "texto_completo": ""
                })
                urls_para_baixar.append(entry.link)
        except Exception:
            pass

    with st.spinner("Extraindo o texto completo..."):
        with ThreadPoolExecutor(max_workers=5) as executor:
            resultados = list(executor.map(extrair_texto_artigo, urls_para_baixar))
            
    for i, texto in enumerate(resultados):
        artigos[i]["texto_completo"] = texto if texto else "Texto indisponível."
        base_tempo = texto if texto else artigos[i]["resumo"]
        artigos[i]["tempo"] = readtime.of_text(base_tempo).text

    return artigos

if st.button("🔄 Atualizar Notícias (RSS)", use_container_width=True):
    st.cache_data.clear()

with st.spinner("Lendo os feeds..."):
    artigos = buscar_noticias()

for fonte in FEEDS.keys():
    noticias_fonte = [a for a in artigos if a["fonte"] == fonte]
    if noticias_fonte:
        st.markdown(f"**{fonte}**")
        for noticia in noticias_fonte:
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #8B0000; padding: 10px;">
                    <div style="display: flex; justify-content: space-between;">
                        <div><b>{noticia['titulo']}</b></div>
                        <div style="background: #171717; padding: 2px 8px; border-radius: 5px; border: 1px solid #8B0000;">⏱️ {noticia['tempo']}</div>
                    </div>
                    <div style="color: #CCC; font-size: 0.85rem; margin-top: 5px;">{noticia['resumo']}</div>
                </div>""",
                unsafe_allow_html=True
            )
            with st.expander("📖 Ler Artigo Completo"):
                st.markdown(noticia['texto_completo'].replace("\n", "<br><br>"), unsafe_allow_html=True)
