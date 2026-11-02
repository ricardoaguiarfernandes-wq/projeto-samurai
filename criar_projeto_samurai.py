"""
criar_projeto_samurai.py — V3.2 (Treino Automático Baseado na Rotação)

ENTREGAS:
1. UI (01_Corpo.py): Remove o selectbox de "Divisão de Treino".
2. LÓGICA: Lê a divisão salva no banco, calcula o dia da rotação e mostra o treino exato.
3. EXERCÍCIOS: Puxa automaticamente os exercícios corretos para o treino do dia.

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

def fix_corpo_automatico() -> None:
    p = BASE / "ui" / "pages" / "01_Corpo.py"
    txt = read(p)

    if "Foco do Dia" in txt:
        print("[SKIP] 01_Corpo.py — treino automático já configurado.")
        return

    # O bloco antigo que vai do selectbox até a definição dos exercícios padrão
    old_block = '''# --- TREINO ---
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

st.subheader(f"🥋 Treino de Hoje: {divisao}")'''

    new_block = '''# --- TREINO AUTOMÁTICO ---
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
    EXERCICIOS_PADRAO = ["Flexão de Braço", "Agachamento", "Barra Fixa", "Prancha (segundos)"]'''

    if old_block in txt:
        txt = txt.replace(old_block, new_block, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 01_Corpo.py — bloco antigo de treino não encontrado.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: treino automatico puxando rotacao salva no banco"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V3.2 — TREINO AUTOMÁTICO")
    print("=" * 60)

    fix_corpo_automatico()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar.")
    print("2. Abra a aba 'Corpo'.")
    print("3. O selectbox sumiu! Ele agora mostra um aviso verde com o 'Foco do Dia' calculado.")
    print("4. A lista de exercícios (Flexão, Agachamento, etc) já vem preenchida com o treino correto.")

if __name__ == "__main__":
    aplicar()