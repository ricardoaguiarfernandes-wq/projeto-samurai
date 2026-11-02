import streamlit as st
import sys
from pathlib import Path
from datetime import date
import random

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

st.title("🌿 Descanso & Lazer")
st.caption("Sugestões detalhadas com transporte, alimentação e custos (Base: Macaé).")

MACAÉ = [
    {"local": "Praia dos Cavaleiros", "transporte": "Local (ir de carro/uber).", "dica": "Orla e açaí.", "horario": "Final da tarde (16h-18h)", "custo": "R$ 30 (Uber + açaí)", "comida": "Quiosques da orla (açaí, sanduíches) ou restaurantes na Av. Atlântica."},
    {"local": "Lagoa de Imboassica", "transporte": "Local (ir de carro/uber).", "dica": "Caiaque e aves.", "horario": "Manhã (8h-11h)", "custo": "R$ 60 (Uber + caiaque)", "comida": "Levar piquenique ou comer em quiosques próximos à lagoa."},
    {"local": "Pico do Frade", "transporte": "Local (ir de carro/uber até a base).", "dica": "Trilha e vista.", "horario": "Início da manhã (7h-9h)", "custo": "R$ 40 (Uber)", "comida": "Não há opções no topo. Leve frutas, barras de cereal e 1,5L de água."},
    {"local": "Praia do Pecado", "transporte": "Local (ir de carro/uber).", "dica": "Reservado.", "horario": "Dia todo", "custo": "R$ 40 (Uber)", "comida": "Não tem quiosque. Leve lancheira com sanduíches e água."},
    {"local": "Parque da Lagoa", "transporte": "Local (ir de carro/uber).", "dica": "Natureza.", "horario": "Tarde", "custo": "Grátis (se for de bike) ou R$ 20 (Uber)", "comida": "Praça de alimentação no local e carrinhos de lanche."}
]

ARREDORES = [
    {"local": "Búzios", "transporte": "Ônibus 1001 (Macaé x Búzios) - ~2h30 de viagem.", "dica": "Rua das Pedras e Geribá.", "horario": "Dia inteiro", "custo": "Passagem 1001 + Almoço (R$ 150+)", "comida": "Restaurantes na Rua das Pedras (frutos do mar, bistrôs)."},
    {"local": "Cabo Frio", "transporte": "Ônibus 1001 (Macaé x Cabo Frio) - ~1h30 de viagem.", "dica": "Praia do Forte.", "horario": "Manhã", "custo": "Passagem 1001 + Almoço (R$ 80)", "comida": "Quiosques na Praia do Forte e restaurantes no centro."},
    {"local": "Arraial do Cabo", "transporte": "Ônibus 1001 (Macaé x Arraial) - ~2h de viagem.", "dica": "Pontal do Atalaia.", "horario": "Manhã (chegue cedo)", "custo": "Passagem 1001 + Almoço (R$ 100)", "comida": "Leve lancheira (opções no local são caras) ou coma no centro da cidade."},
    {"local": "Lumiar", "transporte": "Carro próprio é ideal (sem linha direta de ônibus da 1001).", "dica": "Cachoeiras e frio.", "horario": "Fim de semana", "custo": "Combustível + Pousada/Almoço (R$ 200+)", "comida": "Restaurantes de comida mineira (feijão tropeiro, truta)."},
    {"local": "Rio das Ostras", "transporte": "Ônibus 1001 (Macaé x Rio das Ostras) - ~40min.", "dica": "Costazul.", "horario": "Tarde", "custo": "Passagem 1001 + Lanche (R$ 40)", "comida": "Várias barracas de comida e restaurantes na orla da praia."}
]

random.seed(date.today().isocalendar()[1])
opcoes_macae = random.sample(MACAÉ, 3)
opcoes_arredores = random.sample(ARREDORES, 3)

st.header("Sugestões em Macaé (3 Opções)")
for i, opt in enumerate(opcoes_macae):
    with st.expander(f"📍 Opção {i+1}: {opt['local']}"):
        st.info(f"**💡 Dica:** {opt['dica']}")
        st.markdown(f"**🚌 Transporte:** {opt['transporte']}")
        st.markdown(f"**⏰ Melhor Horário:** {opt['horario']}")
        st.markdown(f"**🍽️ Onde Comer:** {opt['comida']}")
        st.markdown(f"**💰 Custo Estimado:** {opt['custo']}")

st.header("Arredores (3 Opções da Semana)")
for i, opt in enumerate(opcoes_arredores):
    with st.expander(f"🚗 Opção {i+1}: {opt['local']}"):
        st.info(f"**💡 Dica:** {opt['dica']}")
        st.markdown(f"**🚌 Transporte:** {opt['transporte']}")
        st.markdown(f"**⏰ Melhor Horário:** {opt['horario']}")
        st.markdown(f"**🍽️ Onde Comer:** {opt['comida']}")
        st.markdown(f"**💰 Custo Estimado:** {opt['custo']}")
