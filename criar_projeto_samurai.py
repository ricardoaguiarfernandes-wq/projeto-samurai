"""
aplicar_academia.py — Adiciona opções de Musculação (Academia) ao Corpo.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

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
st.caption("Treino progressivo com carga e histórico. (Calistenia e Musculação)")
hoje = date.today().isoformat()

# NOVAS OPÇÕES DE DIVISÃO (CALISTENIA E MUSCULAÇÃO)
divisao = st.selectbox("Divisão de Treino:", [
    "Calistenia - Full Body",
    "Calistenia - PPL (Push/Pull/Legs)",
    "Calistenia - Upper/Lower",
    "Musculação - Full Body",
    "Musculação - ABC (Peito/Costas/Pernas)",
    "Musculação - Push/Pull/Legs"
])

dia = date.today().weekday()

if divisao == "Calistenia - Full Body":
    EXERCICIOS_PADRAO = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]
elif divisao == "Calistenia - PPL (Push/Pull/Legs)":
    if dia in [0, 3]: EXERCICIOS_PADRAO = ["Flexão de Braço", "Desenvolvimento", "Tríceps"]
    elif dia in [1, 4]: EXERCICIOS_PADRAO = ["Barra Fixa", "Remada", "Rosca Direta"]
    else: EXERCICIOS_PADRAO = ["Agachamento", "Afundo", "Panturrilha"]
elif divisao == "Calistenia - Upper/Lower":
    if dia in [0, 3]: EXERCICIOS_PADRAO = ["Barra Fixa", "Flexão de Braço", "Remada"]
    else: EXERCICIOS_PADRAO = ["Agachamento", "Afundo", "Prancha (segundos)"]
elif divisao == "Musculação - Full Body":
    EXERCICIOS_PADRAO = ["Supino Reto", "Agachamento Livre", "Puxada Frontal", "Desenvolvimento com Halteres"]
elif divisao == "Musculação - ABC (Peito/Costas/Pernas)":
    if dia in [0, 3]: EXERCICIOS_PADRAO = ["Supino Reto", "Supino Inclinado", "Tríceps Testa", "Elevação Lateral"]
    elif dia in [1, 4]: EXERCICIOS_PADRAO = ["Puxada Frontal", "Remada Curvada", "Rosca Direta", "Rosca Martelo"]
    else: EXERCICIOS_PADRAO = ["Agachamento Livre", "Leg Press", "Cadeira Extensora", "Mesa Flexora"]
else: # Musculação - PPL
    if dia in [0, 3]: EXERCICIOS_PADRAO = ["Supino Reto", "Desenvolvimento Militar", "Tríceps Corda", "Crucifixo"]
    elif dia in [1, 4]: EXERCICIOS_PADRAO = ["Puxada Frontal", "Remada Baixa", "Rosca Direta", "Rosca Scott"]
    else: EXERCICIOS_PADRAO = ["Agachamento Livre", "Leg Press", "Cadeira Extensora", "Panturrilha em Pé"]

st.subheader(f"🥋 Treino de Hoje: {divisao}")

if st.button("🤖 Gerar Ficha de Treino com IA para Hoje", use_container_width=True):
    with st.spinner("O Treinador está analisando e preparando a ficha..."):
        hist = query_all("SELECT log_date, exercise_name, reps FROM exercise_logs ORDER BY log_date DESC LIMIT 15")
        ctx = "".join([f"- {h['log_date']}: {h['exercise_name']} - {h['reps']} reps\\n" for h in hist])

        prompt = f"Atue como treinador de musculação/calistenia. Aluno ectomorfo. Divisão: {divisao}. Histórico:\\n{ctx}\\n\\nSugira a ficha de hoje focando em progressão. Seja direto e motivador.\\nIMPORTANTE: No final da sua resposta, adicione um bloco de código JSON contendo APENAS os nomes dos exercícios sugeridos.\\nExemplo:\\n```json\\n{{\\"exercicios\\": [\\"Supino Reto\\", \\"Agachamento Livre\\", \\"Puxada Frontal\\", \\"Rosca Direta\\"]}}\\n```\\nNão escreva nada após o bloco JSON."

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
            if "Prancha" in ex or "Segundos" in ex or "Isometria" in ex or "Cardio" in ex:
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
    fig = px.line(df_agrupado, x='log_date', y='reps', color='exercise_name', markers=True, color_discrete_sequence=['#8B0000', '#F9A825', '#4CAF50', '#2196F3', '#9C27B0'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#F2F2F2'))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Sem histórico.")
"""

def _run(cmd):
    subprocess.run(cmd, cwd=BASE, capture_output=True)

def aplicar():
    print("=" * 60)
    print("⚔️  ADICIONANDO MUSCULAÇÃO AO CORPO")
    print("=" * 60)
    
    cam = "ui/pages/01_Corpo.py"
    try:
        ast.parse(CONTEUDO_CORPO)
        (BASE / cam).write_text(CONTEUDO_CORPO, encoding="utf-8")
        print(f"[OK] {cam} atualizado com sucesso.")
    except SyntaxError as e:
        print(f"[ERRO] Sintaxe em {cam}: {e}")
        sys.exit(1)

    print("\n☁️  SINCRONIZANDO COM O GITHUB")
    _run(["git", "add", "-A"])
    _run(["git", "commit", "-m", "Feat: Adiciona divisoes de musculacao (Academia) na pagina Corpo"])
    _run(["git", "push", "origin", "main"])
    print("[OK] Push concluído. O Streamlit vai atualizar em instantes.")
    print("=" * 60)

if __name__ == "__main__":
    aplicar()