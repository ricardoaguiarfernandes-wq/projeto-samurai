import streamlit as st
import sys
from pathlib import Path
from datetime import date
import random

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

st.title("🌿 Descanso & Lazer")
st.caption("Sugestões semanais para recarregar as energias.")

MACAÉ = [
    {"local": "Praia dos Cavaleiros", "dica": "Caminhada na orla e açaí.", "fazer": "Caminhar, correr, ler.", "levar": "Protetor, boné, toalha."},
    {"local": "Lagoa de Imboassica", "dica": "Caiaque e aves.", "fazer": "Pedalinho, piquenique.", "levar": "Repelente, toalha."},
    {"local": "Pico do Frade", "dica": "Trilha e vista.", "fazer": "Trilha leve, fotos.", "levar": "Tênis, mochila."},
    {"local": "Praia do Pecado", "dica": "Lugar reservado.", "fazer": "Leitura, mar calmo.", "levar": "Livro, guarda-sol."},
    {"local": "Parque da Lagoa", "dica": "Natureza.", "fazer": "Bicicleta, trilhas.", "levar": "Tênis, água."}
]

ARREDORES = [
    {"local": "Búzios", "dica": "Rua das Pedras e Geribá.", "fazer": "Passear, almoçar.", "levar": "Sunga, cartão."},
    {"local": "Cabo Frio", "dica": "Praia do Forte e Dunas.", "fazer": "Visitar fortaleza.", "levar": "Protetor, dinheiro."},
    {"local": "Arraial do Cabo", "dica": "Pontal do Atalaia.", "fazer": "Descer escadas, snorkel.", "levar": "Tênis, snorkel."},
    {"local": "Lumiar", "dica": "Cachoeiras e frio.", "fazer": "Poço Feio, trilhas.", "levar": "Casaco, toalha."},
    {"local": "Rio das Ostras", "dica": "Costazul e artesanato.", "fazer": "Feira, caminhada.", "levar": "Roupa leve."}
]

# Sorteia 3 opções (baseado na semana para não mudar a cada refresh)
random.seed(date.today().isocalendar()[1])
opcoes_macae = random.sample(MACAÉ, 3)
opcoes_arredores = random.sample(ARREDORES, 3)

st.header("Sugestões em Macaé (3 Opções)")
for i, opt in enumerate(opcoes_macae):
    with st.expander(f"📍 Opção {i+1}: {opt['local']}"):
        st.info(f"**💡 Dica:** {opt['dica']}")
        st.markdown(f"**🏃 Fazer:** {opt['fazer']} | **🎒 Levar:** {opt['levar']}")

st.header("Sugestões nos Arredores (3 Opções)")
for i, opt in enumerate(opcoes_arredores):
    with st.expander(f"🚗 Opção {i+1}: {opt['local']}"):
        st.info(f"**💡 Dica:** {opt['dica']}")
        st.markdown(f"**🏃 Fazer:** {opt['fazer']} | **🎒 Levar:** {opt['levar']}")
