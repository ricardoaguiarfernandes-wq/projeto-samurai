"""
melhoria.py — Correções no Patrimônio (Renda Fixa), Corpo (IA + Carga) e Descanso (Detalhado).
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

# ==============================================================================
# 1. CORPO (Com Carga, 3 Séries e IA de volta)
# ==============================================================================
CONTEUDO_CORPO = '''import streamlit as st
import sys
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date

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
    EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]
elif divisao == "PPL (Push/Pull/Legs)":
    dia = date.today().weekday()
    if dia in [0, 3]: EXERCICIOS = ["Flexão de Braço", "Desenvolvimento", "Tríceps"]
    elif dia in [1, 4]: EXERCICIOS = ["Barra Fixa", "Remada", "Rosca Direta"]
    else: EXERCICIOS = ["Agachamento", "Afundo", "Panturrilha"]
else:
    dia = date.today().weekday()
    if dia in [0, 3]: EXERCICIOS = ["Barra Fixa", "Flexão de Braço", "Remada"]
    else: EXERCICIOS = ["Agachamento", "Afundo", "Prancha (segundos)"]

st.subheader(f"🥋 Treino de Hoje: {divisao}")

# GERADOR DE IA
if st.button("🤖 Gerar Ficha de Treino com IA para Hoje", use_container_width=True):
    with st.spinner("O Treinador está analisando seu histórico e preparando a ficha..."):
        hist = query_all("SELECT log_date, exercise_name, reps FROM exercise_logs ORDER BY log_date DESC LIMIT 15")
        ctx = "".join([f"- {h['log_date']}: {h['exercise_name']} - {h['reps']} reps\\n" for h in hist])
        prompt = f"Atue como treinador de calistenia. Aluno ectomorfo. Divisão: {divisao}. Histórico:\\n{ctx}\\nSugira a ficha de hoje focando em progressão. Seja direto."
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)

st.markdown("### Registrar Execução")
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos = {}
    for ex in EXERCICIOS:
        val = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        
        # Usando 3 colunas para ficar mais limpo
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1: st.markdown(f"**{ex}**")
        with c2:
            if "Prancha" in ex:
                reps = st.number_input("Segundos", min_value=0, value=int(val["reps"]), key=f"r_{ex}")
                sets = 3 # Prancha fixo em 3 séries
                load = 0
            else:
                reps = st.number_input("Reps", min_value=0, value=int(val["reps"]), key=f"r_{ex}")
                sets = st.number_input("Séries", min_value=0, value=3, key=f"s_{ex}") # Padrão 3 séries
                load = st.number_input("Carga (kg)", min_value=0, value=0, key=f"c_{ex}") # Novo campo de carga
            novos[ex] = {"reps": reps, "sets": sets, "load": load}
            
    if st.form_submit_button("💾 Salvar Treino", use_container_width=True):
        for ex, v in novos.items():
            if v["reps"] > 0:
                # Como a tabela original não tem coluna 'load', salvamos a carga junto nos 'notes' para histórico
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
'''

# ==============================================================================
# 2. PATRIMÔNIO (Fix Renda Fixa e Simplificação da Taxa)
# ==============================================================================
CONTEUDO_PATRIMONIO = '''import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf
import pandas as pd

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()

# CORREÇÃO: Cria a tabela de Renda Fixa na hora, se não existir
execute("CREATE TABLE IF NOT EXISTS patrimony_fixed_income (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, rate TEXT)")

st.title("💎 Patrimônio")

tab_ia, tab_acoes, tab_rf = st.tabs(["🤖 Consultor IA", "📊 Ações/FIIs", "🏦 Renda Fixa"])

with tab_ia:
    st.header("Mentor Financeiro (CFP)")
    acoes_db = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE 'RF:%'")
    rf_db = query_all("SELECT * FROM patrimony_fixed_income")
    
    texto_acoes = "".join([f"- {a['ticker']}: {a['quantity']} cotas (PM: R$ {a['average_price']})\\n" for a in acoes_db])
    texto_rf = "".join([f"- {r['name']}: R$ {r['amount']} (Taxa: {r['rate']})\\n" for r in rf_db])
    
    with st.expander("Ver Carteira Atual (Base para a IA)"):
        st.markdown(f"**Ações:**\\n{texto_acoes if texto_acoes else 'Vazio'}")
        st.markdown(f"**Renda Fixa:**\\n{texto_rf if texto_rf else 'Vazio'}")
    
    with st.form("form_aporte"):
        aporte = st.number_input("Quanto você tem para investir este mês? (R$)", min_value=0.0, step=100.0)
        if st.form_submit_button("Gerar Plano de Alocação", use_container_width=True) and aporte > 0:
            with st.spinner("Analisando o mercado e sua carteira..."):
                prompt = f"""Atue como um Consultor Financeiro (CFP) sênior. 
Eu tenho R$ {aporte:.2f} para investir este mês.
Minha carteira atual:
AÇÕES/FIIs (NUNCA vender, são perenes):
{texto_acoes}
RENDA FIXA/RESERVA:
{texto_rf}

Sua missão:
1. Analise se as ações atuais estão em bom preço (descontadas). Se houver oportunidade, direcione parte do aporte para comprá-las.
2. Se não houver oportunidades claras, distribua o valor entre novas ações perenes, renda fixa (Tesouro Selic, CDBs) e reserva de oportunidade.
3. Detalhe exatamente onde alocar cada centavo (Ex: R$ 300 em PETR4, R$ 400 no Tesouro Selic, R$ 300 na reserva).
4. Justifique brevemente cada escolha."""
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Plano de Alocação do Mês</div><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)

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
        st.markdown(f"""<div class="samurai-card" style="padding: 10px;"><b>{a['ticker']}</b> - {a['quantity']} cotas @ R$ {a['average_price']:.2f}</div>""", unsafe_allow_html=True)

with tab_rf:
    st.subheader("Adicionar Renda Fixa")
    with st.form("f_rf"):
        n = st.text_input("Nome do Título (ex: CDB Banco X, Tesouro IPCA 2029)")
        v = st.number_input("Valor Investido (R$)", min_value=0.0, step=100.0)
        
        col1, col2 = st.columns(2)
        with col1:
            tipo_taxa = st.selectbox("Indexador", ["% do CDI", "% a.a.", "IPCA +"])
        with col2:
            valor_taxa = st.number_input("Valor da Taxa", min_value=0.0, step=0.1, help="Apenas o número. Ex: 110 para 110% do CDI ou 12.5 para 12,5% a.a.")
        
        taxa_final = f"{valor_taxa} {tipo_taxa}"
        
        if st.form_submit_button("Adicionar Renda Fixa"):
            execute("INSERT INTO patrimony_fixed_income (name, amount, rate) VALUES (?, ?, ?)", (n, v, taxa_final))
            st.success("Adicionado com sucesso!")
            st.rerun()
            
    st.divider()
    st.subheader("Seus Títulos")
    rf_db = query_all("SELECT * FROM patrimony_fixed_income")
    for rf in rf_db:
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;"><b>{rf['name']}</b> - R$ {rf['amount']:.2f} ({rf['rate']})</div>""", unsafe_allow_html=True)
'''

# ==============================================================================
# 3. DESCANSO (Detalhado com Transporte e Comida)
# ==============================================================================
CONTEUDO_DESCANSO = '''import streamlit as st
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
'''

def _run(cmd):
    subprocess.run(cmd, cwd=BASE, capture_output=True)

def aplicar():
    print("⚔️  APLICANDO MELHORIAS (Corpo, Patrimônio, Descanso)")
    arquivos = {
        "ui/pages/01_Corpo.py": CONTEUDO_CORPO,
        "ui/pages/04_Patrimonio.py": CONTEUDO_PATRIMONIO,
        "ui/pages/05_Descanso.py": CONTEUDO_DESCANSO
    }
    
    for cam, txt in arquivos.items():
        try:
            ast.parse(txt)
            (BASE / cam).write_text(txt, encoding="utf-8")
            print(f"[OK] {cam} atualizado.")
        except SyntaxError as e:
            print(f"[ERRO] Sintaxe em {cam}: {e}")
            sys.exit(1)

    print("\\n☁️ SINCRONIZANDO COM O GITHUB")
    _run(["git", "add", "-A"])
    _run(["git", "commit", "-m", "Fix: Tabela RF, Carga no treino, IA de volta, Descanso 1001"])
    _run(["git", "push", "origin", "main"])
    print("[OK] Push concluído.")

if __name__ == "__main__":
    aplicar()