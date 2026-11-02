"""
criar_projeto_samurai.py — V8.3 (Gráfico de Constância Anual e Year in Review)

ENTREGAS:
1. UI (00_Home.py): Adiciona o Heatmap (quadradinhos) de constância dos últimos 365 dias.
2. UI (00_Home.py): Adiciona o "Year in Review" (resumo macro de hábitos, treinos e XP).
3. LÓGICA: Conta hábitos diários para pintar o gráfico de acordo com a intensidade.

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
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

def fix_home_heatmap() -> None:
    p = BASE / "ui" / "pages" / "00_Home.py"
    txt = read(p)

    if "Heatmap de Constância" in txt:
        print("[SKIP] 00_Home.py — heatmap já implementado.")
        return

    # Marcador onde vamos injetar o Heatmap (depois do card de Gamificação/XP)
    marker = 'st.caption(f"Hoje é {dia_pt}, {date.today().strftime(\'%d/%m/%Y\')}")'
    
    heatmap_code = r'''st.caption(f"Hoje é {dia_pt}, {date.today().strftime('%d/%m/%Y')}")

# --- HEATMAP DE CONSTÂNCIA (ESTILO GITHUB) ---
import datetime
import pandas as pd

st.divider()
st.subheader("🔥 Heatmap de Constância")
st.caption("Cada quadrado é um dia. A cor representa quantos hábitos você cumpriu.")

# Pega os hábitos dos últimos 365 dias
hoje = date.today()
um_ano_atras = hoje - datetime.timedelta(days=364)
logs = query_all(
    "SELECT log_date, COUNT(*) as total FROM habit_logs WHERE done = 1 AND log_date >= ? GROUP BY log_date",
    (um_ano_atras.isoformat(),)
)
dados_habitos = {r["log_date"]: int(r["total"]) for r in logs}

# Gera os dias
dias = []
for i in range(365):
    dia_atual = um_ano_atras + datetime.timedelta(days=i)
    qtd = dados_habitos.get(dia_atual.isoformat(), 0)
    dias.append({"data": dia_atual, "count": qtd})

df_heatmap = pd.DataFrame(dias)
df_heatmap["semana"] = df_heatmap["data"].dt.isocalendar().week
df_heatmap["dia_semana"] = df_heatmap["data"].dt.weekday
df_heatmap["mes"] = df_heatmap["data"].dt.month

def get_color(count):
    if count == 0: return "#171717" # Vazio
    if count <= 2: return "#5C0000" # Pouco
    if count <= 5: return "#8B0000" # Médio
    if count <= 8: return "#B22222" # Bom
    return "#FF4444" # Excelente

# Constrói o HTML do Heatmap
html = '<div style="display: flex; gap: 3px; overflow-x: auto; padding-bottom: 10px;">'
for week in sorted(df_heatmap["semana"].unique()):
    html += '<div style="display: flex; flex-direction: column; gap: 3px;">'
    semana_df = df_heatmap[df_heatmap["semana"] == week]
    # Preenche dias faltantes no início da semana
    for i in range(7):
        dia = semana_df[semana_df["dia_semana"] == i]
        if not dia.empty:
            row = dia.iloc[0]
            cor = get_color(row["count"])
            data_str = row["data"].strftime("%d/%m/%Y")
            html += f'<div title="{data_str}: {row["count"]} hábitos" style="width: 12px; height: 12px; background-color: {cor}; border-radius: 2px;"></div>'
        else:
            html += '<div style="width: 12px; height: 12px;"></div>'
    html += '</div>'
html += '</div>'

st.markdown(html, unsafe_allow_html=True)

# Legenda
st.markdown("""
<div style="display: flex; align-items: center; gap: 5px; font-size: 0.8rem; color: #CCC; margin-top: -10px;">
    <span>Menos</span>
    <div style="width: 10px; height: 10px; background-color: #171717; border-radius: 2px;"></div>
    <div style="width: 10px; height: 10px; background-color: #5C0000; border-radius: 2px;"></div>
    <div style="width: 10px; height: 10px; background-color: #8B0000; border-radius: 2px;"></div>
    <div style="width: 10px; height: 10px; background-color: #B22222; border-radius: 2px;"></div>
    <div style="width: 10px; height: 10px; background-color: #FF4444; border-radius: 2px;"></div>
    <span>Mais</span>
</div>
""", unsafe_allow_html=True)

# --- YEAR IN REVIEW ---
st.divider()
st.subheader("📊 Resumo do Ano")

col_a, col_b, col_c = st.columns(3)

# Totais
total_habitos = sum(dados_habitos.values())
total_treinos = query_one("SELECT COUNT(DISTINCT log_date) AS c FROM exercise_logs WHERE log_date >= ?", (um_ano_atras.isoformat(),))
total_treinos = total_treinos["c"] if total_treinos else 0
total_flashcards = query_one("SELECT COUNT(*) AS c FROM flashcards")
total_flashcards = total_flashcards["c"] if total_flashcards else 0

with col_a:
    st.metric("Hábitos Cumpridos", total_habitos)
with col_b:
    st.metric("Dias de Treino", total_treinos)
with col_c:
    st.metric("Flashcards Criados", total_flashcards)
'''

    if marker in txt:
        txt = txt.replace(marker, heatmap_code, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 00_Home.py — marcador de data não encontrado.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: adiciona heatmap anual de constancia e year in review"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V8.3 — HEATMAP ANUAL E YEAR IN REVIEW")
    print("=" * 60)

    fix_home_heatmap()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 min).")
    print("2. Vá para a aba '🏯 Dojo' (Home).")
    print("3. Role a tela para baixo e veja o seu Heatmap de Constância. Ele vai estar meio vazio agora, mas vai começar a ficar vermelho conforme você usa o sistema.")
    print("4. Confira também o Resumo do Ano com os seus totais.")

if __name__ == "__main__":
    aplicar()