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
from core.schema import init_db
from services.ai import ask_gemini

init_db()

st.title("📖 Bíblia, Inglês & Filosofia")
st.caption("Seu centro de fortalecimento espiritual e aprendizado de idiomas.")

# Inicializa o plano de leitura caso o banco esteja vazio
count_prog = query_one("SELECT COUNT(*) AS c FROM reading_progress")["c"]
if count_prog == 0:
    with st.spinner("Iniciando o plano de leitura..."):
        for day in range(1, 366):
            execute("INSERT INTO reading_progress (day, completed) VALUES (?, 0)", (day,))
    st.rerun()

# Cria as 4 abas
tab1, tab2, tab3, tab4 = st.tabs([
    "📖 Plano Anual (Português)", 
    "🇺🇸 Devocional Bilíngue", 
    "🎵 Inglês com Louvores", 
    "🔑 Palavras-Chave (1.500 Versículos)"
])

# ==============================================================================
# ABA 1: PLANO ANUAL DE LEITURA
# ==============================================================================
with tab1:
    proximo = query_one("SELECT day FROM reading_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")
    
    if not proximo:
        st.success("🎉 Parabéns! Você concluiu a leitura da Bíblia em 1 ano!")
        st.balloons()
    else:
        day = proximo["day"]
        st.subheader(f"Dia {day} de 365")

        plano = query_one("SELECT start_verse_id, end_verse_id FROM reading_plan WHERE day = ?", (day,))
        if plano:
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
                    if st.button("✅ Concluir Leitura de Hoje", use_container_width=True):
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

                st.divider()
                st.subheader("🇺🇸 Aprender Inglês com a Palavra")
                if st.button("🪄 Traduzir e Explicar em Inglês", use_container_width=True):
                    with st.spinner("Preparando aula de inglês..."):
                        prompt = f"Atue como professor de inglês cristão. Baseado no versículo: '{texto_bruto}'. Forneça: 1. Tradução para o inglês; 2. Três palavras-chave (com pronúncia e significado); 3. Explicação gramatical; 4. Frase motivacional em inglês. Seja didático."
                        st.session_state["aula_ingles"] = ask_gemini(prompt)

                if st.session_state.get("aula_ingles"):
                    st.markdown(
                        f"""<div class="samurai-card" style="border-left-color: #2196F3;">
                            <div class="titulo" style="color: #2196F3;">Class is in session</div>
                            <div style="color: #F2F2F2; white-space: pre-wrap;">{st.session_state['aula_ingles']}</div>
                        </div>""", unsafe_allow_html=True
                    )

# ==============================================================================
# ABA 2: DEVOCIONAL BILÍNGUE
# ==============================================================================
with tab2:
    st.header("Devocional Bilíngue Diário")
    st.write("Fortalecendo a fé e os valores bíblicos enquanto praticamos inglês.")
    
    temas_devocionais = ["Amor ao Próximo", "Integridade e Caráter", "Fé em Tempos Difíceis", "Sabedoria e Decisões", "Gratidão e Contentamento"]
    tema = st.selectbox("Escolha o tema do devocional:", temas_devocionais)
    
    if st.button("🪄 Gerar Devocional Bilíngue", use_container_width=True):
        with st.spinner("O Mentor está preparando seu devocional..."):
            prompt = f"""Atue como um mentor cristão bilíngue. Crie um devocional curto sobre o tema "{tema}".
            Estrutura obrigatória:
            1. **Versículo Base (PT/EN):** Um versículo em português e sua tradução em inglês.
            2. **Reflexão (PT):** 1 parágrafo curto sobre como viver e influenciar com valores bíblicos.
            3. **English Practice:** 3 palavras de vocabulário do versículo e uma frase de aplicação em inglês para o usuário treinar.
            Seja acolhedor e direto."""
            
            devocional = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;">
                <div class="titulo">Devocional de Hoje</div>
                <div style="color: #F2F2F2; white-space: pre-wrap; line-height: 1.6;">{devocional}</div>
            </div>""", unsafe_allow_html=True)

# ==============================================================================
# ABA 3: INGLÊS COM LOUVORES
# ==============================================================================
with tab3:
    st.header("Aprenda Inglês com Louvores")
    st.write("Estude o vocabulário e o significado teológico das suas músicas favoritas.")
    
    louvores = ["Because He Lives", "How Great Thou Art", "I Speak Jesus", "Holy Forever"]
    musica = st.selectbox("Escolha um louvor para estudar:", louvores)
    
    if st.button("🎵 Analisar Louvor com IA", use_container_width=True):
        with st.spinner("Analisando a letra e preparando a aula..."):
            prompt = f"""Atue como um professor de inglês e teólogo. Analise o louvor "{musica}".
            Forneça:
            1. **Trecho Principal:** O refrão ou a parte mais famosa da música (em inglês).
            2. **Vocabulário:** 4 palavras-chave da letra com tradução e pronúncia aproximada.
            3. **Teologia:** O que essa música ensina sobre Deus e a fé cristã?
            4. **Grammar Point:** Uma explicação gramatical baseada em uma frase do refrão."""
            
            analise = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;">
                <div class="titulo" style="color: #2196F3;">Aula Musical: {musica}</div>
                <div style="color: #F2F2F2; white-space: pre-wrap; line-height: 1.6;">{analise}</div>
            </div>""", unsafe_allow_html=True)

# ==============================================================================
# ABA 4: PLANO DE PALAVRAS-CHAVE (PROGRESSIVO)
# ==============================================================================
with tab4:
    st.header("Plano de Palavras-Chave (Inglês)")
    st.write("Leia cerca de 1.500 versículos focados nas 50 palavras mais repetidas da Bíblia. Desbloqueie os blocos conforme avança.")
    
    # Simulação de desbloqueio (na prática, você pode salvar o progresso no banco)
    if "bloco_max" not in st.session_state:
        st.session_state["bloco_max"] = 1
        
    blocos = {
        1: "Bloco 1: Fé e Amor (Faith, Love, Hope)",
        2: "Bloco 2: Graça e Paz (Grace, Peace, Joy)",
        3: "Bloco 3: Sabedoria e Luz (Wisdom, Light, Truth)",
    }
    
    bloco_escolhido = st.radio("Selecione o bloco de estudo:", list(blocos.values()))
    
    if st.button("📖 Estudar Versículos do Bloco", use_container_width=True):
        with st.spinner("Buscando e organizando os versículos em inglês..."):
            prompt = f"""Atue como um guia de estudos bíblicos bilíngue. 
            O usuário selecionou: "{bloco_escolhido}".
            Gere uma lista com 3 versículos famosos em inglês (e português) que contenham as palavras-chave deste bloco.
            Para cada versículo, forneça a referência, o texto em inglês, a tradução para o português e uma breve pergunta de reflexão.
            Formate de maneira bonita."""
            
            estudo = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #8B0000;">
                <div class="titulo">{bloco_escolhido}</div>
                <div style="color: #F2F2F2; white-space: pre-wrap; line-height: 1.6;">{estudo}</div>
            </div>""", unsafe_allow_html=True)
            
            # Lógica simples de progressão (apenas visual por enquanto)
            if st.button("✅ Concluir este Bloco e Avançar"):
                st.session_state["bloco_max"] += 1
                st.success("Parabéns! Você desbloqueou o próximo bloco.")
                st.rerun()
