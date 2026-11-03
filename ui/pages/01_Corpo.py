import streamlit as st
import sys
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date
import json
import re
import time
import os
import tempfile
import streamlit.components.v1 as components

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all, query_one
from services.ai import ask_gemini

st.title("💪 Corpo")
st.caption("Treino progressivo com carga, histórico e cronômetro interativo.")

with st.expander("🔄 Rotação de Treino (Usada pela IA do Telegram)", expanded=False):
    st.write("Escolha a sua divisão fixa. O sistema calculará automaticamente qual é o treino de hoje.")
    
    settings = query_one("SELECT workout_split, workout_start_date FROM user_settings WHERE id = 1") or {}
    split_atual = settings.get("workout_split", "Musculação - Push/Pull/Legs + Corrida")
    
    OPCOES_SPLIT = [
        "Musculação - Push/Pull/Legs + Corrida",
        "Musculação - ABC",
        "Calistenia - Full Body",
        "Calistenia - PPL"
    ]
    
    nova_split = st.selectbox("Sua divisão fixa:", OPCOES_SPLIT, index=OPCOES_SPLIT.index(split_atual) if split_atual in OPCOES_SPLIT else 0)
    
    if st.button("Salvar Rotação (Reseta contagem para hoje)", use_container_width=True):
        hoje = date.today().isoformat()
        execute("INSERT INTO user_settings (id, workout_split, workout_start_date) VALUES (1, ?, ?) ON CONFLICT(id) DO UPDATE SET workout_split=excluded.workout_split, workout_start_date=excluded.workout_start_date", (nova_split, hoje))
        st.success("Rotação salva! O próximo treino será o primeiro da lista.")
        st.rerun()

    # Lógica matemática de qual treino é hoje
    if settings and settings.get("workout_start_date"):
        from datetime import datetime
        try:
            start_dt = datetime.strptime(settings["workout_start_date"], "%Y-%m-%d").date()
            dias = (date.today() - start_dt).days
            
            # Define a sequência baseada na escolha
            if "Push/Pull/Legs + Corrida" in split_atual:
                seq = ["Push (Peito, Ombro, Tríceps)", "Legs (Pernas)", "Pull (Costas, Bíceps)", "Corrida (Cardio)"]
            elif "ABC" in split_atual:
                seq = ["A (Peito, Tríceps, Ombro)", "B (Costas, Bíceps)", "C (Pernas)", "Descanso"]
            elif "Calistenia - PPL" in split_atual:
                seq = ["Push", "Pull", "Legs", "Descanso"]
            else:
                seq = ["Full Body", "Descanso"]
                
            treino_hoje = seq[dias % len(seq)]
            st.info(f"📅 **Treino calculado para hoje:** {treino_hoje} (Dia {dias} da rotação)")
        except Exception as e:
            st.warning(f"Erro ao calcular rotação: {e}")
    else:
        st.info("⚠️ Salve a sua rotação acima para que a IA saiba o treino de hoje.")

with st.expander("⚖️ Atualizar Peso e Composição Corporal"):
    with st.form("form_peso"):
        c1, c2 = st.columns(2)
        peso = c1.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
        bf = c2.number_input("Gordura Corporal (%)", min_value=1.0, max_value=50.0, value=15.0, step=0.1)
        if st.form_submit_button("Salvar Medidas", use_container_width=True):
            execute("INSERT INTO body_metrics (log_date, weight, body_fat) VALUES (?, ?, ?) ON CONFLICT(log_date) DO UPDATE SET weight=excluded.weight, body_fat=excluded.body_fat", (date.today().isoformat(), peso, bf))
            st.success("Medidas atualizadas! A IA agora usará esses dados.")
            st.rerun()

# Busca o peso mais recente para a IA
try:
    _metric = query_one("SELECT weight, body_fat FROM body_metrics ORDER BY log_date DESC LIMIT 1")
except Exception:
    # Fallback caso a tabela não exista no SQLite local ainda
    execute("CREATE TABLE IF NOT EXISTS body_metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, log_date TEXT NOT NULL UNIQUE, weight REAL NOT NULL, body_fat REAL, notes TEXT)")
    _metric = None

peso_atual = _metric["weight"] if _metric else 70.0
bf_atual = _metric["body_fat"] if _metric else "N/A"
hoje = date.today().isoformat()

# --- RECOMENDADOR E DOWNLOAD DE PODCASTS ---
with st.expander("🎧 Podcasts para o Treino (Recomendação IA + Download)", expanded=False):
    st.write("Escolha um tema e o Mentor sugere 3 opções com links de busca. Para baixar, clique no link, copie a URL do YouTube e cole abaixo.")
    tema_podcast = st.selectbox("Tema do Podcast:", ["Motivacional e Disciplina", "Filosofia e Reflexão", "Finanças e Negócios", "História e Geopolítica", "Foco e Alta Performance", "Música Épica para Treino"])
    
    if st.button("🎙️ Sugerir 3 Podcasts", use_container_width=True):
        with st.spinner("Buscando recomendações..."):
            prompt = f"Atue como curador de conteúdo. Sugira 3 episódios ou podcasts focados em '{tema_podcast}' para ouvir treinando. Para cada um, forneça: 1. Nome do Podcast e Título do Episódio. 2. Um resumo curto. 3. Por que é bom para treinar. 4. OBRIGATÓRIO: Um link de busca do YouTube para o usuário achar o vídeo. Formate o link exatamente assim (trocando os espaços por +): [🎬 Buscar no YouTube](https://www.youtube.com/results?search_query=Nome+do+Podcast+Titulo+do+Episodio)"
            st.markdown(f'<div class="samurai-card" style="border-left-color: #9C27B0;"><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("**⬇️ Baixar Áudio para o PC**")
    link_podcast = st.text_input("Cole o link do YouTube (vídeo do podcast) ou link direto do MP3:")
    
    if st.button("Preparar Download", use_container_width=True) and link_podcast:
        with st.spinner("Baixando áudio... (Isso pode demorar alguns minutos)"):
            try:
                if "youtube.com" in link_podcast or "youtu.be" in link_podcast:
                    import yt_dlp
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # MUDANÇA AQUI: Baixa o áudio original (m4a) sem precisar do FFmpeg
                        ydl_opts = {
                            'format': 'bestaudio[ext=m4a]/bestaudio',
                            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                            'quiet': True,
                            'noplaylist': True,
                        }
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(link_podcast, download=True)
                            filename = ydl.prepare_filename(info)
                            ext = info.get('ext', 'm4a')
                            
                            with open(filename, "rb") as f:
                                audio_bytes = f.read()
                            
                            st.success(f"Áudio pronto: {info.get('title', 'Podcast')}")
                            st.download_button(
                                label=f"💾 Salvar Áudio ({ext}) no Computador",
                                data=audio_bytes,
                                file_name=f"{info.get('title', 'Podcast')}.{ext}",
                                mime="audio/mp4" if ext == "m4a" else "audio/webm",
                                use_container_width=True
                            )
                else:
                    import requests
                    res = requests.get(link_podcast)
                    if res.status_code == 200:
                        st.download_button(
                            label="💾 Salvar MP3 no Computador",
                            data=res.content,
                            file_name="podcast.mp3",
                            mime="audio/mpeg",
                            use_container_width=True
                        )
                    else:
                        st.error("Falha ao baixar o MP3. Verifique o link.")
            except Exception as e:
                st.error(f"Erro ao preparar o download: {e}")

st.divider()

# --- TREINO AUTOMÁTICO ---
settings = query_one("SELECT workout_split, workout_start_date FROM user_settings WHERE id = 1")
split_salvo = settings["workout_split"] if settings and settings.get("workout_split") else "Calistenia - Full Body"
start_date = settings.get("workout_start_date") if settings else None

treino_hoje_nome = "Treino Livre"
if start_date:
    from datetime import datetime
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        dias_passados = (date.today() - start_dt).days
        
        if "Push/Pull/Legs + Corrida" in split_salvo:
            seq = ["Push", "Legs", "Pull", "Corrida"]
        elif "ABC" in split_salvo:
            seq = ["A (Peito/Ombro/Tríceps)", "B (Costas/Bíceps)", "C (Pernas)", "Descanso"]
        elif "Calistenia - PPL" in split_salvo:
            seq = ["Push", "Pull", "Legs", "Descanso"]
        else:
            seq = ["Full Body", "Descanso"]
            
        treino_hoje_nome = seq[dias_passados % len(seq)]
    except Exception:
        pass

st.subheader(f"🥋 Treino de Hoje: {split_salvo}")
st.info(f"🎯 **Foco do Dia:** {treino_hoje_nome}")

# Define os exercícios com base no treino do dia
EXERCICIOS_PADRAO = []
if "Calistenia - Full Body" in split_salvo:
    EXERCICIOS_PADRAO = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]
elif "Calistenia - PPL" in split_salvo:
    if treino_hoje_nome == "Push": EXERCICIOS_PADRAO = ["Flexão de Braço", "Desenvolvimento", "Tríceps"]
    elif treino_hoje_nome == "Pull": EXERCICIOS_PADRAO = ["Barra Fixa", "Remada", "Rosca Direta"]
    elif treino_hoje_nome == "Legs": EXERCICIOS_PADRAO = ["Agachamento", "Afundo", "Panturrilha"]
    else: EXERCICIOS_PADRAO = ["Descanso Ativo", "Mobilidade"]
elif "Push/Pull/Legs + Corrida" in split_salvo:
    if treino_hoje_nome == "Push": EXERCICIOS_PADRAO = ["Supino Reto", "Desenvolvimento Militar", "Tríceps Corda", "Crucifixo"]
    elif treino_hoje_nome == "Pull": EXERCICIOS_PADRAO = ["Puxada Frontal", "Remada Baixa", "Rosca Direta", "Rosca Scott"]
    elif treino_hoje_nome == "Legs": EXERCICIOS_PADRAO = ["Agachamento Livre", "Leg Press", "Cadeira Extensora", "Panturrilha em Pé"]
    elif treino_hoje_nome == "Corrida": EXERCICIOS_PADRAO = ["Corrida Leve (30-40 min)", "Alongamento Pós-Corrida"]
    else: EXERCICIOS_PADRAO = ["Descanso Total"]
elif "Musculação - ABC" in split_salvo:
    if "A" in treino_hoje_nome: EXERCICIOS_PADRAO = ["Supino Reto", "Supino Inclinado", "Tríceps Testa", "Elevação Lateral"]
    elif "B" in treino_hoje_nome: EXERCICIOS_PADRAO = ["Puxada Frontal", "Remada Curvada", "Rosca Direta", "Rosca Martelo"]
    elif "C" in treino_hoje_nome: EXERCICIOS_PADRAO = ["Agachamento Livre", "Leg Press", "Cadeira Extensora", "Mesa Flexora"]
    else: EXERCICIOS_PADRAO = ["Descanso Total"]
else:
    EXERCICIOS_PADRAO = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]

if st.button("🤖 Gerar Ficha de Treino com IA para Hoje", use_container_width=True):
    with st.spinner("O Treinador está analisando e preparando a ficha..."):
        hist = query_all("SELECT log_date, exercise_name, reps FROM exercise_logs ORDER BY log_date DESC LIMIT 15")
        ctx = "".join([f"- {h['log_date']}: {h['exercise_name']} - {h['reps']} reps\n" for h in hist])
        prompt = f"""Atue como o Treinador Samurai. Aluno ectomorfo. Peso: {peso_atual}kg, BF: {bf_atual}%. Divisão atual: {split_salvo}. O Foco do Dia é: {treino_hoje_nome}. Histórico recente:\n{ctx}\n\nFilosofia Samurai (Iniciante -> Avançado): O aluno está no nível INICIANTE. Seu papel é guiá-lo com exercícios e intensidade de iniciante, mas sempre preparando o terreno para o nível AVANÇADO. Foco em evolução constante.\n\nREGRAS DO TREINO DE HOJE:\n1. Se o Foco for "Corrida": Crie um treino de corrida/cardio para iniciantes (ex: intervalos de caminhada e corrida leve). NÃO sugira musculação nesse dia.\n2. Se o Foco for Musculação (Push/Pull/Legs): Crie a ficha de musculação correspondente.\n3. Seja direto e motivador.\n\nIMPORTANTE: No final da sua resposta, adicione um bloco de código JSON contendo APENAS os nomes dos exercícios sugeridos.\nExemplo:\n```json\n{{\"exercicios\": [\"Corrida Leve\", \"Caminhada\"]}}\n```\nNão escreva nada após o bloco JSON."""
        resposta_ia = ask_gemini(prompt)
        try:
            match = re.search(r'```json\s*(.*?)\s*```', resposta_ia, re.DOTALL)
            if not match: match = re.search(r'\{.*\}', resposta_ia, re.DOTALL)
            if match:
                json_str = match.group(1) if '```' in match.group(0) else match.group(0)
                data = json.loads(json_str)
                if "exercicios" in data and len(data["exercicios"]) > 0:
                    st.session_state["exercicios_ia"] = data["exercicios"]
                    st.session_state["texto_ia"] = resposta_ia.replace(match.group(0), "").strip()
                    st.success("Ficha gerada! Os exercícios foram atualizados abaixo.")
            else: st.session_state["texto_ia"] = resposta_ia
        except Exception:
            st.session_state["texto_ia"] = resposta_ia
            st.warning("A IA gerou a ficha, mas não foi possível atualizar o formulário automaticamente.")

if st.session_state.get("texto_ia"):
    st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div style="white-space: pre-wrap;">{st.session_state["texto_ia"]}</div></div>', unsafe_allow_html=True)
    if st.button("🔄 Limpar Ficha da IA e voltar ao padrão"):
        if "exercicios_ia" in st.session_state: del st.session_state["exercicios_ia"]
        if "texto_ia" in st.session_state: del st.session_state["texto_ia"]
        st.rerun()

# --- CRONÔMETRO INTERATIVO ---
def start_timer():
    st.session_state["timer_active"] = True
    st.session_state["timer_start"] = time.time()

if st.session_state.get("timer_active"):
    elapsed = time.time() - st.session_state.get("timer_start", 0)
    remain = max(0, 150 - int(elapsed))
    if remain > 0:
        components.html(f'''
            <div id="timer" style="font-size: 48px; color: #8B0000; text-align: center; font-family: sans-serif; font-weight: bold; margin-top: 10px;">{remain//60:02d}:{remain%60:02d}</div>
            <div style="text-align: center; color: #F2F2F2; font-family: sans-serif;">Descanso entre séries...</div>
            <script>
                var timeLeft = {remain};
                var elem = document.getElementById('timer');
                var timerId = setInterval(function() {{
                    if (timeLeft <= 0) {{
                        clearInterval(timerId);
                        elem.innerHTML = "FIM!";
                        elem.style.color = "#4CAF50";
                    }} else {{
                        var m = Math.floor(timeLeft / 60);
                        var s = timeLeft % 60;
                        elem.innerHTML = m + ":" + (s < 10 ? "0" : "") + s;
                        timeLeft--;
                    }}
                }}, 1000);
            </script>
        ''', height=90)
    else:
        st.success("✅ Descanso finalizado! Próxima série.")

st.markdown("### Registrar Execução")

EXERCICIOS_ATUAIS = st.session_state.get("exercicios_ia", EXERCICIOS_PADRAO)
rows = query_all("SELECT exercise_name, notes FROM exercise_logs WHERE log_date = ?", (hoje,))
treinos_hoje = {}
for r in rows:
    try:
        if r["notes"]: treinos_hoje[r["exercise_name"]] = json.loads(r["notes"])
    except: pass

for ex in EXERCICIOS_ATUAIS:
    st.markdown(f"#### {ex}")
    h1, h2, h3 = st.columns([1, 1, 1])
    h1.caption("✅ Feito")
    h2.caption("🔄 Reps")
    h3.caption("🏋️ Carga (kg)")
    
    sets_data = treinos_hoje.get(ex, [])
    if not sets_data:
        sets_data = [{"set": i, "reps": 0, "load": 0, "done": False} for i in range(1, 4)]

    for s in sets_data:
        set_num = s["set"]
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.checkbox(f"Série {set_num}", value=s["done"], key=f"chk_{ex}_{set_num}", on_change=start_timer)
        with c2:
            st.number_input("Reps", min_value=0, value=int(s["reps"]), key=f"reps_{ex}_{set_num}", label_visibility="collapsed")
        with c3:
            st.number_input("Carga", min_value=0, value=int(s["load"]), key=f"carga_{ex}_{set_num}", label_visibility="collapsed")
    st.markdown("---")

if st.button("💾 Salvar Treino Completo", use_container_width=True):
    for ex in EXERCICIOS_ATUAIS:
        sets_data_to_save = []
        total_reps = 0
        total_sets = 0
        for set_num in range(1, 4):
            is_done = st.session_state.get(f"chk_{ex}_{set_num}", False)
            reps = st.session_state.get(f"reps_{ex}_{set_num}", 0)
            load = st.session_state.get(f"carga_{ex}_{set_num}", 0)
            
            if is_done or reps > 0:
                sets_data_to_save.append({"set": set_num, "reps": reps, "load": load, "done": is_done})
                if is_done:
                    total_reps += reps
                    total_sets += 1
                    
        if sets_data_to_save:
            notes_str = json.dumps(sets_data_to_save)
            execute("INSERT INTO exercise_logs (log_date, exercise_name, reps, sets, notes) VALUES (?, ?, ?, ?, ?) ON CONFLICT(log_date, exercise_name) DO UPDATE SET reps=excluded.reps, sets=excluded.sets, notes=excluded.notes", (hoje, ex, total_reps, total_sets, notes_str))
            
    st.success("Treino registrado com sucesso!")
    st.session_state["timer_active"] = False
    time.sleep(1)
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
