"""Consistência — check-in diário, marcação de hábitos e score anti-burnout."""
from __future__ import annotations

import sys
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from datetime import date, timedelta

import streamlit as st
from fpdf import FPDF
import io
import pandas as pd
import plotly.express as px

from core.database import execute, query_all, query_one
from services.ai import ask_gemini

today = date.today()
today_iso = today.isoformat()

def calcular_burnout() -> tuple[float, dict]:
    week_ago = (today - timedelta(days=7)).isoformat()

    checkins = query_all("SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?", (week_ago,))
    total_habits = query_one("SELECT COUNT(*) AS c FROM habits WHERE active = 1")["c"] or 0
    logs = query_all("SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,))
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    total = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return total, {
        "avg_energy": avg_energy,
        "avg_stress": avg_stress,
        "avg_sleep": avg_sleep,
        "taxa": taxa,
    }

def classificar_burnout(score: float) -> tuple[str, str]:
    if score < 30:
        return "🟢 Baixo", "#2E7D32"
    if score < 60:
        return "🟡 Médio", "#F9A825"
    if score < 80:
        return "🟠 Alto", "#EF6C00"
    return "🔴 Crítico", "#C62828"

st.title("🎯 Consistência")
st.caption("Disciplina diária é o que forja o samurai.")

st.subheader("📝 Check-in do dia")
existente = query_one("SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,))
MOOD_OPTIONS = ["Ótimo", "Bom", "Neutro", "Cansado", "Estressado", "Ansioso"]
mood_default = (MOOD_OPTIONS.index(existente["mood"]) if existente and existente["mood"] in MOOD_OPTIONS else 2)

with st.form("form_checkin", clear_on_submit=False):
    energy = st.slider("Energia (1–10)", 1, 10, int(existente["energy"]) if existente else 6)
    sleep_hours = st.number_input("Horas de sono", min_value=0.0, max_value=16.0, step=0.5, value=float(existente["sleep_hours"]) if existente else 7.0)
    mood = st.selectbox("Humor", MOOD_OPTIONS, index=mood_default)
    stress = st.slider("Estresse (1–10)", 1, 10, int(existente["stress"]) if existente else 5)
    notes = st.text_area("Notas (opcional)", value=existente["notes"] if existente and existente["notes"] else "")
    submit = st.form_submit_button("💾 Salvar check-in", use_container_width=True)

if submit:
    execute(
        """
        INSERT INTO daily_checkins (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy = excluded.energy, sleep_hours = excluded.sleep_hours, mood = excluded.mood, stress = excluded.stress, notes = excluded.notes
        """,
        (today_iso, energy, sleep_hours, mood, stress, notes or None),
    )
    st.success("[OK] Check-in registrado.")
    st.rerun()

st.divider()
st.subheader("🥋 Hábitos de hoje")
habits = query_all(
    """
    SELECT h.id, h.name, h.pillar, COALESCE(l.done, 0) AS done
    FROM habits h LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.active = 1 ORDER BY h.pillar, h.name
    """, (today_iso,),
)
alterou = False
for h in habits:
    novo = st.checkbox(f"**{h['pillar']}** · {h['name']}", value=bool(h["done"]), key=f"habit_{h['id']}")
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """, (h["id"], today_iso, 1 if novo else 0),
        )
        # Bugfix: Adicionar XP se o hábito foi concluído (e não estava concluído antes)
        if novo and not h["done"]:
            try:
                execute("UPDATE user_stats SET xp = xp + 10 WHERE id = 1")
            except Exception:
                pass
        alterou = True
if alterou: st.rerun()

st.divider()
st.subheader("🔥 Score Anti-Burnout (7 dias)")
score, metricas = calcular_burnout()
label, cor = classificar_burnout(score)

st.markdown(
    f"""<div class="samurai-card" style="border-left-color:{cor};">
        <div class="titulo">Risco atual</div>
        <div class="valor" style="color:{cor};">{score:.0f}/100 — {label}</div>
        <div class="detalhe">
            Média energia: {metricas['avg_energy']:.1f} · Sono: {metricas['avg_sleep']:.1f}h · Estresse: {metricas['avg_stress']:.1f} · Hábitos: {metricas['taxa']*100:.0f}%
        </div>
    </div>""", unsafe_allow_html=True,
)
st.progress(min(1.0, score / 100.0))

if score >= 80:
    st.error("⚠️ Risco crítico. Priorize descanso hoje. Nenhum treino vale um colapso.")
elif score >= 60:
    st.warning("Atenção: sinais de sobrecarga. Reduza intensidade e priorize sono.")


st.divider()
st.subheader("📊 Histórico de Energia e Estresse (14 dias)")

checkins_historico = query_all("SELECT checkin_date, energy, stress FROM daily_checkins ORDER BY checkin_date DESC LIMIT 14")
if checkins_historico:
    df_check = pd.DataFrame(checkins_historico)
    # Inverte para o gráfico ficar da esquerda (mais antigo) para direita (hoje)
    df_check = df_check.iloc[::-1]
    
    fig2 = px.line(
        df_check, 
        x='checkin_date', 
        y=['energy', 'stress'],
        markers=True,
        color_discrete_sequence=['#4CAF50', '#F44336'],
        labels={'value': 'Nível', 'variable': 'Métrica', 'checkin_date': 'Data'}
    )
    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#F2F2F2'),
        legend_title=""
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Faça check-ins diários para visualizar o histórico.")


st.divider()
st.subheader("📊 Correlação de Performance (30 dias)")
st.write("O Samurai cruzou seus dados para descobrir o que mais impacta a sua consistência.")

# Busca dados dos últimos 30 dias
from datetime import timedelta
import pandas as pd
import plotly.express as px

thirty_days_ago = (today - timedelta(days=30)).isoformat()

# Dados de Check-in
checkins_30d = query_all("SELECT checkin_date, energy, sleep_hours, stress FROM daily_checkins WHERE checkin_date >= ?", (thirty_days_ago,))

# Dados de Hábitos (quantos foram concluídos por dia)
habits_30d = query_all("SELECT log_date, COUNT(*) as habits_done FROM habit_logs WHERE done = 1 AND log_date >= ? GROUP BY log_date", (thirty_days_ago,))

if len(checkins_30d) < 5 or len(habits_30d) < 5:
    st.info("ℹ️ Dados insuficientes para gerar correlações precisas. Continue fazendo check-ins e marcando hábitos por pelo menos 5 dias.")
else:
    df_check = pd.DataFrame(checkins_30d)
    df_habits = pd.DataFrame(habits_30d)
    
    # Converte colunas numéricas para float (evita erro de string no Postgres)
    for col in ['energy', 'sleep_hours', 'stress']:
        df_check[col] = pd.to_numeric(df_check[col], errors='coerce').fillna(0)
    df_habits['habits_done'] = pd.to_numeric(df_habits['habits_done'], errors='coerce').fillna(0)

    # Faz o merge das duas tabelas pela data
    df_merged = pd.merge(df_check, df_habits, left_on='checkin_date', right_on='log_date', how='left').fillna(0)
    
    # Calcula a matriz de correlação (apenas colunas numéricas)
    df_corr = df_merged[['sleep_hours', 'energy', 'stress', 'habits_done']].corr()

    # Desenha o heatmap
    fig_corr = px.imshow(
        df_corr, 
        text_auto=".2f", 
        aspect="auto", 
        color_continuous_scale=['#F44336', '#171717', '#4CAF50'],
        labels=dict(color="Correlação")
    )
    fig_corr.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='#F2F2F2'),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    if st.button("🧠 Gerar Diagnóstico de Performance com IA", use_container_width=True):
        with st.spinner("Analisando suas correlações e traçando insights..."):
            # Prepara um resumo dos dados para a IA
            corr_sono = df_corr.loc['sleep_hours', 'habits_done']
            corr_energia = df_corr.loc['energy', 'habits_done']
            corr_estresse = df_corr.loc['stress', 'habits_done']
            
            prompt = f"""Atue como um Cientista de Dados e Mentor de Alta Performance.
Aqui estão as correlações dos últimos 30 dias do usuário:
- Sono vs Conclusão de Hábitos: {corr_sono:.2f}
- Energia vs Conclusão de Hábitos: {corr_energia:.2f}
- Estresse vs Conclusão de Hábitos: {corr_estresse:.2f}

Legenda: 1.0 é correlação positiva perfeita, -1.0 é negativa perfeita, 0 é neutro.

Sua missão:
1. Explique o que esses números significam na prática para a vida do usuário (sem usar jargão matemático complexo).
2. Dê 2 ações práticas baseadas nesses dados (ex: se sono tem correlação alta com hábitos, mande ele priorizar o sono).
3. Mantenha o tom de Mentor Samurai: direto, motivador e focado em evolução.

Responda em até 3 parágrafos."""

            diagnostico = ask_gemini(prompt)
            st.markdown(f'<div class="samurai-card" style="border-left-color: #2196F3;"><div class="titulo">Diagnóstico do Mentor</div><div style="white-space: pre-wrap;">{diagnostico}</div></div>', unsafe_allow_html=True)

st.divider()
st.subheader("📄 Exportar Relatório")
if st.button("Gerar Relatório em PDF", use_container_width=True):
    with st.spinner("Gerando PDF..."):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Relatorio Samurai - Consistencia", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        
        # Limpa emojis para não quebrar o PDF (fonte padrão do FPDF não suporta)
        label_limpo = label.encode('ascii', 'ignore').decode('ascii')
        
        pdf.cell(0, 10, f"Data: {today_iso}", ln=True)
        pdf.cell(0, 10, f"Score de Burnout: {score:.0f}/100 - {label_limpo}", ln=True)
        pdf.cell(0, 10, f"Media de Energia: {metricas['avg_energy']:.1f}/10", ln=True)
        pdf.cell(0, 10, f"Media de Sono: {metricas['avg_sleep']:.1f}h", ln=True)
        pdf.cell(0, 10, f"Media de Estresse: {metricas['avg_stress']:.1f}/10", ln=True)
        pdf.cell(0, 10, f"Taxa de Habitos: {metricas['taxa']*100:.0f}%", ln=True)
        
        _pdf_result = pdf.output()
        if isinstance(_pdf_result, str):
            pdf_bytes = _pdf_result.encode('latin-1')
        else:
            pdf_bytes = bytes(_pdf_result)
        st.download_button(
            label="⬇️ Baixar PDF",
            data=pdf_bytes,
            file_name=f"relatorio_samurai_{today_iso}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

st.divider()
st.subheader("🧠 Relatório do Mentor Samurai")
if st.button("📜 Gerar Análise Semanal com IA", use_container_width=True):
    with st.spinner("O Mentor está analisando seus dados da semana..."):
        prompt_ia = f"Atue como um mentor samurai sábio e direto. Aqui estão os dados da semana do usuário:\n- Score de Burnout: {score:.0f}/100\n- Média de Energia: {metricas['avg_energy']:.1f}\n- Média de Sono: {metricas['avg_sleep']:.1f}h\n- Média de Estresse: {metricas['avg_stress']:.1f}\n- Taxa de conclusão de hábitos: {metricas['taxa']*100:.0f}%\n\nEscreva um relatório semanal curto (max 3 parágrafos), motivador e realista. Se o burnout estiver alto (>60), aconselhe descanso. Se estiver baixo, parabenize e incentive a manter a disciplina. Mantenha o tom sério, mas encorajador."
        relatorio_ia = ask_gemini(prompt_ia)
        
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 15px;">
            <div class="titulo">Visão do Mestre</div>
            <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{relatorio_ia}</div>
        </div>""", unsafe_allow_html=True)
