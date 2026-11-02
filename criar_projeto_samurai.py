"""
aplicar_academia.py — Adiciona opção de baixar o áudio do podcast localmente.
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
import time
import os
import tempfile
import streamlit.components.v1 as components

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("💪 Corpo")
st.caption("Treino progressivo com carga, histórico e cronômetro interativo.")
hoje = date.today().isoformat()

# --- RECOMENDADOR E DOWNLOAD DE PODCASTS ---
with st.expander("🎧 Podcasts para o Treino (Recomendação IA + Download)", expanded=False):
    st.write("Escolha um tema e o Mentor sugere 3 opções. Para baixar no seu PC, cole o link do YouTube ou do MP3 abaixo.")
    tema_podcast = st.selectbox("Tema do Podcast:", ["Motivacional e Disciplina", "Filosofia e Reflexão", "Finanças e Negócios", "História e Geopolítica", "Foco e Alta Performance", "Música Épica para Treino"])
    
    if st.button("🎙️ Sugerir 3 Podcasts", use_container_width=True):
        with st.spinner("Buscando recomendações..."):
            prompt = f"Atue como curador. Sugira 3 episódios ou podcasts focados em '{tema_podcast}' para ouvir treinando. Dê o nome, um resumo e por que é bom."
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
                        ydl_opts = {
                            'format': 'bestaudio/best',
                            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
                            'quiet': True,
                            'noplaylist': True,
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': '192',
                            }],
                        }
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(link_podcast, download=True)
                            # Após a conversão, o arquivo estará em mp3
                            mp3_filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
                            mp3_path = os.path.join(tmpdir, mp3_filename)
                            
                            # Lê o arquivo em memória para o botão de download
                            with open(mp3_path, "rb") as f:
                                audio_bytes = f.read()
                            
                            st.success(f"Áudio pronto: {info.get('title', 'Podcast')}")
                            st.download_button(
                                label="💾 Salvar MP3 no Computador",
                                data=audio_bytes,
                                file_name=f"{info.get('title', 'Podcast')}.mp3",
                                mime="audio/mpeg",
                                use_container_width=True
                            )
                else:
                    # Se for um link direto de MP3
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
                st.error(f"Erro ao preparar o download (O FFmpeg está instalado?): {e}")

st.divider()

# --- TREINO ---
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
            if not match: match = re.search(r'\\{.*\\}', resposta_ia, re.DOTALL)
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
"""

def _run(cmd):
    subprocess.run(cmd, cwd=BASE, capture_output=True)

def aplicar():
    print("=" * 60)
    print("⚔️  ADICIONANDO DOWNLOAD DE PODCAST E CORRIGINDO LAYOUT")
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
    _run(["git", "commit", "-m", "Feat: Download de podcasts via YouTube/MP3"])
    _run(["git", "push", "origin", "main"])
    print("[OK] Push concluído. O Streamlit vai atualizar em instantes.")
    print("=" * 60)

if __name__ == "__main__":
    aplicar()