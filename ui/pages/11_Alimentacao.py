import streamlit as st
import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("🍏 Alimentação")
st.caption("Nutrição para Ectomorfos.")

refeicoes = {
    "☕ Café da Manhã": [
        {"prato": "Panqueca de Aveia", "ing": "2 ovos, 50g aveia, banana, pasta de amendoim.", "prep": "Bata tudo e doure na frigideira."},
        {"prato": "Ovos Mexidos com Pão Integral", "ing": "3 ovos, 2 fatias pão, queijo.", "prep": "Mexa os ovos e sirva com queijo."},
        {"prato": "Vitamina Hipercalórica", "ing": "Leite, banana, aveia, whey, pasta de amendoim.", "prep": "Bata tudo no liquidificador."}
    ],
    "🍛 Almoço": [
        {"prato": "Frango com Arroz e Feijão", "ing": "150g frango, arroz, feijão, salada.", "prep": "Grelhe o frango e monte o prato."},
        {"prato": "Carne Moída com Macarrão", "ing": "150g patinho, macarrão, molho.", "prep": "Refogue a carne e misture ao macarrão."},
        {"prato": "Tilápia com Purê e Legumes", "ing": "150g tilápia, batata, cenoura.", "prep": "Asse o peixe e faça o purê."}
    ],
    "🥪 Café da Tarde": [
        {"prato": "Sanduíche de Atum", "ing": "Pão integral, atum, maionese light.", "prep": "Misture e monte o sanduíche."},
        {"prato": "Iogurte com Granola e Frutas", "ing": "Iogurte natural, granola, maçã.", "prep": "Misture tudo em uma tigela."},
        {"prato": "Tapioca com Ovo e Queijo", "ing": "Goma de tapioca, 2 ovos, queijo.", "prep": "Faça a tapioca e recheie."}
    ],
    "🍲 Jantar": [
        {"prato": "Omelete de Frango", "ing": "3 ovos, frango desfiado, queijo.", "prep": "Bata os ovos e cozinhe com o frango."},
        {"prato": "Sopa de Legumes com Carne", "ing": "Carne, batata, cenoura, macarrão.", "prep": "Cozinhe tudo na panela de pressão."},
        {"prato": "Wrap de Frango", "ing": "Tortilha, frango, salada, molho.", "prep": "Enrole o frango na tortilha."}
    ]
}

for nome, opcoes in refeicoes.items():
    st.subheader(nome)
    escolha = st.selectbox(f"Escolha o prato para {nome}:", [o["prato"] for o in opcoes], key=f"sel_{nome}")
    detalhe = next(o for o in opcoes if o["prato"] == escolha)
    st.markdown(f"""<div class="samurai-card" style="padding: 10px;"><b>Ingredientes:</b> {detalhe['ing']}<br><b>Modo de Preparo:</b> {detalhe['prep']}</div>""", unsafe_allow_html=True)

st.divider()
st.subheader("🤖 Chef Samurai (Criar Nova Receita)")
with st.form("form_receita"):
    ref_escolhida = st.selectbox("Qual refeição?", list(refeicoes.keys()))
    ingredientes = st.text_input("O que tem na geladeira?")
    if st.form_submit_button("Gerar Receita com IA", use_container_width=True):
        with st.spinner("Criando..."):
            prompt = f"Crie uma receita hipercalórica para {ref_escolhida}. Ingredientes: {ingredientes}. Formate em Ingredientes e Modo de Preparo."
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;">{ask_gemini(prompt)}</div>""", unsafe_allow_html=True)
