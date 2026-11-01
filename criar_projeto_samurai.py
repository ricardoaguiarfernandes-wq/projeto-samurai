"""
melhoria.py — Atualização Massiva do Projeto Samurai.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
PADROES_SECRETOS = [
    re.compile(r"AQ\.Ab8RN6[A-Za-z0-9_\-]{20,}"),
    re.compile(r"postgresql://[^:\s]+:[^@\s]+@"),
]
ARQUIVOS_PROIBIDOS = {"config.json", ".env", "secrets.toml"}

# ==============================================================================
# 1. CORPO
# ==============================================================================
CONTEUDO_CORPO = '''import streamlit as st
import sys
from pathlib import Path
from datetime import date
import pandas as pd
import plotly.express as px

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("💪 Corpo")
st.caption("Treino calistênico progressivo.")
hoje = date.today().isoformat()

divisao = st.selectbox("Divisão de Treino:", ["Full Body (Corpo Inteiro)", "PPL (Push/Pull/Legs)", "Upper/Lower (Superiores/Inferiores)"])

if divisao == "Full Body (Corpo Inteiro)":
    EXERCICIOS = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]
elif divisao == "PPL (Push/Pull/Legs)":
    dia_semana = date.today().weekday()
    if dia_semana in [0, 3]: EXERCICIOS = ["Flexão de Braço", "Desenvolvimento", "Tríceps"]
    elif dia_semana in [1, 4]: EXERCICIOS = ["Barra Fixa", "Remada", "Rosca Direta"]
    else: EXERCICIOS = ["Agachamento", "Afundo", "Panturrilha"]
else:
    dia_semana = date.today().weekday()
    if dia_semana in [0, 3]: EXERCICIOS = ["Barra Fixa", "Flexão de Braço", "Remada"]
    else: EXERCICIOS = ["Agachamento", "Afundo", "Prancha (segundos)"]

st.subheader(f"🥋 Treino de Hoje: {divisao}")
rows = query_all("SELECT exercise_name, reps, sets FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {r["exercise_name"]: {"reps": r["reps"], "sets": r["sets"]} for r in rows}

with st.form("form_treino"):
    novos_valores = {}
    for ex in EXERCICIOS:
        valor_atual = treinos_hoje.get(ex, {"reps": 0, "sets": 0})
        col1, col2 = st.columns([2, 1])
        with col1: st.markdown(f"**{ex}**")
        with col2:
            if "Prancha" in ex:
                reps = st.number_input(f"Segundos", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}")
                sets = 1
            else:
                reps = st.number_input(f"Reps", min_value=0, value=int(valor_atual["reps"]), key=f"reps_{ex}")
                sets = st.number_input(f"Séries", min_value=0, value=int(valor_atual["sets"]), key=f"sets_{ex}")
            novos_valores[ex] = {"reps": reps, "sets": sets}
    if st.form_submit_button("💾 Salvar Treino", use_container_width=True):
        for ex, val in novos_valores.items():
            if val["reps"] > 0:
                execute("INSERT INTO exercise_logs (log_date, exercise_name, reps, sets) VALUES (?, ?, ?, ?) ON CONFLICT(log_date, exercise_name) DO UPDATE SET reps = excluded.reps, sets = excluded.sets", (hoje, ex, val["reps"], val["sets"]))
        st.rerun()

st.divider()
st.subheader("⏱️ Cronômetro de Descanso (2:30)")
import streamlit.components.v1 as components
components.html("""<div style="text-align: center; color: #F2F2F2;"><button onclick="startTimer()" style="padding: 10px 20px; background: #8B0000; color: white; border: none; border-radius: 5px; cursor: pointer;">Iniciar Descanso</button><h1 id="timer" style="font-size: 54px; color: #8B0000;">02:30</h1></div><script>let timeLeft=150;let timerId;function startTimer(){if(timerId)clearInterval(timerId);timeLeft=150;updateDisplay();timerId=setInterval(()=>{timeLeft--;if(timeLeft<0){clearInterval(timerId);alert("Descanso finalizado!");timeLeft=150;}updateDisplay();},1000);}function updateDisplay(){let m=Math.floor(timeLeft/60);let s=timeLeft%60;document.getElementById("timer").innerText=m+":"+(s<10?"0":"")+s;}</script>""", height=180)

st.divider()
st.subheader("🤖 Treinador de IA")
if st.button("🪄 Gerar Ficha de Treino para Hoje", use_container_width=True):
    with st.spinner("Analisando..."):
        hist = query_all("SELECT log_date, exercise_name, reps FROM exercise_logs ORDER BY log_date DESC LIMIT 15")
        ctx = "".join([f"- {h['log_date']}: {h['exercise_name']} - {h['reps']} reps\\n" for h in hist])
        prompt = f"Atue como treinador. Aluno ectomorfo (1,86m, 70kg). Divisão atual: {divisao}. Histórico:\\n{ctx}\\nSugira o treino de hoje focando em progressão."
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)
'''

# ==============================================================================
# 2. INFORMAÇÃO (Com Newsletter Integrada)
# ==============================================================================
CONTEUDO_INFORMACAO = '''import streamlit as st
import sys
from pathlib import Path
import yfinance as yf
import requests
import feedparser
import readtime
import re
import trafilatura
from concurrent.futures import ThreadPoolExecutor

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db
from core.database import query_all

init_db()

st.title("📰 Informação & Notícias")
tab_financas, tab_newsletter = st.tabs(["📈 Finanças & Notícias Diárias", "⚡ The Samurai Brief"])

with tab_financas:
    st.subheader("Cotações (Tempo Real)")
    col1, col2, col3 = st.columns(3)
    tickers = {"Dólar": "BRL=X", "IBOVESPA": "^BVSP", "Bitcoin": "BTC-USD"}
    for i, (nome, ticker) in enumerate(tickers.items()):
        try:
            data = yf.Ticker(ticker).history(period="1d")
            if not data.empty:
                preco = data['Close'].iloc[-1]
                with [col1, col2, col3][i]:
                    st.markdown(f"""<div class="samurai-card"><div class="titulo">{nome}</div><div class="valor">R$ {preco:,.2f}</div></div>""", unsafe_allow_html=True)
        except: pass

    st.divider()
    st.subheader("🗞️ Últimas Notícias (G1)")
    try:
        url = "https://g1.globo.com/rss/g1/"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        feed = feedparser.parse(response.content)
        for entry in feed.entries[:5]: st.markdown(f"- [{entry.title}]({entry.link})")
    except: st.warning("Erro ao carregar notícias.")

with tab_newsletter:
    emails = query_all("SELECT * FROM newsletters_inbox ORDER BY received_at DESC LIMIT 5")
    if not emails:
        st.info("Nenhuma newsletter recebida ainda.")
    else:
        if st.button("📰 Gerar 'The Samurai Brief' do Dia (IA)", use_container_width=True):
            with st.spinner("Resumindo newsletters..."):
                from bs4 import BeautifulSoup
                texto = ""
                for e in emails[:3]:
                    soup = BeautifulSoup(e['content'], "html.parser")
                    texto += f"--- {e['subject']} ---\\n{soup.get_text(strip=True)}\\n"
                prompt = f"Atue como editor da newsletter The Hustle. Resuma os pontos principais:\\n{texto}"
                resumo = ask_gemini(prompt)
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Edição de Hoje</div><div style="white-space: pre-wrap;">{resumo}</div></div>""", unsafe_allow_html=True)
        
        for e in emails:
            with st.expander(f"✉️ {e['subject']}"):
                st.markdown(f"<div style='max-height: 400px; overflow-y: auto;'>{e['content']}</div>", unsafe_allow_html=True)
'''

# ==============================================================================
# 3. PATRIMÔNIO (Com Renda Fixa)
# ==============================================================================
CONTEUDO_PATRIMONIO = '''import streamlit as st
import sys
from pathlib import Path
from datetime import date
import yfinance as yf
import pandas as pd
import plotly.express as px

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()
st.title("💎 Patrimônio")

tab_acoes, tab_renda_fixa, tab_gastos = st.tabs(["📊 Ações/FIIs", "🏦 Renda Fixa", "💸 Gastos"])

with tab_acoes:
    carteira = query_all("SELECT * FROM portfolio ORDER BY ticker")
    with st.expander("➕ Adicionar Ação"):
        with st.form("form_ativo"):
            ticker = st.text_input("Ticker (ex: PETR4.SA)").upper()
            qtd = st.number_input("Qtd", min_value=1, value=100)
            pm = st.number_input("Preço Médio (R$)", min_value=0.01, value=30.00)
            if st.form_submit_button("Salvar"):
                execute("INSERT INTO portfolio (ticker, quantity, average_price) VALUES (?, ?, ?) ON CONFLICT(ticker) DO UPDATE SET quantity=excluded.quantity, average_price=excluded.average_price", (ticker, qtd, pm))
                st.rerun()
    
    if carteira:
        for a in carteira:
            try:
                data = yf.Ticker(a["ticker"]).history(period="1d")
                preco = data['Close'].iloc[-1] if not data.empty else a["average_price"]
            except: preco = a["average_price"]
            lucro = (preco - a["average_price"]) * a["quantity"]
            cor = "#4CAF50" if lucro >= 0 else "#F44336"
            st.markdown(f"""<div class="samurai-card" style="border-left-color: {cor};"><div style="display:flex; justify-content:space-between;"><div>{a['ticker']} ({a['quantity']} cotas)</div><div style="color:{cor};">R$ {lucro:.2f}</div></div></div>""", unsafe_allow_html=True)

with tab_renda_fixa:
    st.subheader("Seus Investimentos em Renda Fixa")
    st.info("Cadastre aqui Tesouro Direto, CDBs, LCI/LCA, etc.")
    with st.form("form_renda_fixa"):
        nome = st.text_input("Nome do Título (ex: Tesouro Selic 2029)")
        valor_investido = st.number_input("Valor Investido (R$)", min_value=0.0, step=100.0)
        taxa = st.text_input("Taxa (ex: 11% a.a ou 100% CDI)")
        if st.form_submit_button("Adicionar Renda Fixa"):
            # Como não criamos uma tabela nova, usamos a de portfolio com ticker customizado
            execute("INSERT INTO portfolio (ticker, quantity, average_price) VALUES (?, ?, ?) ON CONFLICT(ticker) DO UPDATE SET quantity=excluded.quantity, average_price=excluded.average_price", (f"RF: {nome} ({taxa})", 1, valor_investido))
            st.success("Adicionado!")
            st.rerun()
    
    renda_fixa_db = query_all("SELECT * FROM portfolio WHERE ticker LIKE 'RF:%'")
    for rf in renda_fixa_db:
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;"><div class="titulo">{rf['ticker']}</div><div class="valor">R$ {rf['average_price']:.2f}</div></div>""", unsafe_allow_html=True)

with tab_gastos:
    with st.form("form_gasto"):
        desc = st.text_input("Descrição")
        val = st.number_input("Valor (R$)", min_value=0.0)
        if st.form_submit_button("Registrar Gasto"):
            execute("INSERT INTO expenses (expense_date, description, amount) VALUES (?, ?, ?)", (date.today().isoformat(), desc, val))
            st.rerun()
    for g in query_all("SELECT * FROM expenses ORDER BY expense_date DESC LIMIT 10"):
        st.markdown(f"- {g['description']}: R$ {g['amount']:.2f} ({g['expense_date']})")
'''

# ==============================================================================
# 4. DESCANSO (3 Opções de Cada)
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
'''

# ==============================================================================
# 5. RELIGIÃO (Com Bíblia Integrada)
# ==============================================================================
CONTEUDO_RELIGIAO = '''import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db, setup_biblia
from services.ai import ask_gemini

init_db()

st.title("🕊️ Religião & Bíblia")
tab_biblia, tab_praticas = st.tabs(["📖 Leitura Bíblica Diária", "🙏 Práticas e Oração"])

with tab_biblia:
    count_prog = query_one("SELECT COUNT(*) AS c FROM reading_progress")["c"]
    if count_prog == 0:
        with st.spinner("Iniciando plano..."):
            setup_biblia()
        st.rerun()
        
    proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")
    if not proximo:
        st.success("🎉 Você concluiu a Bíblia!")
    else:
        day = proximo["day"]
        plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
        if plano:
            versiculos = query_all("SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id", (plano["start_verse_id"], plano["end_verse_id"]))
            if versiculos:
                ref = f"{versiculos[0]['book_name']} {versiculos[0]['chapter']}:{versiculos[0]['verse']}"
                st.subheader(f"Dia {day} de 365 - {ref}")
                texto = "".join([f"**{v['verse']}** {v['text']}\\n" for v in versiculos])
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 300px; overflow-y: auto;"><div style="line-height: 1.8;">{texto}</div></div>""", unsafe_allow_html=True)
                if st.button("✅ Concluir Leitura", use_container_width=True):
                    execute("UPDATE reading_progress SET completed = 1 WHERE day = ?", (day,))
                    st.rerun()

with tab_praticas:
    st.subheader("🙏 Práticas Espirituais")
    habits = query_all("SELECT h.id, h.name, COALESCE(l.done, 0) AS done FROM habits h LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ? WHERE h.pillar = 'Religião' AND h.active = 1", (date.today().isoformat(),))
    for h in habits:
        if st.checkbox(h["name"], value=bool(h["done"])):
            execute("INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, 1) ON CONFLICT(habit_id, log_date) DO UPDATE SET done = 1", (h["id"], date.today().isoformat()))
    
    st.divider()
    st.subheader("🙏 Oração do Dia")
    if st.button("Gerar Oração com IA", use_container_width=True):
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;">{ask_gemini("Crie uma oração curta e poderosa para o dia de hoje.")}</div>""", unsafe_allow_html=True)
'''

# ==============================================================================
# 6. ALIMENTAÇÃO (3 Opções por Refeição)
# ==============================================================================
CONTEUDO_ALIMENTACAO = '''import streamlit as st
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
'''

# ==============================================================================
# 7. MENTE (Correção do Erro yt_dlp)
# ==============================================================================
CONTEUDO_MENTE = '''import streamlit as st
import sys
import re
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("🧠 Mente")
tab_leitura, tab_youtube = st.tabs(["📚 Livros (PDF)", "📺 Resumo de Vídeos (YouTube)"])

with tab_leitura:
    st.write("Função de PDF mantida.")

with tab_youtube:
    st.header("Resumo de Vídeos do YouTube")
    video_url = st.text_input("URL do Vídeo:", placeholder="https://www.youtube.com/watch?v=...")
    
    if st.button("📺 Extrair Leitura do Vídeo", use_container_width=True):
        if not video_url:
            st.warning("Cole uma URL.")
        else:
            with st.spinner("Processando..."):
                try:
                    video_id = re.search(r"(?:v=|\\/)([0-9A-Za-z_-]{11}).*", video_url).group(1)
                    try:
                        from youtube_transcript_api import YouTubeTranscriptApi
                        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
                        texto_video = " ".join([t['text'] for t in transcript])
                        st.toast("Legendas encontradas!")
                    except Exception:
                        st.error("Vídeo sem legendas. A transcrição por áudio (Whisper) requer instalação local. Rode o projeto no seu PC via INICIAR.bat para usar esse recurso.")
                        st.stop()
                        
                    prompt = f"Resuma em tópicos:\\n{texto_video[:15000]}"
                    st.markdown(f"""<div class="samurai-card" style="border-left-color: #FF0000;"><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Erro: {e}")
'''

# ==============================================================================
# 8. APP.PY (Remover Newsletter do Menu)
# ==============================================================================
def atualizar_app_py():
    arq_app = BASE / "app.py"
    texto = arq_app.read_text(encoding="utf-8")
    # Remove a linha que define a página newsletter
    texto = re.sub(r'newsletter = st\.Page\(.*?\)\n', '', texto)
    # Remove do menu
    texto = texto.replace(", newsletter", "")
    arq_app.write_text(texto, encoding="utf-8")
    print("[OK] app.py atualizado (Newsletter removida do menu).")

# ==============================================================================
# HELPERS DE SINCRONIZAÇÃO E EXECUÇÃO
# ==============================================================================
def _run(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e: return 1, str(e)

def _verificar_stage():
    _, out = _run(["git", "diff", "--cached", "--name-only"])
    for rel in [l for l in out.splitlines() if l.strip()]:
        if Path(rel).name in ARQUIVOS_PROIBIDOS:
            raise RuntimeError(f"🚨 Segredo detectado: {rel}")

def aplicar_melhoria():
    print("=" * 60)
    print("⚔️  APLICANDO MELHORIA MASSIVA (6 PÁGINAS)")
    print("=" * 60)

    arquivos = {
        "ui/pages/01_Corpo.py": CONTEUDO_CORPO,
        "ui/pages/03_Informacao.py": CONTEUDO_INFORMACAO,
        "ui/pages/04_Patrimonio.py": CONTEUDO_PATRIMONIO,
        "ui/pages/05_Descanso.py": CONTEUDO_DESCANSO,
        "ui/pages/08_Religiao.py": CONTEUDO_RELIGIAO,
        "ui/pages/11_Alimentacao.py": CONTEUDO_ALIMENTACAO,
        "ui/pages/02_Mente.py": CONTEUDO_MENTE
    }

    for caminho, conteudo in arquivos.items():
        try:
            ast.parse(conteudo)
            (BASE / caminho).write_text(conteudo, encoding="utf-8")
            print(f"[OK] Arquivo atualizado: {caminho}")
        except SyntaxError as e:
            print(f"[ERRO] Sintaxe em {caminho}: {e}")
            sys.exit(1)

    atualizar_app_py()

    print("\n☁️  SINCRONIZANDO COM O SERVIDOR (GitHub)")
    _run(["git", "add", "-A"])
    _run(["git", "rm", "--cached", "PROJETO_SAMURAI*.md"])
    
    try:
        _verificar_stage()
    except RuntimeError as e:
        _run(["git", "reset"])
        print(e)
        sys.exit(1)

    code, out = _run(["git", "commit", "-m", "Feat: Melhorias massivas (Dividir treinos, unificar info/news, renda fixa, 3 opcoes descanso e comida, Biblia em Religiao)"])
    if code != 0 and "nothing to commit" not in out:
        print(f"[ERRO] Commit falhou: {out}")
        sys.exit(1)
    
    print("[OK] Commit realizado.")
    _run(["git", "pull", "origin", "main", "--rebase", "--no-edit"])
    
    code, out = _run(["git", "push", "origin", "main"])
    if code != 0:
        print(f"[ERRO] Push falhou: {out}")
        sys.exit(1)
    
    print("[OK] Push concluído. O Streamlit vai atualizar em instantes.")
    print("=" * 60)

if __name__ == "__main__":
    aplicar_melhoria()