"""
Projeto Samurai — Sistema Operacional Pessoal.
Entry point Streamlit. Configura tema, navegação e injeta CSS.
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st

st.set_page_config(
    page_title="Projeto Samurai ⚔️",
    page_icon="⚔️",
    layout="centered",
    initial_sidebar_state="expanded",
)

from core.schema import init_db
from services.auth import check_password

# OTIMIZAÇÃO: Roda o init_db apenas uma vez por sessão, não a cada clique
@st.cache_resource
def setup_database():
    init_db()

setup_database()

# Bloqueia o app se a senha não estiver correta
if not check_password():
    st.stop()


SAMURAI_CSS = """
<style>
:root {
    --s-red:        #8B0000;
    --s-dark-red:   #5C0000;
    --s-black:      #0B0B0B;
    --s-gray:       #171717;
    --s-gray-soft:  #1F1F1F;
    --s-white:      #FFFFFF;
    --s-white-soft: #CCCCCC;
}

.stApp, [data-testid="stAppViewContainer"] {
    background-color: var(--s-black) !important;
}

h1, h2, h3, h4, h5, h6, p, span, li, label, 
div[data-testid="stMarkdownContainer"] *, 
[data-testid="stWidgetLabel"] * {
    color: var(--s-white) !important;
}

h1 {
    border-bottom: 2px solid var(--s-red) !important;
    padding-bottom: 8px !important;
    letter-spacing: .5px !important;
}

section[data-testid="stSidebar"] {
    background-color: var(--s-gray) !important;
    border-right: 1px solid var(--s-red) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--s-white) !important;
}

.samurai-card {
    background-color: var(--s-gray-soft) !important;
    border-left: 4px solid var(--s-red) !important;
    border-radius: 8px !important;
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.4) !important;
}
.samurai-card .titulo {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: var(--s-white-soft) !important;
    margin-bottom: 6px !important;
    font-weight: 600 !important;
}
.samurai-card .valor {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--s-white) !important;
}
.samurai-card .detalhe {
    font-size: 0.85rem !important;
    color: var(--s-white-soft) !important;
    margin-top: 6px !important;
}

.stButton > button, .stFormSubmitButton > button {
    background-color: var(--s-red) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-dark-red) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100%;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background-color: var(--s-dark-red) !important;
    border-color: var(--s-white) !important;
}

.stProgress > div > div > div > div {
    background-color: var(--s-red) !important;
}

.stTextInput input, .stNumberInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: var(--s-gray) !important;
    color: var(--s-white) !important;
    border: 1px solid var(--s-red) !important;
}

hr { border-color: var(--s-red) !important; opacity: .5 !important; }
.stAlert { 
    background-color: var(--s-gray-soft) !important; 
    color: var(--s-white) !important; 
    border: 1px solid var(--s-red) !important; 
}
.stAlert * { color: var(--s-white) !important; }

/* MOBILE OPTIMIZATIONS */
@media (max-width: 768px) {
    .block-container { padding: 1rem 0.5rem !important; }
    h1 { font-size: 1.8rem !important; }
    .samurai-card { padding: 12px !important; }
    .stButton>button { padding: 0.5rem !important; font-size: 0.9rem !important; }
    [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; }
}
</style>
"""

st.markdown(SAMURAI_CSS, unsafe_allow_html=True)

# --- CONFIGURAÇÃO PWA (APP NATIVO) ---
import base64
manifest_b64 = "eyJuYW1lIjogIlByb2pldG8gU2FtdXJhaSIsICJzaG9ydF9uYW1lIjogIlNhbXVyYWkiLCAic3RhcnRfdXJsIjogIi4iLCAiZGlzcGxheSI6ICJzdGFuZGFsb25lIiwgImJhY2tncm91bmRfY29sb3IiOiAiIzBCMEIwQiIsICJ0aGVtZV9jb2xvciI6ICIjOEIwMDAwIiwgImljb25zIjogW3sic3JjIjogImRhdGE6aW1hZ2UvcG5nO2Jhc2U2NCxpVkJPUncwS0dnb0FBQUFOU1VoRVVnQUFBTUFBQUFEQUNBWUFBQUJTM0d3SEFBQUFBWE5TUjBJQXJzNGM2UUFBQUFSblFVMUJBQUN4and2OFlRVUFBQUFKY0VoWmN3QUFEc01BQUE3REFjZHZxR1FBQUFESlNVUkJWSGhlN2RFeEFRQUFETU9nK1RmZG1jZ0J5RzRxQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFnTDhCd1NBQUFWUjhKNmtBQUFBQVNVVk9SSzVDWUlJPSIsICJzaXplcyI6ICIxOTJ4MTkyIiwgInR5cGUiOiAiaW1hZ2UvcG5nIn1dfQ=="
pwa_html = f"""
<link rel="manifest" href="data:application/json;base64,{manifest_b64}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Samurai">
<meta name="mobile-web-app-capable" content="yes">
"""
st.markdown(pwa_html, unsafe_allow_html=True)
# --------------------------------------



home = st.Page("ui/pages/00_Home.py", title="🏯 Dojo", default=True)
consistencia = st.Page("ui/pages/07_Consistencia.py", title="🎯 Consistência")
disciplina = st.Page("ui/pages/13_Disciplina.py", title="🛡️ Disciplina")
carreira = st.Page("ui/pages/14_Carreira.py", title="💼 Carreira")
financas = st.Page("ui/pages/15_Financas.py", title="💸 Finanças")
conquistas = st.Page("ui/pages/16_Conquistas.py", title="🏆 Conquistas")
corpo = st.Page("ui/pages/01_Corpo.py", title="💪 Corpo")
mente = st.Page("ui/pages/02_Mente.py", title="🧠 Mente")
informacao = st.Page("ui/pages/03_Informacao.py", title="📰 Informação")
patrimonio = st.Page("ui/pages/04_Patrimonio.py", title="💎 Patrimônio")
descanso = st.Page("ui/pages/05_Descanso.py", title="🌿 Descanso & Lazer")
autoconhecimento = st.Page("ui/pages/06_Autoconhecimento.py", title="🪞 Autoconhecimento")
religiao = st.Page("ui/pages/08_Religiao.py", title="🕊️ Religião")
alimentacao = st.Page("ui/pages/11_Alimentacao.py", title="🍏 Alimentação")
filosofia = st.Page("ui/pages/12_Filosofia.py", title="🏛️ Filosofia")

pg = st.navigation(
    {
        "⚔️ Comando": [home, consistencia, disciplina, carreira, financas, conquistas],
        "🏛️ Pilares": [corpo, mente, informacao, patrimonio, descanso, autoconhecimento, religiao, alimentacao, filosofia],
    }
)

from services.ai import get_api_key

with st.sidebar:
    st.divider()
    st.markdown("### ⚙️ IA Configuração")
    key_atual = get_api_key()
    
    if key_atual and key_atual != "COLE_SUA_CHAVE_AQUI":
        st.success("IA Conectada 🟢")
    else:
        st.warning("IA Desconectada 🔴")
        nova_chave = st.text_input("Cole sua API Key do Gemini:", type="password", placeholder="AIzaSy...")
        if st.button("Salvar e Ativar IA", use_container_width=True):
            if nova_chave.strip():
                config_file = BASE_DIR / "config.json"
                config_file.write_text(json.dumps({"gemini_api_key": nova_chave.strip()}, indent=4), encoding="utf-8")
                st.success("Chave salva com sucesso!")
                import time
                time.sleep(1)
                st.rerun()

pg.run()
