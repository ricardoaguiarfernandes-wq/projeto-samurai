import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()

st.title("🪞 Autoconhecimento")
st.caption("Diário reflexivo e meditação.")

PROMPTS = [
    "O que drenou minha energia hoje e por quê?",
    "Qual pequena vitória eu tive hoje?",
    "O que eu faria diferente se pudesse recomeçar o dia?",
    "Pelo que sou grato neste exato momento?",
    "Qual pensamento negativo eu posso deixar ir embora?",
    "Como eu tratei as pessoas ao meu redor hoje?",
    "O que aprendi sobre mim mesmo nesta semana?",
]

prompt_do_dia = PROMPTS[date.today().toordinal() % len(PROMPTS)]

st.subheader("📝 Diário Reflexivo")
st.markdown(f"**Prompt de hoje:** *{prompt_do_dia}*")

with st.form("form_journal"):
    texto = st.text_area("Sua reflexão:", height=150, placeholder="Escreva livremente...")
    submitted = st.form_submit_button("Salvar e Refletir com IA", use_container_width=True)

if submitted and texto.strip():
    with st.spinner("O Mentor Samurai está refletindo sobre suas palavras..."):
        prompt_ia = f"Atue como um mentor samurai sábio e empático. O usuário escreveu a seguinte reflexão sobre o prompt '{prompt_do_dia}':\n\n'{texto.strip()}'\n\nForneça uma resposta curta (máximo 2 parágrafos) validando os sentimentos dele e oferecendo uma perspectiva focada em disciplina, evolução e paz interior. Fale de forma direta e acolhedora."
        reflexao_ia = ask_gemini(prompt_ia)
        
        execute(
            "INSERT INTO journal_entries (entry_date, prompt, content, ai_reflection) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), prompt_do_dia, texto.strip(), reflexao_ia)
        )
    st.success("Reflexão salva e analisada.")
    st.rerun()

st.divider()
st.subheader("🧘‍♂️ Meditação Curta")
st.markdown("""
**Respiração Box (5 minutos):**
1. Inspire contando até **4**.
2. Segure a respiração contando até **4**.
3. Expire lentamente contando até **4**.
4. Aguarde contando até **4**.
5. Repita por 5 minutos.
""")

st.divider()
st.subheader("📚 Histórico de Reflexões")

entries = query_all("SELECT * FROM journal_entries ORDER BY entry_date DESC, id DESC LIMIT 5")
if not entries:
    st.info("Nenhuma reflexão registrada ainda.")
else:
    for e in entries:
        with st.expander(f"📅 {e['entry_date']} — {e['prompt']}"):
            st.markdown(f"**Sua reflexão:**\n{e['content']}")
            if e['ai_reflection']:
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000; margin-top: 10px; padding: 10px;">
                    <div style="color: #F2F2F2; font-size: 0.9rem; font-style: italic;">
                        <b>Mentor Samurai:</b><br>{e['ai_reflection']}
                    </div>
                </div>""", unsafe_allow_html=True)


st.divider()
st.subheader("💬 Converse com o Mentor Samurai")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Como você está se sentindo hoje?"):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Refletindo..."):
            resposta = ask_gemini(f"Atue como um mentor samurai. O usuario disse: '{prompt}'. Responda de forma sabia, empatica e curta.")
            st.markdown(resposta)
            
    st.session_state.chat_messages.append({"role": "assistant", "content": resposta})
