"""
criar_projeto_samurai.py — V5.2 (Dashboard de Correlação e Diagnóstico IA)

ENTREGAS:
1. UI (07_Consistencia.py): Adiciona uma nova seção de "Correlação de Performance".
2. LÓGICA: Usa Pandas para cruzar dados de sono, energia e hábitos dos últimos 30 dias.
3. IA: Cria o botão "Diagnóstico de Performance" para a IA analisar os gráficos e gerar insights acionáveis.

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

def _git_run_safe(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)

def read(p: Path) -> str: return p.read_text(encoding="utf-8")
def write_validated(p: Path, content: str) -> None:
    if p.suffix == ".py":
        try: ast.parse(content, filename=str(p))
        except SyntaxError as e:
            print(f"[ABORTA] Sintaxe quebrada em {p}: {e}"); sys.exit(1)
    p.write_text(content, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")

def fix_consistencia_correlation() -> None:
    p = BASE / "ui" / "pages" / "07_Consistencia.py"
    txt = read(p)

    if "Correlação de Performance" in txt:
        print("[SKIP] 07_Consistencia.py — correlação já implementada.")
        return

    # Marcador onde vamos injetar o código (antes do exportar relatório)
    marker = 'st.divider()\nst.subheader("📄 Exportar Relatório")'
    
    new_section = r'''st.divider()
st.subheader("📊 Correlação de Performance (30 dias)")
st.write("O Samurai cruzou seus dados para descobrir o que mais impacta a sua consistência.")

# Busca dados dos últimos 30 dias
from datetime import timedelta
import pandas as pd
import plotly.express as px

thirty_days_ago = (today - timedelta(days=30)).isoformat()

# Dados de Check-in
checkins_30d = query_all("SELECT checkin_date, energy, sleep_hours, stress FROM daily_checkins WHERE checkin_date >= ?", (thirty_days_ago,))

# Dados de Hábitos (quantos foram concluídos por dia)
habits_30d = query_all("SELECT log_date, COUNT(*) as habits_done FROM habit_logs WHERE done = 1 AND log_date >= ? GROUP BY log_date", (thirty_days_ago,))

if len(checkins_30d) < 5 or len(habits_30d) < 5:
    st.info("ℹ️ Dados insuficientes para gerar correlações precisas. Continue fazendo check-ins e marcando hábitos por pelo menos 5 dias.")
else:
    df_check = pd.DataFrame(checkins_30d)
    df_habits = pd.DataFrame(habits_30d)
    
    # Converte colunas numéricas para float (evita erro de string no Postgres)
    for col in ['energy', 'sleep_hours', 'stress']:
        df_check[col] = pd.to_numeric(df_check[col], errors='coerce').fillna(0)
    df_habits['habits_done'] = pd.to_numeric(df_habits['habits_done'], errors='coerce').fillna(0)

    # Faz o merge das duas tabelas pela data
    df_merged = pd.merge(df_check, df_habits, left_on='checkin_date', right_on='log_date', how='left').fillna(0)
    
    # Calcula a matriz de correlação (apenas colunas numéricas)
    df_corr = df_merged[['sleep_hours', 'energy', 'stress', 'habits_done']].corr()

    # Desenha o heatmap
    fig_corr = px.imshow(
        df_corr, 
        text_auto=".2f", 
        aspect="auto", 
        color_continuous_scale=['#F44336', '#171717', '#4CAF50'],
        labels=dict(color="Correlação")
    )
    fig_corr.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='#F2F2F2'),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    if st.button("🧠 Gerar Diagnóstico de Performance com IA", use_container_width=True):
        with st.spinner("Analisando suas correlações e traçando insights..."):
            # Prepara um resumo dos dados para a IA
            corr_sono = df_corr.loc['sleep_hours', 'habits_done']
            corr_energia = df_corr.loc['energy', 'habits_done']
            corr_estresse = df_corr.loc['stress', 'habits_done']
            
            prompt = f"""Atue como um Cientista de Dados e Mentor de Alta Performance.
Aqui estão as correlações dos últimos 30 dias do usuário:
- Sono vs Conclusão de Hábitos: {corr_sono:.2f}
- Energia vs Conclusão de Hábitos: {corr_energia:.2f}
- Estresse vs Conclusão de Hábitos: {corr_estresse:.2f}

Legenda: 1.0 é correlação positiva perfeita, -1.0 é negativa perfeita, 0 é neutro.

Sua missão:
1. Explique o que esses números significam na prática para a vida do usuário (sem usar jargão matemático complexo).
2. Dê 2 ações práticas baseadas nesses dados (ex: se sono tem correlação alta com hábitos, mande ele priorizar o sono).
3. Mantenha o tom de Mentor Samurai: direto, motivador e focado em evolução.

Responda em até 3 parágrafos."""

            diagnostico = ask_gemini(prompt)
            st.markdown(f'<div class="samurai-card" style="border-left-color: #2196F3;"><div class="titulo">Diagnóstico do Mentor</div><div style="white-space: pre-wrap;">{diagnostico}</div></div>', unsafe_allow_html=True)

st.divider()
st.subheader("📄 Exportar Relatório")'''

    if marker in txt:
        txt = txt.replace(marker, new_section, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 07_Consistencia.py — marcador para correlação não encontrado.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: adiciona dashboard de correlacao de habitos e diagnostico com ia"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V5.2 — CORRELAÇÃO DE HÁBITOS E DIAGNÓSTICO IA")
    print("=" * 60)

    fix_consistencia_correlation()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 min).")
    print("2. Vá para a aba 'Consistência'.")
    print("3. Role até o final e veja o novo gráfico de calor (Heatmap).")
    print("4. Clique em 'Gerar Diagnóstico de Performance com IA'.")
    print("5. A IA vai ler os dados do gráfico e te dar insights exclusivos sobre a sua rotina!")

if __name__ == "__main__":
    aplicar()