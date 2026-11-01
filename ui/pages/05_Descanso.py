import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

st.title("🌿 Descanso & Lazer")
st.caption("Sugestões semanais para recarregar as energias.")

semana_ano = date.today().isocalendar()[1]

MACAÉ = [
    {
        "local": "Praia dos Cavaleiros",
        "dica": "Caminhada na orla e um açaí no fim da tarde.",
        "fazer": "Caminhar na orla, correr, jogar altinha ou apenas sentar para ler.",
        "levar": "Protetor solar, boné, toalha, canga e dinheiro para o açaí.",
        "comida": "Quiosques da orla (água de coco, açaí, sanduíches naturais).",
        "agua": "Leve uma garrafa de 1L, o sol da tarde é forte."
    },
    {
        "local": "Lagoa de Imboassica",
        "dica": "Passeio de caiaque ou pedalinho, ótimo para desacelerar.",
        "fazer": "Alugar caiaque/pedalinho, observar as aves, fazer um piquenique.",
        "levar": "Repelente, protetor solar, toalha e roupa confortável.",
        "comida": "Levar frutas, sanduíches e petiscos leves para um piquenique.",
        "agua": "Leve 1,5L de água, pois a atividade física na água desidrata."
    },
    {
        "local": "Pico do Frade",
        "dica": "Trilha leve com vista panorâmica da cidade. Leve água.",
        "fazer": "Fazer a trilha, tirar fotos no mirante, contemplar a vista.",
        "levar": "Tênis de caminhada, mochila leve, repelente e boné.",
        "comida": "Levar barras de cereal, frutas e castanhas para a trilha.",
        "agua": "Obrigatório levar ao menos 1,5L de água. A subida é íngreme."
    },
    {
        "local": "Praia do Pecado",
        "dica": "Lugar mais reservado para ler um livro e relaxar.",
        "fazer": "Leitura, descanso, meditação e banho de mar em águas calmas.",
        "levar": "Livro, protetor solar, canga, guarda-sol e fone de ouvido.",
        "comida": "Não há quiosques na areia. Leve um lanche prático (sanduíche).",
        "agua": "Leve 1L de água para se manter hidratado durante o dia."
    },
    {
        "local": "Parque Municipal da Lagoa",
        "dica": "Caminhada e contato com a natureza.",
        "fazer": "Caminhar pelas trilhas, andar de bicicleta, observar a fauna.",
        "levar": "Tênis confortável, repelente, boné e garrafa de água.",
        "comida": "O parque tem praça de alimentação e carrinhos de lanche.",
        "agua": "O parque tem bebedouros, mas é bom levar a sua garrafa."
    },
]

ARREDORES = [
    {
        "local": "Búzios - Rua das Pedras",
        "dica": "Almoço, caminhada e fim de tarde na praia de Geribá.",
        "fazer": "Passear pela Rua das Pedras, almoçar, ir à praia de Geribá, ver o pôr do sol.",
        "levar": "Roupas leves, sunga/maiô, protetor solar, cartão/carteira.",
        "comida": "A Rua das Pedras tem restaurantes excelentes (frutos do mar e bistrôs).",
        "agua": "O comércio é vasto, mas leve sua garrafa para a praia."
    },
    {
        "local": "Cabo Frio - Praia do Forte",
        "dica": "Visitar as dunas e a Fortaleza de São Mateus.",
        "fazer": "Conhecer a Fortaleza, caminhar nas areias brancas e subir as dunas.",
        "levar": "Sunga/maiô, protetor solar, óculos escuros e dinheiro para táxi.",
        "comida": "Quiosques na Praia do Forte e restaurantes no centro da cidade.",
        "agua": "Leve 1L, o sol e a areia refletem muito calor."
    },
    {
        "local": "Arraial do Cabo - Pontal do Atalaia",
        "dica": "Levar água e preparar para o visual mais bonito da região.",
        "fazer": "Descer as escadarias para as Prainhas, tirar fotos, fazer snorkel.",
        "levar": "Tênis (para as escadas), roupa de banho, snorkel, toalha.",
        "comida": "Leve lancheira com sanduíches e frutas, pois as opções no local são caras.",
        "agua": "MUITA ÁGUA. Leve pelo menos 2L, não há vendedores lá embaixo."
    },
    {
        "local": "Lumiar (Nova Friburgo)",
        "dica": "Pousada, cachoeiras e gastronomia mineira.",
        "fazer": "Visitar o Poço Feio, fazer trilhas e curtir o friozinho.",
        "levar": "Casaco, toalha, tênis de trilha e roupas para cachoeira.",
        "comida": "Restaurantes com comida mineira (feijão tropeiro, frango com quiabo).",
        "agua": "Leve água na mochila para as trilhas."
    },
    {
        "local": "Rio das Ostras - Costazul",
        "dica": "Feira de artesanato e passeio na lagoa.",
        "fazer": "Visitar a feira de artesanato, caminhar na orla e ver a lagoa.",
        "levar": "Roupa confortável, dinheiro para comprar artesanato e protetor.",
        "comida": "Há várias barracas de comida e restaurantes próximos à lagoa.",
        "agua": "Fácil acesso a comércio, leve apenas uma garrafa pequena."
    },
]

sugestao_macae = MACAÉ[semana_ano % len(MACAÉ)]
sugestao_arredores = ARREDORES[semana_ano % len(ARREDORES)]

# --- CARD MACAÉ ---
st.markdown(f"### Sugestão em Macaé")
with st.expander(f"📍 {sugestao_macae['local']}", expanded=True):
    st.info(f"**💡 Dica:** {sugestao_macae['dica']}")
    st.markdown(f"**🏃 O que fazer:**\n{sugestao_macae['fazer']}")
    st.markdown(f"**🎒 O que levar:**\n{sugestao_macae['levar']}")
    st.markdown(f"**🍽️ Comida:**\n{sugestao_macae['comida']}")
    st.markdown(f"**💧 Água:**\n{sugestao_macae['agua']}")

# --- CARD ARREDORES ---
st.markdown(f"### Sugestão nos Arredores")
with st.expander(f"🚗 {sugestao_arredores['local']}", expanded=True):
    st.info(f"**💡 Dica:** {sugestao_arredores['dica']}")
    st.markdown(f"**🏃 O que fazer:**\n{sugestao_arredores['fazer']}")
    st.markdown(f"**🎒 O que levar:**\n{sugestao_arredores['levar']}")
    st.markdown(f"**🍽️ Comida:**\n{sugestao_arredores['comida']}")
    st.markdown(f"**💧 Água:**\n{sugestao_arredores['agua']}")

st.divider()
st.info("💡 Lembre-se de usar o **Cartão Macaé** nos estabelecimentos parceiros da cidade.")
