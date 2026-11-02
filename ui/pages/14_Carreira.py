import streamlit as st
import sys
import json
import re
from datetime import date
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("💼 Carreira & Profissão")
st.caption("Trilha de evolução: Estagiário de Survey ➔ Surveyor Junior.")

hoje = date.today().isoformat()

# Busca as missões de hoje
missoes = query_all("SELECT id, task, completed FROM career_missions WHERE mission_date = ?", (hoje,))

if not missoes:
    st.info("🎯 Nenhuma missão definida para hoje. O seu Mentor de Carreira está pronto.")
    if st.button("🧠 Gerar Missões de Hoje com IA", use_container_width=True):
        with st.spinner("Traçando estratégia para a sua efetivação..."):
            prompt = """Atue como um Gestor Sênior e Mentor da área de Survey (levantamentos, inspeções, offshore/onshore).
O usuário é estagiário e tem a meta de ser efetivado como Surveyor Junior no início do próximo ano.

Crie 3 missões diárias curtas, práticas e teóricas para o dia de hoje. O foco deve ser:
1. Habilidade Técnica (ex: leitura de dados, equipamentos, normas, softwares).
2. Postura Profissional (ex: comunicação com a equipe, proatividade, relatórios).
3. Visão de Negócio (ex: entender o impacto do survey no projeto).

Sua resposta DEVE ser APENAS um JSON válido com a seguinte estrutura, sem formatação markdown:
{
  "missions": [
    "Missão 1...",
    "Missão 2...",
    "Missão 3..."
  ]
}
"""
            res = ask_gemini(prompt)
            m = re.search(r'\{.*\}', res, re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group(0))
                    for task in data.get("missions", []):
                        execute("INSERT INTO career_missions (mission_date, task, completed) VALUES (?, ?, 0)", (hoje, task))
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao processar missões: {e}")
            else:
                st.error("A IA não retornou o formato esperado. Tente novamente.")
else:
    st.subheader("📋 Missões de Hoje")
    alterou = False
    for m in missoes:
        novo = st.checkbox(m["task"], value=bool(m["completed"]), key=f"mission_{m['id']}")
        if novo != bool(m["completed"]):
            execute("UPDATE career_missions SET completed = ? WHERE id = ?", (1 if novo else 0, m["id"]))
            alterou = True
    
    if alterou:
        st.rerun()

    if all(m["completed"] for m in missoes):
        st.success("🏆 Todas as missões concluídas! O Surveyor Junior está cada vez mais perto.")

    st.divider()
    if st.button("🔄 Gerar Novas Missões (Substituir as de hoje)", use_container_width=True):
        execute("DELETE FROM career_missions WHERE mission_date = ?", (hoje,))
        st.rerun()
