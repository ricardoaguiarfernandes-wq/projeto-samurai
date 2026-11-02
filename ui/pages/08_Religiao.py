import streamlit as st
import sys
import io
from pathlib import Path
from datetime import date
from gtts import gTTS

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db, setup_biblia
from services.ai import ask_gemini

init_db()

st.title("🕊️ Religião & Bíblia")
st.caption("Seu centro de fortalecimento espiritual e aprendizado de idiomas.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📖 Plano Anual", 
    "🇺🇸 Devocional Bilíngue", 
    "🎵 Inglês com Louvores", 
    "🔑 Palavras-Chave (1.500)",
    "🙏 Práticas e Oração"
])

# ==============================================================================
# ABA 1: PLANO ANUAL DE LEITURA
# ==============================================================================
with tab1:
    count_prog = query_one("SELECT COUNT(*) AS c FROM reading_progress")["c"]
    if count_prog == 0:
        st.warning("O banco de dados ainda não foi inicializado.")
        if st.button("🔄 Baixar Bíblia e Iniciar Plano", use_container_width=True):
            with st.spinner("Baixando (pode levar 1-2 min)..."):
                setup_biblia()
            st.rerun()
    else:
        # Verifica se o plano está quebrado (Dia 1 com menos de 10 versículos)
        plano_teste = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = 1")
        plano_corrompido = False
        if plano_teste and (plano_teste["end_verse_id"] - plano_teste["start_verse_id"]) < 10:
            plano_corrompido = True

        if plano_corrompido:
            st.error("⚠️ O plano de leitura está desatualizado ou incorreto.")
            if st.button("🛠️ Corrigir Divisão do Plano Agora", use_container_width=True):
                with st.spinner("Corrigindo... (não feche a página)"):
                    execute("DELETE FROM reading_plan")
                    execute("DELETE FROM reading_progress")
                    versiculos = query_all("SELECT id, text FROM bible_verses ORDER BY id")
                    if versiculos:
                        total_palavras = sum(len(v["text"].split()) for v in versiculos)
                        meta = total_palavras / 365
                        day, acc, start = 1, 0, versiculos[0]["id"]
                        for i, v in enumerate(versiculos):
                            acc += len(v["text"].split())
                            if (acc >= meta and day < 365) or i == len(versiculos) - 1:
                                execute("INSERT INTO reading_plan (day, start_verse_id, end_verse_id) VALUES (?, ?, ?)", (day, start, v["id"]))
                                day += 1
                                acc = 0
                                if i < len(versiculos) - 1: start = versiculos[i + 1]["id"]
                        while day <= 365:
                            execute("INSERT INTO reading_plan (day, start_verse_id, end_verse_id) VALUES (?, ?, ?)", (day, start, versiculos[-1]["id"]))
                            day += 1
                        for d in range(1, 366):
                            execute("INSERT INTO reading_progress (day, completed) VALUES (?, 0)", (d,))
                    st.success("Plano corrigido!")
                    st.rerun()
        else:
            proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")
            if not proximo:
                st.success("🎉 Parabéns! Você concluiu a leitura da Bíblia em 1 ano!")
            else:
                day = proximo["day"]
                st.subheader(f"Dia {day} de 365")
                plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
                if plano:
                    versiculos = query_all("SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id", (plano["start_verse_id"], plano["end_verse_id"]))
                    if versiculos:
                        primeiro, ultimo = versiculos[0], versiculos[-1]
                        ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']}"
                        st.markdown(f"**Leitura de hoje:** {ref}")
                        
                        texto_limpo, texto_bruto = "", ""
                        for v in versiculos:
                            safe_text = str(v['text']).replace("{", "{{").replace("}", "}}")
                            texto_limpo += f"**{v['verse']}** {safe_text}  \n"
                            texto_bruto += f"{v['verse']} {v['text']} "
                            
                        st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 300px; overflow-y: auto;"><div style="line-height: 1.8;">{texto_limpo}</div></div>""", unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Concluir Leitura", use_container_width=True):
                                execute("UPDATE reading_progress SET completed = 1 WHERE day = ?", (day,))
                                st.rerun()
                        with col2:
                            if st.button("🔊 Ouvir Áudio (PT)", use_container_width=True):
                                with st.spinner("Gerando áudio..."):
                                    tts = gTTS(text=texto_bruto, lang='pt', slow=False)
                                    fp = io.BytesIO()
                                    tts.write_to_fp(fp)
                                    fp.seek(0)
                                    st.audio(fp.getvalue(), format="audio/mp3")

# ==============================================================================
# ABA 2: DEVOCIONAL BILÍNGUE
# ==============================================================================
with tab2:
    st.header("Devocional Diário Automático")
    temas = ["Amor ao Próximo", "Integridade e Caráter", "Fé em Tempos Difíceis", "Sabedoria e Decisões", "Gratidão e Contentamento"]
    tema_hoje = temas[date.today().toordinal() % len(temas)]
    st.info(f"**Tema de Hoje:** {tema_hoje}")
    
    @st.cache_data(ttl=86400, show_spinner=False)
    def gerar_devocional(tema):
        prompt = f"Atue como um mentor cristão bilíngue. Crie um devocional curto sobre o tema '{tema}'. Estrutura: 1. Versículo Base (PT/EN) 2. Reflexão (PT) 3. English Practice."
        return ask_gemini(prompt)
        
    if st.button("🪄 Gerar Devocional de Hoje", use_container_width=True):
        with st.spinner("Preparando..."):
            dev = gerar_devocional(tema_hoje)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Devocional: {tema_hoje}</div><div style="white-space: pre-wrap;">{dev}</div></div>""", unsafe_allow_html=True)

# ==============================================================================
# ABA 3: INGLÊS COM LOUVORES
# ==============================================================================
with tab3:
    st.header("Aprenda Inglês com Louvores")
    if "louvores" not in st.session_state:
        st.session_state["louvores"] = ["Because He Lives", "How Great Thou Art", "I Speak Jesus", "Holy Forever"]
        
    with st.expander("➕ Adicionar Novo Louvor"):
        nova = st.text_input("Nome da música:")
        if st.button("Adicionar") and nova:
            st.session_state["louvores"].append(nova)
            st.rerun()
            
    musica = st.selectbox("Escolha um louvor:", st.session_state["louvores"])
    if st.button("🎵 Analisar Louvor com IA", use_container_width=True):
        with st.spinner("Analisando..."):
            prompt = f"Atue como professor de inglês e teólogo. Analise o louvor '{musica}'. Forneça: 1. Refrão em inglês; 2. 4 palavras-chave; 3. Teologia da música; 4. Explicação gramatical."
            analise = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;"><div class="titulo">Aula Musical: {musica}</div><div style="white-space: pre-wrap;">{analise}</div></div>""", unsafe_allow_html=True)

# ==============================================================================
# ABA 4: PALAVRAS-CHAVE (1.500 VERSÍCULOS)
# ==============================================================================
with tab4:
    st.header("Plano de Palavras-Chave (Inglês)")
    blocos = {1: "Bloco 1: Fé e Amor", 2: "Bloco 2: Graça e Paz", 3: "Bloco 3: Sabedoria e Luz", 4: "Bloco 4: Força e Coragem", 5: "Bloco 5: Misericórdia e Perdão"}
    bloco_escolhido = st.radio("Selecione o bloco:", list(blocos.values()))
    
    if st.button("📖 Estudar Versículos do Bloco", use_container_width=True):
        with st.spinner("Buscando..."):
            prompt = f"Atue como guia bilíngue. Gere 3 versículos famosos em inglês e PT contendo palavras do bloco '{bloco_escolhido}'. Inclua referência, texto EN, tradução PT e uma pergunta reflexiva."
            estudo = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000;"><div class="titulo">{bloco_escolhido}</div><div style="white-space: pre-wrap;">{estudo}</div></div>""", unsafe_allow_html=True)

# ==============================================================================
# ABA 5: PRÁTICAS E ORAÇÃO
# ==============================================================================
with tab5:
    st.subheader("🙏 Práticas Espirituais")
    habits = query_all("SELECT h.id, h.name, COALESCE(l.done, 0) AS done FROM habits h LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ? WHERE h.pillar = 'Religião' AND h.active = 1", (date.today().isoformat(),))
    alterou_religiao = False
    for h in habits:
        novo = st.checkbox(h["name"], value=bool(h["done"]), key=f"religiao_habit_{h['id']}")
        if novo != bool(h["done"]):
            execute("INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?) ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done", (h["id"], date.today().isoformat(), 1 if novo else 0))
            alterou_religiao = True
    if alterou_religiao:
        st.rerun()
            
    st.divider()
    st.subheader("🙏 Oração do Dia")
    if st.button("Gerar Oração com IA", use_container_width=True):
        st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;">{ask_gemini("Crie uma oração curta e poderosa para o dia de hoje.")}</div>""", unsafe_allow_html=True)
