"""Dojo — resumo do dia, hábitos pendentes e energia."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date

import streamlit as st

from core.database import query_all, query_one, execute

today_iso = date.today().isoformat()

st.title("🏯 Dojo")

# --- GAMIFICAÇÃO ---
try:
    stats = query_one("SELECT xp FROM user_stats WHERE id = 1") or {"xp": 0}
except Exception:
    execute("CREATE TABLE IF NOT EXISTS user_stats (id INTEGER PRIMARY KEY, xp INTEGER NOT NULL DEFAULT 0, level INTEGER NOT NULL DEFAULT 1)")
    execute("INSERT INTO user_stats (id, xp, level) VALUES (1, 0, 1)")
    stats = {"xp": 0}
xp_total = stats["xp"] if stats else 0
nivel = (xp_total // 100) + 1
ranks = {1: "Ronin", 2: "Ashigaru", 3: "Samurai", 4: "Hatamoto", 5: "Daimyo"}
rank_atual = ranks.get(nivel, "Lenda")

st.markdown(f"""
<div class="samurai-card" style="display: flex; justify-content: space-between; align-items: center; border-left-color: #F9A825;">
    <div>
        <div class="titulo">Patente</div>
        <div class="valor">Nível {nivel} - {rank_atual}</div>
    </div>
    <div style="text-align: right;">
        <div class="titulo">Experiência</div>
        <div class="valor">{xp_total} XP</div>
    </div>
</div>
""", unsafe_allow_html=True)
DIAS_SEMANA = {
    "Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"
}
dia_ingles = date.today().strftime('%A')
dia_pt = DIAS_SEMANA.get(dia_ingles, dia_ingles)
st.caption(f"Hoje é {dia_pt}, {date.today().strftime('%d/%m/%Y')}")

# --- HEATMAP DE CONSTÂNCIA (ESTILO GITHUB) ---
import datetime
import pandas as pd

st.divider()
st.subheader("🔥 Heatmap de Constância")
st.caption("Cada quadrado é um dia. A cor representa quantos hábitos você cumpriu.")

# Pega os hábitos dos últimos 365 dias
hoje = date.today()
um_ano_atras = hoje - datetime.timedelta(days=364)
logs = query_all(
    "SELECT log_date, COUNT(*) as total FROM habit_logs WHERE done = 1 AND log_date >= ? GROUP BY log_date",
    (um_ano_atras.isoformat(),)
)
dados_habitos = {r["log_date"]: int(r["total"]) for r in logs}

# Gera os dias
dias = []
for i in range(365):
    dia_atual = um_ano_atras + datetime.timedelta(days=i)
    qtd = dados_habitos.get(dia_atual.isoformat(), 0)
    dias.append({"data": dia_atual, "count": qtd})

df_heatmap = pd.DataFrame(dias)
# FIX: Força a conversão para datetime antes de usar .dt
df_heatmap["data"] = pd.to_datetime(df_heatmap["data"])
df_heatmap["semana"] = df_heatmap["data"].dt.isocalendar().week
df_heatmap["dia_semana"] = df_heatmap["data"].dt.weekday
df_heatmap["mes"] = df_heatmap["data"].dt.month

def get_color(count):
    if count == 0: return "#171717" # Vazio
    if count <= 2: return "#5C0000" # Pouco
    if count <= 5: return "#8B0000" # Médio
    if count <= 8: return "#B22222" # Bom
    return "#FF4444" # Excelente

# Constrói o HTML do Heatmap
html = '<div style="display: flex; gap: 3px; overflow-x: auto; padding-bottom: 10px;">'
for week in sorted(df_heatmap["semana"].unique()):
    html += '<div style="display: flex; flex-direction: column; gap: 3px;">'
    semana_df = df_heatmap[df_heatmap["semana"] == week]
    # Preenche dias faltantes no início da semana
    for i in range(7):
        dia = semana_df[semana_df["dia_semana"] == i]
        if not dia.empty:
            row = dia.iloc[0]
            cor = get_color(row["count"])
            data_str = row["data"].strftime("%d/%m/%Y")
            html += f'<div title="{data_str}: {row["count"]} hábitos" style="width: 12px; height: 12px; background-color: {cor}; border-radius: 2px;"></div>'
        else:
            html += '<div style="width: 12px; height: 12px;"></div>'
    html += '</div>'
html += '</div>'

st.markdown(html, unsafe_allow_html=True)

# Legenda
st.markdown("""
<div style="display: flex; align-items: center; gap: 5px; font-size: 0.8rem; color: #CCC; margin-top: -10px;">
    <span>Menos</span>
    <div style="width: 10px; height: 10px; background-color: #171717; border-radius: 2px;"></div>
    <div style="width: 10px; height: 10px; background-color: #5C0000; border-radius: 2px;"></div>
    <div style="width: 10px; height: 10px; background-color: #8B0000; border-radius: 2px;"></div>
    <div style="width: 10px; height: 10px; background-color: #B22222; border-radius: 2px;"></div>
    <div style="width: 10px; height: 10px; background-color: #FF4444; border-radius: 2px;"></div>
    <span>Mais</span>
</div>
""", unsafe_allow_html=True)

# --- YEAR IN REVIEW ---
st.divider()
st.subheader("📊 Resumo do Ano")

col_a, col_b, col_c = st.columns(3)

# Totais
total_habitos = sum(dados_habitos.values())
total_treinos = query_one("SELECT COUNT(DISTINCT log_date) AS c FROM exercise_logs WHERE log_date >= ?", (um_ano_atras.isoformat(),))
total_treinos = total_treinos["c"] if total_treinos else 0
total_flashcards = query_one("SELECT COUNT(*) AS c FROM flashcards")
total_flashcards = total_flashcards["c"] if total_flashcards else 0

with col_a:
    st.metric("Hábitos Cumpridos", total_habitos)
with col_b:
    st.metric("Dias de Treino", total_treinos)
with col_c:
    st.metric("Flashcards Criados", total_flashcards)


checkin = query_one(
    "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
)

col1, col2, col3 = st.columns(3)
if checkin:
    with col1:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Energia</div>
                <div class="valor">{checkin['energy']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Sono</div>
                <div class="valor">{checkin['sleep_hours']}h</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">Estresse</div>
                <div class="valor">{checkin['stress']}/10</div>
            </div>""",
            unsafe_allow_html=True,
        )
else:
    st.info("⚡ Nenhum check-in hoje. Vá em **Consistência** e registre sua energia.")

st.subheader("🎯 Hábitos pendentes hoje")

rows = query_all(
    """
    SELECT h.id, h.name, h.pillar,
           COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l
        ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1
    ORDER BY h.pillar, h.name
    """,
    (today_iso,),
)

pendentes = [r for r in rows if not r["done"]]
concluidos = [r for r in rows if r["done"]]

if not pendentes:
    st.success("🥋 Todos os hábitos foram cumpridos. Disciplina exemplar.")
else:
    for r in pendentes:
        st.markdown(
            f"""<div class="samurai-card">
                <div class="titulo">{r['pillar']}</div>
                <div class="valor" style="font-size:1.1rem;">{r['name']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

if concluidos:
    st.divider()
    st.caption(f"✅ {len(concluidos)} hábito(s) já cumprido(s) hoje")

st.divider()
if st.button("📝 Fazer check-in diário agora", use_container_width=True):
    st.switch_page("ui/pages/07_Consistencia.py")
