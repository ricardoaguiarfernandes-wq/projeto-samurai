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
st.caption("Nutrição hipercalórica para Ectomorfos.")

tipo_refeicao = st.radio("Destino da refeição:", ["Para agora (Na hora)", "Para marmita (Dura +3 dias)"], horizontal=True)

refeicoes = {
    "☕ Café da Manhã": [
        {"prato": "Panqueca Proteica", "ing": "2 ovos, 50g aveia, 1 banana, 1 colher pasta de amendoim.", "prep": "Amasse a banana, misture os ovos e a aveia. Despeje em frigideira antiaderente em fogo baixo. Doure dos dois lados. Sirva com a pasta de amendoim.", "porque": "Aveia e banana dão carboidratos de digestão lenta, ovos dão proteína e a pasta de amendoim adiciona gordura boa."},
        {"prato": "Ovos Mexidos com Pão", "ing": "3 ovos, 2 fatias pão integral, 30g queijo.", "prep": "Bata os ovos com sal. Em fogo baixo, mexa lentamente até ficarem cremosos. Sirva sobre o pão tostado com o queijo derretido.", "porque": "Proteína de alto valor biológico pela manhã."},
        {"prato": "Vitamina Hipercalórica", "ing": "300ml leite, 1 banana, 30g aveia, 1 scoop whey, 1 colher pasta de amendoim.", "prep": "Bata todos os ingredientes no liquidificador até ficar homogêneo.", "porque": "Fácil de consumir e altíssima densidade calórica."}
    ],
    "🍛 Almoço": [
        {"prato": "Frango com Arroz e Feijão", "ing": "150g frango, 4 colheres arroz, 1 concha feijão, salada.", "prep": "Tempere o frango com alho e sal, grelhe. Cozinhe o arroz e o feijão. Monte o prato.", "porque": "A combinação arroz + feijão forma uma proteína completa."},
        {"prato": "Macarrão com Carne Moída", "ing": "150g macarrão, 150g patinho moído, molho de tomate.", "prep": "Cozinhe o macarrão. Refogue a carne, adicione o molho e deixe apurar. Misture.", "porque": "Carboidratos e proteínas para repor o glicogênio pós-treino."},
        {"prato": "Tilápia com Purê", "ing": "150g tilápia, 2 batatas, legumes.", "prep": "Asse a tilápia com limão. Cozinhe as batatas, amasse e adicione leite. Sirva com legumes.", "porque": "Peixe tem digestão leve, ideal se for treinar logo depois."}
    ],
    "🥪 Café da Tarde": [
        {"prato": "Sanduíche de Atum", "ing": "2 fatias pão, 1 lata atum, maionese light.", "prep": "Misture o atum com a maionese e recheie o pão.", "porque": "Prático e rico em proteína."},
        {"prato": "Iogurte com Granola", "ing": "200g iogurte natural, granola, mel.", "prep": "Misture tudo em uma tigela.", "porque": "Probióticos e carboidratos rápidos."},
        {"prato": "Tapioca com Ovo", "ing": "Goma de tapioca, 2 ovos, queijo.", "prep": "Faça a tapioca na frigideira, recheie com ovos mexidos e queijo.", "porque": "Carboidratos rápidos para dar energia antes do treino."}
    ],
    "🍲 Jantar": [
        {"prato": "Omelete de Frango", "ing": "3 ovos, frango desfiado, queijo.", "prep": "Bata os ovos, adicione o frango e o queijo. Cozinhe em fogo baixo.", "porque": "Proteína leve à noite."},
        {"prato": "Sopa de Legumes", "ing": "Carne, batata, cenoura, macarrão.", "prep": "Cozinhe tudo na panela de pressão por 20 min.", "porque": "Hidratante e nutritivo."},
        {"prato": "Wrap de Frango", "ing": "Tortilha, frango, salada, molho.", "prep": "Aqueça a tortilha e recheie.", "porque": "Refeição completa e rápida."}
    ]
}

for nome, opcoes in refeicoes.items():
    st.subheader(nome)
    escolha = st.selectbox(f"Prato para {nome}:", [o["prato"] for o in opcoes], key=f"s_{nome}")
    det = next(o for o in opcoes if o["prato"] == escolha)
    
    prep_texto = det["prep"]
    if "marmita" in tipo_refeicao.lower():
        prep_texto += "<br><br><b style='color: #2196F3;'>🍱 PARA MARMITA:</b> Espere esfriar e guarde em potes herméticos na geladeira. Dura até 3 dias. Ao reaquecer, adicione 1 colher de água para não secar."
    else:
        prep_texto += "<br><br><b style='color: #4CAF50;'>🍽️ PARA AGORA:</b> Sirva imediatamente enquanto estiver quente e no ponto."

    st.markdown(f'<div class="samurai-card" style="padding: 15px; border-left-color: #F9A825;"><b>🛒 Ingredientes:</b><br>{det["ing"]}<br><br><b>👨‍🍳 Modo de Preparo:</b><br>{prep_texto}<br><br><b style="color: #4CAF50;">💪 Por que é bom para Ectomorfo?</b><br>{det["porque"]}</div>', unsafe_allow_html=True)

st.divider()
st.subheader("🤖 Chef Samurai (Criar Nova Receita)")
with st.form("form_receita"):
    ref = st.selectbox("Refeição:", list(refeicoes.keys()))
    ing = st.text_input("O que tem na geladeira?")
    if st.form_submit_button("Gerar Receita com IA", use_container_width=True):
        with st.spinner("Criando..."):
            prompt = f"Crie uma receita hipercalórica para {ref}. O destino é: {tipo_refeicao}. Ingredientes: {ing}. Se for marmita, foque em ingredientes que aguentam dias na geladeira e expliquem como armazenar. Formate com Ingredientes, Preparo e Por que é bom para ectomorfos."
            st.markdown(f'<div class="samurai-card">{ask_gemini(prompt)}</div>', unsafe_allow_html=True)
