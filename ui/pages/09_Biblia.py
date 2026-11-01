import streamlit as st
import sys
from pathlib import Path
from gtts import gTTS
import io
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from core.schema import init_db, setup_biblia
from services.ai import ask_gemini

init_db()

st.title("📖 Bíblia, Inglês & Filosofia")

# Inicializa o plano caso esteja vazio
count_prog = query_one("SELECT COUNT(*) AS c FROM reading_progress")["c"]
if count_prog == 0:
    with st.spinner("Iniciando o plano de leitura..."):
        for day in range(1, 366):
            execute("INSERT INTO reading_progress (day, completed) VALUES (?, 0)", (day,))
    st.rerun()

tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Plano Anual", 
    "🇺🇸 Devocional Bilíngue", 
    "🎵 Inglês com Louvores", 
    "🔑 Palavras-Chave (1.500)"
])

# ==============================================================================
# ABA 1: PLANO ANUAL DE LEITURA
# ==============================================================================
with tab1:
    proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")
    
    if not proximo:
        st.success("🎉 Parabéns! Você concluiu a leitura da Bíblia em 1 ano!")
    else:
        day = proximo["day"]
        st.subheader(f"Dia {day} de 365")

        plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
        
        # CORREÇÃO: Se o plano estiver vazio na nuvem, recria na hora
        if not plano:
            st.warning("O plano de leitura não foi gerado corretamente (provavelmente por timeout).")
            if st.button("🔄 Gerar Plano de Leitura Agora", use_container_width=True):
                with st.spinner("Baixando a Bíblia e gerando o plano (pode levar 1-2 min)..."):
                    setup_biblia()
                st.success("Plano gerado com sucesso!")
                st.rerun()
        else:
            versiculos = query_all(
                "SELECT book_name, chapter, verse, text FROM bible_verses WHERE id BETWEEN ? AND ? ORDER BY id",
                (plano["start_verse_id"], plano["end_verse_id"])
            )

            if versiculos:
                primeiro = versiculos[0]
                ref = f"{primeiro['book_name']} {primeiro['chapter']}:{primeiro['verse']}"
                st.markdown(f"**Leitura de hoje:** {ref}")

                texto_limpo, texto_bruto = "", ""
                for v in versiculos:
                    safe_text = str(v['text']).replace("{", "{{").replace("}", "}}")
                    texto_limpo += f"**{v['verse']}** {safe_text}  \n"
                    texto_bruto += f"{v['verse']} {v['text']} "

                st.markdown(
                    f"""<div class="samurai-card" style="border-left-color: #F9A825; max-height: 300px; overflow-y: auto;">
                        <div style="color: #F2F2F2; font-size: 1rem; line-height: 1.8;">{texto_limpo}</div>
                    </div>""", unsafe_allow_html=True
                )

                st.divider()
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
# ABA 2: DEVOCIONAL BILÍNGUE (AUTOMÁTICO)
# ==============================================================================
with tab2:
    st.header("Devocional Diário Automático")
    st.write("Um novo devocional gerado todos os dias para fortalecer sua fé.")
    
    temas = ["Amor ao Próximo", "Integridade e Caráter", "Fé em Tempos Difíceis", "Sabedoria e Decisões", "Gratidão e Contentamento"]
    # Escolhe o tema com base no dia do ano
    tema_hoje = temas[date.today().toordinal() % len(temas)]
    
    st.info(f"**Tema de Hoje:** {tema_hoje}")
    
    @st.cache_data(ttl=86400, show_spinner=False) # Cache de 24h para não gastar API à toa
    def gerar_devocional(tema):
        prompt = f"""Atue como um mentor cristão bilíngue. Crie um devocional curto sobre o tema "{tema}".
        Estrutura: 
        1. Versículo Base (PT/EN)
        2. Reflexão (PT) sobre viver e influenciar com valores bíblicos.
        3. English Practice: 3 palavras do versículo e uma frase de aplicação em inglês."""
        return ask_gemini(prompt)

    if st.button("🪄 Gerar Devocional de Hoje", use_container_width=True):
        with st.spinner("Preparando devocional..."):
            devocional = gerar_devocional(tema_hoje)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;">
                <div class="titulo">Devocional: {tema_hoje}</div>
                <div style="color: #F2F2F2; white-space: pre-wrap;">{devocional}</div>
            </div>""", unsafe_allow_html=True)

# ==============================================================================
# ABA 3: INGLÊS COM LOUVORES (ADICIONAR MÚSICAS)
# ==============================================================================
with tab3:
    st.header("Aprenda Inglês com Louvores")
    
    # Gerenciamento de músicas no session_state
    if "louvores" not in st.session_state:
        st.session_state["louvores"] = ["Because He Lives", "How Great Thou Art", "I Speak Jesus", "Holy Forever"]
        
    with st.expander("➕ Adicionar Novo Louvor"):
        nova_musica = st.text_input("Nome da música:")
        if st.button("Adicionar à Lista") and nova_musica:
            st.session_state["louvores"].append(nova_musica)
            st.rerun()
            
    musica = st.selectbox("Escolha um louvor para estudar:", st.session_state["louvores"])
    
    if st.button("🎵 Analisar Louvor com IA", use_container_width=True):
        with st.spinner("Analisando a letra..."):
            prompt = f"Atue como professor de inglês e teólogo. Analise o louvor '{musica}'. Forneça: 1. Refrão em inglês; 2. 4 palavras-chave; 3. Teologia da música; 4. Explicação gramatical."
            analise = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;">
                <div class="titulo">Aula Musical: {musica}</div>
                <div style="color: #F2F2F2; white-space: pre-wrap;">{analise}</div>
            </div>""", unsafe_allow_html=True)

# ==============================================================================
# ABA 4: PLANO DE PALAVRAS-CHAVE (EXPANDIDO)
# ==============================================================================
with tab4:
    st.header("Plano de Palavras-Chave (Inglês)")
    st.write("Leia cerca de 1.500 versículos focados nas 50 palavras mais repetidas da Bíblia.")
    
    blocos = {
        1: "Bloco 1: Fé e Amor (Faith, Love, Hope)",
        2: "Bloco 2: Graça e Paz (Grace, Peace, Joy)",
        3: "Bloco 3: Sabedoria e Luz (Wisdom, Light, Truth)",
        4: "Bloco 4: Força e Coragem (Strength, Courage, Power)",
        5: "Bloco 5: Misericórdia e Perdão (Mercy, Forgiveness, Redemption)"
    }
    
    bloco_escolhido = st.radio("Selecione o bloco de estudo:", list(blocos.values()))
    
    if st.button("📖 Estudar Versículos do Bloco", use_container_width=True):
        with st.spinner("Buscando versículos..."):
            prompt = f"Atue como guia bilíngue. Gere 3 versículos famosos em inglês (e PT) contendo palavras do bloco '{bloco_escolhido}'. Inclua referência, texto EN, tradução PT e uma pergunta reflexiva."
            estudo = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000;">
                <div class="titulo">{bloco_escolhido}</div>
                <div style="color: #F2F2F2; white-space: pre-wrap;">{estudo}</div>
            </div>""", unsafe_allow_html=True)
