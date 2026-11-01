import streamlit as st
import sys
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db

init_db()

st.title("🕊️ Religião")
st.caption("Cultivando a fé e a conexão com Deus.")

hoje = date.today().isoformat()

# --- HÁBITOS RELIGIOSOS ---
st.subheader("🙏 Práticas Espirituais")

habits = query_all(
    """
    SELECT h.id, h.name, COALESCE(l.done, 0) AS done
    FROM habits h
    LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ?
    WHERE h.pillar = 'Religião' AND h.active = 1
    ORDER BY h.name
    """,
    (hoje,),
)

alterou = False
for h in habits:
    novo = st.checkbox(h["name"], value=bool(h["done"]), key=f"rel_{h['id']}")
    if novo != bool(h["done"]):
        execute(
            """
            INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
            """,
            (h["id"], hoje, 1 if novo else 0),
        )
        alterou = True

if alterou:
    st.rerun()

st.divider()

# --- VERSÍCULO DO DIA ---
st.subheader("📖 Versículo do Dia")

VERSICULOS = [
    ("Salmos 23:1", "O Senhor é o meu pastor; nada me faltará."),
    ("Filipenses 4:13", "Posso todas as coisas naquele que me fortalece."),
    ("Josué 1:9", "Sê forte e corajoso; não temas, nem te espantes, porque o Senhor, teu Deus, é contigo."),
    ("Provérbios 3:5", "Confia no Senhor de todo o teu coração e não te estribes no teu próprio entendimento."),
    ("Isaías 41:10", "Não temas, porque eu sou contigo; não te assombres, porque eu sou o teu Deus."),
    ("Salmos 119:105", "Lâmpada para os meus pés é tua palavra e luz, para o meu caminho."),
    ("Romanos 8:28", "E sabemos que todas as coisas contribuem juntamente para o bem daqueles que amam a Deus."),
]

# Escolhe o versículo baseado no dia do ano
v = VERSICULOS[date.today().toordinal() % len(VERSICULOS)]

st.markdown(
    f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-top: 15px;">
        <div class="titulo">{v[0]}</div>
        <div class="valor" style="font-size: 1.1rem; font-style: italic; color: #F2F2F2;">"{v[1]}"</div>
    </div>""",
    unsafe_allow_html=True,
)

st.divider()
st.subheader("✍️ Diário Espiritual")

with st.form("form_diario_espiritual"):
    texto = st.text_area("O que Deus falou com você hoje?", placeholder="Escreva uma oração, um agradecimento ou um aprendizado...")
    submitted = st.form_submit_button("Salvar no Diário", use_container_width=True)

if submitted and texto.strip():
    execute(
        "INSERT INTO journal_entries (entry_date, prompt, content) VALUES (?, ?, ?)",
        (date.today().isoformat(), "Diário Espiritual", texto.strip())
    )
    st.success("Registro salvo.")
    st.rerun()
