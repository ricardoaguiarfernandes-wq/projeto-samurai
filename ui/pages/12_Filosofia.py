import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db
from core.database import execute
from services.ai import ask_gemini

init_db()

st.title("🏛️ Filosofia & Sabedoria")
st.caption("Desenvolvimento do raciocínio, visão interdisciplinar e as aulas do COF.")

# --- DESAFIO DO DIA ---
st.subheader("🧠 Desafio Intelectual do Dia")

PROMPTS_COF = [
    "O que é a verdadeira ignorância: não saber, ou saber e não aplicar?",
    "Como você pode diferenciar uma opinião de um conhecimento real em sua vida hoje?",
    "Qual foi a última vez que você mudou de ideia? O que te fez mudar?",
    "O que a sua rotina atual diz sobre a sua visão de mundo?",
    "Por que buscamos distrações em vez de encarar a realidade?",
    "Qual a diferença entre saber o nome de uma coisa e entender como ela funciona?",
    "Como a ordem no seu ambiente físico reflete a ordem da sua mente?"
]

# Escolhe a frase baseada no dia do ano
prompt_do_dia = PROMPTS_COF[date.today().toordinal() % len(PROMPTS_COF)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #8B0000;">
        <div class="titulo">Reflexão de Hoje</div>
        <div class="valor" style="font-size: 1.2rem; font-weight: 500;">{prompt_do_dia}</div>
    </div>""", unsafe_allow_html=True
)

# --- MENTOR DE FILOSOFIA (IA) ---
st.divider()
st.subheader("🤖 Mentor Filosófico (Inspirado no COF)")
st.write("Debata com a IA. Ela usará o método socrático para testar suas ideias.")

with st.form("form_filosofia"):
    reflexao = st.text_area("Sua reflexão sobre o tema:", height=150, placeholder="Escreva sem medo de errar. A filosofia é o exercício do pensamento...")
    submitted = st.form_submit_button("Debater com o Mentor", use_container_width=True)

if submitted and reflexao.strip():
    with st.spinner("O Mentor está analisando seus argumentos..."):
        prompt_ia = f"""Atue como um mentor de filosofia no estilo interdisciplinar do Curso Online de Filosofia (COF). 
O tema do dia é: "{prompt_do_dia}"
O usuário respondeu com: "{reflexao}"

Sua tarefa:
1. Validar o esforço de raciocínio do usuário.
2. Apontar uma falha lógica, uma contradição ou um ponto cego no argumento dele (sem ser arrogante).
3. Fazer UMA pergunta socrática profunda que force o usuário a pensar além da superficialidade.
4. Terminar com uma citação curta (real ou adaptada) de um filósofo clássico.

Seja rigoroso, direto, mas acolhedor. O objetivo é o amadurecimento intelectual."""
        
        resposta_ia = ask_gemini(prompt_ia)
        
        st.markdown(
            f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
                <div class="titulo">A Resposta do Mestre</div>
                <div style="color: #F2F2F2; font-size: 0.95rem; line-height: 1.6; white-space: pre-wrap;">{resposta_ia}</div>
            </div>""", unsafe_allow_html=True
        )

# --- OUTROS MATERIAIS (COF) ---
st.divider()
st.subheader("📚 Estudos Complementares")
st.markdown("""
Aqui você pode construir uma base sólida de conhecimento interdisciplinar:
*   **Leitura:** Procure ler 15 minutos por dia de um livro clássico (filosofia, teologia ou literatura).
*   **Retenção:** Anote o que leu. Escrever força a mente a organizar o caos.
*   **Conexões:** Tente ligar o que você leu com um problema real da sua vida.
""")
