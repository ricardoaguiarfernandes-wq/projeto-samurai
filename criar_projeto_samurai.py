"""
aplicar.py — Versão Segura e Definitiva (Sem aspas triplas internas).
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

# ==============================================================================
# 1. CORPO
# ==============================================================================
CONTEUDO_CORPO = """import streamlit as st
import sys
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date
import json
import re

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("💪 Corpo")
st.caption("Treino calistênico progressivo com carga e histórico.")
hoje = date.today().isoformat()

divisao = st.selectbox("Divisão de Treino:", ["Full Body", "PPL (Push/Pull/Legs)", "Upper/Lower"])

if divisao == "Full Body":
    EXERCICIOS_PADRAO = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]
elif divisao == "PPL (Push/Pull/Legs)":
    dia = date.today().weekday()
    if dia in [0, 3]: EXERCICIOS_PADRAO = ["Flexão de Braço", "Desenvolvimento", "Tríceps"]
    elif dia in [1, 4]: EXERCICIOS_PADRAO = ["Barra Fixa", "Remada", "Rosca Direta"]
    else: EXERCICIOS_PADRAO = ["Agachamento", "Afundo", "Panturrilha"]
else:
    dia = date.today().weekday()
    if dia in [0, 3]: EXERCICIOS_PADRAO = ["Barra Fixa", "Flexão de Braço", "Remada"]
    else: EXERCICIOS_PADRAO = ["Agachamento", "Afundo", "Prancha (segundos)"]

st.subheader(f"🥋 Treino de Hoje: {divisao}")

if st.button("🤖 Gerar Ficha de Treino com IA para Hoje", use_container_width=True):
    with st.spinner("O Treinador está analisando e preparando a ficha..."):
        hist = query_all("SELECT log_date, exercise_name, reps FROM exercise_logs ORDER BY log_date DESC LIMIT 15")
        ctx = "".join([f"- {h['log_date']}: {h['exercise_name']} - {h['reps']} reps\\n" for h in hist])

        prompt = f"Atue como treinador de calistenia. Aluno ectomorfo. Divisão: {divisao}. Histórico:\\n{ctx}\\n\\nSugira a ficha de hoje focando em progressão. Seja direto e motivador.\\nIMPORTANTE: No final da sua resposta, adicione um bloco de código JSON contendo APENAS os nomes dos exercícios sugeridos.\\nExemplo:\\n```json\\n{{\\"exercicios\\": [\\"Flexão Declinada\\", \\"Pistol Squat\\", \\"Barra Pronada\\", \\"Leg Raises\\"]}}\\n```\\nNão escreva nada após o bloco JSON."

        resposta_ia = ask_gemini(prompt)

        try:
            match = re.search(r'```json\\s*(.*?)\\s*```', resposta_ia, re.DOTALL)
            if not match:
                match = re.search(r'\\{.*\\}', resposta_ia, re.DOTALL)

            if match:
                json_str = match.group(1) if '```' in match.group(0) else match.group(0)
                data = json.loads(json_str)
                if "exercicios" in data and len(data["exercicios"]) > 0:
                    st.session_state["exercicios_ia"] = data["exercicios"]
                    texto_limpo = resposta_ia.replace(match.group(0), "").strip()
                    st.session_state["texto_ia"] = texto_limpo
                    st.success("Ficha gerada! Os exercícios foram atualizados no formulário abaixo.")
            else:
                st.session_state["texto_ia"] = resposta_ia
        except Exception as e:
            st.session_state["texto_ia"] = resposta_ia
            st.warning("A IA gerou a ficha, mas não foi possível atualizar o formulário automaticamente.")

if st.session_state.get("texto_ia"):
    st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div style="white-space: pre-wrap;">{st.session_state["texto_ia"]}</div></div>', unsafe_allow_html=True)

    if st.button("🔄 Limpar Ficha da IA e voltar ao padrão"):
        if "exercicios_ia" in st.session_state: del st.session_state["exercicios_ia"]
        if "texto_ia" in st.session_state: del st.session_state["texto_ia"]
        st.rerun()

st.markdown("### Registrar Execução")
EXERCICIOS_ATUAIS = st.session_state.get("exercicios_ia", EXERCICIOS_PADRAO)
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos = {}
    for ex in EXERCICIOS_ATUAIS:
        val = treinos_hoje.get(ex, {"reps": 0, "sets": 0})

        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: st.markdown(f"**{ex}**")
        with c2:
            if "Prancha" in ex or "Segundos" in ex or "Isometria" in ex:
                reps = st.number_input("Segundos", min_value=0, value=int(val["reps"]), key=f"r_{ex}")
                sets = 3
                load = 0
            else:
                reps = st.number_input("Reps", min_value=0, value=int(val["reps"]), key=f"r_{ex}")
                sets = st.number_input("Séries", min_value=0, value=3, key=f"s_{ex}")
                load = st.number_input("Carga (kg)", min_value=0, value=0, key=f"c_{ex}")
            novos[ex] = {"reps": reps, "sets": sets, "load": load}

    if st.form_submit_button("💾 Salvar Treino", use_container_width=True):
        for ex, v in novos.items():
            if v["reps"] > 0:
                execute("INSERT INTO exercise_logs (log_date, exercise_name, reps, sets, notes) VALUES (?, ?, ?, ?, ?) ON CONFLICT(log_date, exercise_name) DO UPDATE SET reps=excluded.reps, sets=excluded.sets, notes=excluded.notes", (hoje, ex, v["reps"], v["sets"], f"Carga: {v['load']}kg"))
        st.rerun()

st.divider()
st.subheader("📈 Ficha do Aluno (Últimos 14 dias)")
hist = query_all("SELECT log_date, exercise_name, reps FROM exercise_logs ORDER BY log_date DESC LIMIT 50")
if hist:
    df = pd.DataFrame(hist)
    df_agrupado = df.groupby(['log_date', 'exercise_name'])['reps'].sum().reset_index()
    fig = px.line(df_agrupado, x='log_date', y='reps', color='exercise_name', markers=True, color_discrete_sequence=['#8B0000', '#F9A825', '#4CAF50', '#2196F3'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#F2F2F2'))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Sem histórico.")
"""

# ==============================================================================
# 2. PATRIMÔNIO
# ==============================================================================
CONTEUDO_PATRIMONIO = """import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()

execute("CREATE TABLE IF NOT EXISTS patrimony_fixed_income (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, rate TEXT)")

st.title("💎 Patrimônio")
tab_ia, tab_acoes, tab_rf = st.tabs(["🤖 Consultor IA", "📊 Ações/FIIs", "🏦 Renda Fixa"])

with tab_ia:
    st.header("Mentor Financeiro (CFP)")
    acoes_db = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE 'RF:%'")
    rf_db = query_all("SELECT * FROM patrimony_fixed_income")

    texto_acoes = "".join([f"- {a['ticker']}: {a['quantity']} cotas (PM: R$ {a['average_price']})\\n" for a in acoes_db])
    texto_rf = "".join([f"- {r['name']}: R$ {r['amount']} (Taxa: {r['rate']})\\n" for r in rf_db])

    with st.expander("Ver Carteira Atual"):
        st.markdown(f'**Ações:**\\n{texto_acoes if texto_acoes else "Vazio"}')
        st.markdown(f'**Renda Fixa:**\\n{texto_rf if texto_rf else "Vazio"}')

    with st.form("form_aporte"):
        aporte = st.number_input("Quanto você tem para investir este mês? (R$)", min_value=0.0, step=100.0)
        if st.form_submit_button("Gerar Plano de Alocação", use_container_width=True) and aporte > 0:
            with st.spinner("Analisando o mercado..."):
                prompt = f"Atue como um Consultor Financeiro (CFP) sênior. \\nTenho R$ {aporte:.2f} para investir.\\nAÇÕES (NUNCA vender):\\n{texto_acoes}\\nRENDA FIXA: \\n{texto_rf}\\n\\nSua missão: Analise se as ações atuais estão descontadas e direcione parte do aporte. Se não, distribua entre novas ações perenes, renda fixa e reserva. Detalhe exatamente onde alocar cada centavo (Ex: R$ 300 em PETR4, R$ 400 no Tesouro Selic) e justifique."
                st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Plano de Alocação</div><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>', unsafe_allow_html=True)

with tab_acoes:
    carteira = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE 'RF:%'")
    with st.expander("➕ Adicionar Ação"):
        with st.form("f_a"):
            t = st.text_input("Ticker (ex: PETR4.SA)").upper()
            q = st.number_input("Qtd", min_value=1, value=100)
            p = st.number_input("Preço Médio", min_value=0.01, value=30.00)
            if st.form_submit_button("Salvar"):
                execute("INSERT INTO portfolio (ticker, quantity, average_price) VALUES (?, ?, ?) ON CONFLICT(ticker) DO UPDATE SET quantity=excluded.quantity, average_price=excluded.average_price", (t, q, p))
                st.rerun()
    for a in carteira:
        st.markdown(f'<div class="samurai-card" style="padding: 10px;"><b>{a["ticker"]}</b> - {a["quantity"]} cotas @ R$ {a["average_price"]:.2f}</div>', unsafe_allow_html=True)

with tab_rf:
    st.subheader("Adicionar Renda Fixa")
    with st.form("f_rf"):
        n = st.text_input("Nome (ex: CDB Banco X, Tesouro IPCA 2029)")
        v = st.number_input("Valor Investido (R$)", min_value=0.0, step=100.0)

        col1, col2 = st.columns(2)
        with col1: tipo_taxa = st.selectbox("Indexador", ["% do CDI", "% a.a.", "IPCA +"])
        with col2: valor_taxa = st.number_input("Valor da Taxa", min_value=0.0, step=0.1, help="Apenas o número. Ex: 110 para 110% do CDI.")

        taxa_final = f"{valor_taxa} {tipo_taxa}"
        if st.form_submit_button("Adicionar"):
            execute("INSERT INTO patrimony_fixed_income (name, amount, rate) VALUES (?, ?, ?)", (n, v, taxa_final))
            st.rerun()

    st.divider()
    rf_db = query_all("SELECT * FROM patrimony_fixed_income")
    for rf in rf_db:
        st.markdown(f'<div class="samurai-card" style="border-left-color: #2196F3;"><b>{rf["name"]}</b> - R$ {rf["amount"]:.2f} ({rf["rate"]})</div>', unsafe_allow_html=True)
"""

# ==============================================================================
# 3. DESCANSO
# ==============================================================================
CONTEUDO_DESCANSO = """import streamlit as st
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
"""

# ==============================================================================
# 4. ALIMENTAÇÃO
# ==============================================================================
CONTEUDO_ALIMENTACAO = """import streamlit as st
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
    st.markdown(f'<div class="samurai-card" style="padding: 15px; border-left-color: #F9A825;"><b>🛒 Ingredientes:</b><br>{det["ing"]}<br><br><b>👨‍🍳 Modo de Preparo:</b><br>{det["prep"]}<br><br><b style="color: #4CAF50;">💪 Por que é bom para Ectomorfo?</b><br>{det["porque"]}</div>', unsafe_allow_html=True)

st.divider()
st.subheader("🤖 Chef Samurai (Criar Nova Receita)")
with st.form("form_receita"):
    ref = st.selectbox("Refeição:", list(refeicoes.keys()))
    ing = st.text_input("O que tem na geladeira?")
    if st.form_submit_button("Gerar Receita com IA", use_container_width=True):
        with st.spinner("Criando..."):
            prompt = f"Crie uma receita hipercalórica para {ref}. Ingredientes: {ing}. Formate com Ingredientes, Preparo e Por que é bom para ectomorfos."
            st.markdown(f'<div class="samurai-card">{ask_gemini(prompt)}</div>', unsafe_allow_html=True)
"""

def _run(cmd):
    subprocess.run(cmd, cwd=BASE, capture_output=True)

def aplicar():
    print("=" * 60)
    print("⚔️  APLICANDO PACOTE COMPLETO DE MELHORIAS")
    print("=" * 60)
    
    arquivos = {
        "ui/pages/01_Corpo.py": CONTEUDO_CORPO,
        "ui/pages/04_Patrimonio.py": CONTEUDO_PATRIMONIO,
        "ui/pages/05_Descanso.py": CONTEUDO_DESCANSO,
        "ui/pages/11_Alimentacao.py": CONTEUDO_ALIMENTACAO
    }
    
    for cam, txt in arquivos.items():
        try:
            ast.parse(txt)
            (BASE / cam).write_text(txt, encoding="utf-8")
            print(f"[OK] {cam} atualizado.")
        except SyntaxError as e:
            print(f"[ERRO] Sintaxe em {cam}: {e}")
            sys.exit(1)

    print("\n☁️  SINCRONIZANDO COM O GITHUB")
    _run(["git", "add", "-A"])
    _run(["git", "commit", "-m", "Fix: Correcao definitiva de sintaxe nas aspas"])
    _run(["git", "push", "origin", "main"])
    print("[OK] Push concluído. O Streamlit vai atualizar em instantes.")
    print("=" * 60)

if __name__ == "__main__":
    aplicar()