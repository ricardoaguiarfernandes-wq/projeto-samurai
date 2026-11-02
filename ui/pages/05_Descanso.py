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
    {"local": "Praia dos Cavaleiros", "transporte": "Local (carro/uber).", "dica": "Orla e açaí.", "horario": "Final da tarde (16h-18h)", "custo": "R$ 30 (Uber + açaí)", "comida": "Quiosques (açaí, sanduíches) ou restaurantes na Av. Atlântica."},
    {"local": "Lagoa de Imboassica", "transporte": "Local (carro/uber).", "dica": "Caiaque e aves.", "horario": "Manhã (8h-11h)", "custo": "R$ 60 (Uber + caiaque)", "comida": "Piquenique ou quiosques próximos."},
    {"local": "Pico do Frade", "transporte": "Local (carro/uber até a base).", "dica": "Trilha e vista.", "horario": "Início da manhã (7h-9h)", "custo": "R$ 40 (Uber)", "comida": "Leve frutas, barras de cereal e 1,5L de água."},
    {"local": "Praia do Pecado", "transporte": "Local (carro/uber).", "dica": "Reservado.", "horario": "Dia todo", "custo": "R$ 40 (Uber)", "comida": "Sem quiosque. Leve lancheira com sanduíches."},
    {"local": "Parque da Lagoa", "transporte": "Local (carro/uber/bike).", "dica": "Natureza.", "horario": "Tarde", "custo": "Grátis (bike) ou R$ 20 (Uber)", "comida": "Praça de alimentação no local."}
]

ARREDORES = [
    {"local": "Búzios", "transporte": "Ônibus 1001 (Macaé x Búzios) - ~2h30.", "dica": "Rua das Pedras.", "horario": "Dia inteiro", "custo": "Passagem 1001 + Almoço (R$ 150+)", "comida": "Restaurantes na Rua das Pedras (frutos do mar)."},
    {"local": "Cabo Frio", "transporte": "Ônibus 1001 (Macaé x Cabo Frio) - ~1h30.", "dica": "Praia do Forte.", "horario": "Manhã", "custo": "Passagem 1001 + Almoço (R$ 80)", "comida": "Quiosques na Praia do Forte e restaurantes no centro."},
    {"local": "Arraial do Cabo", "transporte": "Ônibus 1001 (Macaé x Arraial) - ~2h.", "dica": "Pontal do Atalaia.", "horario": "Manhã (cedo)", "custo": "Passagem 1001 + Almoço (R$ 100)", "comida": "Leve lancheira ou coma no centro (opções no local são caras)."},
    {"local": "Lumiar", "transporte": "Carro próprio (sem linha direta 1001).", "dica": "Cachoeiras.", "horario": "Fim de semana", "custo": "Combustível + Almoço (R$ 200+)", "comida": "Restaurantes de comida mineira."},
    {"local": "Rio das Ostras", "transporte": "Ônibus 1001 (Macaé x Rio das Ostras) - ~40min.", "dica": "Costazul.", "horario": "Tarde", "custo": "Passagem 1001 + Lanche (R$ 40)", "comida": "Barracas de comida e restaurantes na orla."}
]

random.seed(date.today().isocalendar()[1])
st.header("Macaé (3 Opções)")
for i, opt in enumerate(random.sample(MACAÉ, 3)):
    with st.expander(f"📍 Opção {i+1}: {opt['local']}"):
        st.info(f'**💡 Dica:** {opt["dica"]}')
        st.markdown(f'**🚌 Transporte:** {opt["transporte"]}')
        st.markdown(f'**⏰ Melhor Horário:** {opt["horario"]}')
        st.markdown(f'**🍽️ Onde Comer:** {opt["comida"]}')
        st.markdown(f'**💰 Custo Estimado:** {opt["custo"]}')

st.header("Arredores (3 Opções)")
for i, opt in enumerate(random.sample(ARREDORES, 3)):
    with st.expander(f"🚗 Opção {i+1}: {opt['local']}"):
        st.info(f'**💡 Dica:** {opt["dica"]}')
        st.markdown(f'**🚌 Transporte:** {opt["transporte"]}')
        st.markdown(f'**⏰ Melhor Horário:** {opt["horario"]}')
        st.markdown(f'**🍽️ Onde Comer:** {opt["comida"]}')
        st.markdown(f'**💰 Custo Estimado:** {opt["custo"]}')
