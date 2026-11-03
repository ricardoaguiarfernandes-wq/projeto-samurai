import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import query_all

st.title("🏆 Salão de Troféus")
st.caption("Suas conquistas na jornada Samurai.")

# Definição de todas as conquistas possíveis
TODAS_CONQUISTAS = {
    "primeiro_passo": {"nome": "Primeiro Passo", "desc": "Fez o primeiro check-in.", "icon": "👣"},
    "treino_dia": {"nome": "Sangue e Suor", "desc": "Completou o treino de hoje.", "icon": "💪"},
    "habito_completo": {"nome": "Disciplina", "desc": "Completou todos os hábitos de um dia.", "icon": "🔥"},
    "streak_7": {"nome": "Monge", "desc": "7 dias seguidos de domínio.", "icon": "🧘"},
    "financeiro": {"nome": "Investidor", "desc": "Registrou a primeira ação na carteira.", "icon": "📈"},
    "estudioso": {"nome": "Estudioso", "desc": "Respondeu 5 flashcards no Telegram.", "icon": "📚"}
}

# Buscar as que já foram ganhas
try:
    ganhas_db = query_all("SELECT id, earned_at FROM achievements")
    ganhas = {g['id']: g['earned_at'] for g in ganhas_db}
except Exception:
    ganhas = {}

# Exibe o Grid de Troféus
cols = st.columns(3)
for i, (key, data) in enumerate(TODAS_CONQUISTAS.items()):
    with cols[i % 3]:
        if key in ganhas:
            # Ganhou
            st.markdown(f"""
            <div class="samurai-card" style="text-align: center; border-left-color: #F9A825; background: linear-gradient(135deg, #2A1A00, #171717);">
                <div style="font-size: 3rem;">{data['icon']}</div>
                <div class="valor" style="font-size: 1.2rem; color: #F9A825;">{data['nome']}</div>
                <div class="detalhe">{data['desc']}</div>
                <div style="font-size: 0.7rem; color: #888; margin-top: 10px;">Ganhou em: {ganhas[key][:10]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Bloqueado
            st.markdown(f"""
            <div class="samurai-card" style="text-align: center; border-left-color: #333; opacity: 0.5;">
                <div style="font-size: 3rem; filter: grayscale(100%);">{data['icon']}</div>
                <div class="valor" style="font-size: 1.2rem;">???</div>
                <div class="detalhe">{data['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()
st.info("💡 Novas conquistas são desbloqueadas automaticamente conforme você usa o app e o Telegram. O Mentor vai te avisar!")
