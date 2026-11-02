import streamlit as st
import sys
from pathlib import Path
from datetime import date
import random

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

st.title("🌿 Descanso & Lazer")

MACAÉ = [
    {"local": "Praia dos Cavaleiros", "dica": "Orla e açaí.", "horario": "Final da tarde (16h-18h)", "custo": "R$ 20 (açaí)", "extra": "Estacionamento fácil na orla."},
    {"local": "Lagoa de Imboassica", "dica": "Caiaque e aves.", "horario": "Manhã (8h-11h)", "custo": "R$ 40 (caiaque)", "extra": "Leve repelente."},
    {"local": "Pico do Frade", "dica": "Trilha e vista.", "horario": "Início da manhã (7h-9h)", "custo": "Grátis", "extra": "Vá com tênis apropriado."},
    {"local": "Praia do Pecado", "dica": "Reservado.", "horario": "Dia todo", "custo": "Grátis", "extra": "Não tem quiosque, leve água."},
    {"local": "Parque da Lagoa", "dica": "Natureza.", "horario": "Tarde", "custo": "Grátis", "extra": "Boa opção para ler."}
]

ARREDORES = [
    {"local": "Búzios", "dica": "Rua das Pedras e Geribá.", "horario": "Dia inteiro", "custo": "R$ 100+", "extra": "Almoce na Rua das Pedras."},
    {"local": "Cabo Frio", "dica": "Praia do Forte.", "horario": "Manhã", "custo": "R$ 50", "extra": "Visite a Fortaleza."},
    {"local": "Arraial do Cabo", "dica": "Pontal do Atalaia.", "horario": "Manhã (chegue cedo)", "custo": "R$ 80", "extra": "Escadaria íngreme, vá de tênis."},
    {"local": "Lumiar", "dica": "Cachoeiras e frio.", "horario": "Fim de semana", "custo": "R$ 150+", "extra": "Leve casaco."},
    {"local": "Rio das Ostras", "dica": "Costazul.", "horario": "Tarde", "custo": "R$ 30", "extra": "Feira de artesanato."}
]

random.seed(date.today().isocalendar()[1])
opcoes_macae = random.sample(MACAÉ, 3)
opcoes_arredores = random.sample(ARREDORES, 3)

st.header("Macaé (3 Opções da Semana)")
for i, opt in enumerate(opcoes_macae):
    with st.expander(f"📍 Opção {i+1}: {opt['local']}"):
        st.info(f"**💡 Dica:** {opt['dica']}")
        st.markdown(f"**⏰ Melhor Horário:** {opt['horario']}")
        st.markdown(f"**💰 Custo Estimado:** {opt['custo']}")
        st.markdown(f"**📌 Extra:** {opt['extra']}")

st.header("Arredores (3 Opções da Semana)")
for i, opt in enumerate(opcoes_arredores):
    with st.expander(f"🚗 Opção {i+1}: {opt['local']}"):
        st.info(f"**💡 Dica:** {opt['dica']}")
        st.markdown(f"**⏰ Melhor Horário:** {opt['horario']}")
        st.markdown(f"**💰 Custo Estimado:** {opt['custo']}")
        st.markdown(f"**📌 Extra:** {opt['extra']}")
