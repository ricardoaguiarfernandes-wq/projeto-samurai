import streamlit as st
import sys
from pathlib import Path
import time

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db
from services.ai import ask_gemini

init_db()

st.title("🍏 Alimentação")
st.caption("Nutrição focada em hipertrofia para Ectomorfos (1,86m, 70kg).")

st.markdown("""
<div class="samurai-card" style="border-left-color: #F9A825;">
    <div class="titulo">Estratégia Nutricional</div>
    <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6;">
        Seu foco é o <b>superávit calórico</b> (comer mais calorias do que gasta). Como ectomorfo, você precisa de refeições frequentes (a cada 3h), ricas em carboidratos complexos, proteínas de alto valor biológico e gorduras boas.
    </div>
</div>
""", unsafe_allow_html=True)

# --- REFEIÇÕES ---
refeicoes = {
    "☕ Café da Manhã (07:00)": {
        "prato": "Panqueca de Aveia e Banana com Pasta de Amendoim",
        "ingredientes": "2 ovos inteiros, 50g de aveia em flocos, 1 banana amassada, 1 colher de sopa de pasta de amendoim, canela a gosto.",
        "receita": "Bata os ovos, a aveia e a banana no liquidificador ou misture bem até formar uma massa. Despeje em uma frigideira antiaderente e doure dos dois lados. Sirva com a pasta de amendoim por cima e polvilhe canela."
    },
    "🍛 Almoço (12:00)": {
        "prato": "Frango Grelhado com Arroz, Feijão e Legumes",
        "ingredientes": "150g de peito de frango, 4 colheres de arroz branco, 1 concha de feijão, brócolis e cenoura, azeite de oliva.",
        "receita": "Grelhe o frango temperado com alho e sal. Cozinhe o arroz e o feijão. Refogue os legumes no azeite. Monte o prato caprichando nas porções para garantir as calorias."
    },
    "🥪 Café da Tarde / Pré-Treino (16:00)": {
        "prato": "Sanduíche Proteico com Vitamina de Frutas",
        "ingredientes": "2 fatias de pão integral, 100g de frango desfiado ou atum, queijo cottage, 1 copo de leite, 1 banana, 30g de aveia, 1 colher de mel.",
        "receita": "Monte o sanduíche com o frango e o queijo. Bata no liquidificador o leite, a banana, a aveia e o mel para fazer a vitamina. É a refeição perfeita para dar energia antes do treino."
    },
    "🍲 Jantar (20:00)": {
        "prato": "Macarrão Integral com Carne Moída e Molho de Tomate",
        "ingredientes": "150g de macarrão integral, 150g de carne moída (patinho), molho de tomate caseiro, cebola, alho, queijo ralado.",
        "receita": "Cozinhe o macarrão. Refogue a cebola e o alho, adicione a carne moída até dourar, coloque o molho de tomate e deixe apurar. Misture ao macarrão e finalize com queijo ralado."
    }
}

for nome, info in refeicoes.items():
    st.markdown(f"### {nome}")
    with st.expander(f"👨‍🍳 Receita: {info['prato']}", expanded=False):
        st.markdown(f"**🛒 Ingredientes:**\n{info['ingredientes']}")
        st.markdown(f"**🍳 Modo de Preparo:**\n{info['receita']}")

# --- GERADOR DE RECEITAS IA ---
st.divider()
st.subheader("🤖 Chef Samurai (Gerador de Receitas)")

with st.form("form_receita"):
    st.write("Está sem criatividade? Peça uma receita focada no seu perfil.")
    opcoes_refeicao = ["Café da Manhã", "Almoço", "Café da Tarde", "Jantar"]
    refeicao_escolhida = st.selectbox("Qual refeição você quer preparar?", opcoes_refeicao)
    ingredientes_user = st.text_input("O que você tem na geladeira? (Opcional)", placeholder="Ex: ovos, arroz, frango...")
    
    submit_receita = st.form_submit_button("🪄 Gerar Receita com IA", use_container_width=True)
    
    if submit_receita:
        with st.spinner("O Chef IA está criando a receita..."):
            prompt = f"""Atue como um Chef de Cozinha e Nutricionista esportivo. 
            Estou preparando o {refeicao_escolhida}. Sou Ectomorfo (1,86m, 70kg) e preciso de refeições hipercalóricas, ricas em proteína e carboidratos complexos.
            Ingredientes que tenho em casa: {ingredientes_user if ingredientes_user else "Não especificado, use ingredientes comuns"}.
            
            Crie uma receita deliciosa. Formate a resposta em Markdown, separando em 'Ingredientes' e 'Modo de Preparo'. Seja direto e prático."""
            
            receita_ia = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000;">
                <div class="titulo">Receita do Chef</div>
                <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{receita_ia}</div>
            </div>""", unsafe_allow_html=True)
