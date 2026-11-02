"""
criar_projeto_samurai.py — V4.1 (Módulo de Carreira e Survey)

ENTREGAS:
1. DB: Cria a tabela 'career_missions' para guardar as missões diárias.
2. NAVEGAÇÃO (app.py): Adiciona a nova aba "💼 Carreira" no menu.
3. UI (14_Carreira.py): Interface com IA focada em gerar 3 missões diárias estruturadas (Técnica, Postura, Negócio) para um estagiário de Survey se tornar efetivado como Surveyor Junior.

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

# ============================================================
# 1. DB SCHEMA (Carreira)
# ============================================================
def fix_schema_career() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)
    if "CREATE TABLE IF NOT EXISTS career_missions" in txt:
        print("[SKIP] schema.py — tabela career_missions já existe.")
        return
    
    marker = '"""CREATE TABLE IF NOT EXISTS discipline (id INTEGER PRIMARY KEY, start_date TEXT, longest_streak INTEGER DEFAULT 0);""",'
    nova_linha = marker + '\n        """CREATE TABLE IF NOT EXISTS career_missions (id INTEGER PRIMARY KEY AUTOINCREMENT, mission_date TEXT NOT NULL, task TEXT NOT NULL, completed INTEGER DEFAULT 0);""",'
    
    if marker in txt:
        txt = txt.replace(marker, nova_linha, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] schema.py — marcador de discipline não encontrado.")

# ============================================================
# 2. NAVEGAÇÃO (app.py)
# ============================================================
def fix_app_nav_career() -> None:
    p = BASE / "app.py"
    txt = read(p)
    if "14_Carreira.py" in txt:
        print("[SKIP] app.py — navegação de carreira já existe.")
        return

    old_nav = 'disciplina = st.Page("ui/pages/13_Disciplina.py", title="🛡️ Disciplina")'
    new_nav = old_nav + '\ncarreira = st.Page("ui/pages/14_Carreira.py", title="💼 Carreira")'

    old_dict = '"⚔️ Comando": [home, consistencia, disciplina],'
    new_dict = '"⚔️ Comando": [home, consistencia, disciplina, carreira],'

    if old_nav in txt and old_dict in txt:
        txt = txt.replace(old_nav, new_nav, 1)
        txt = txt.replace(old_dict, new_dict, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] app.py — estrutura de navegação não encontrada.")

# ============================================================
# 3. UI DA PÁGINA DE CARREIRA
# ============================================================
def create_career_page() -> None:
    p = BASE / "ui" / "pages" / "14_Carreira.py"
    if p.exists():
        print("[SKIP] 14_Carreira.py — página já existe.")
        return

    content = '''import streamlit as st
import sys
import json
import re
from datetime import date
from pathlib import Path

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_all
from core.schema import init_db
from services.ai import ask_gemini

init_db()
st.title("💼 Carreira & Profissão")
st.caption("Trilha de evolução: Estagiário de Survey ➔ Surveyor Junior.")

hoje = date.today().isoformat()

# Busca as missões de hoje
missoes = query_all("SELECT id, task, completed FROM career_missions WHERE mission_date = ?", (hoje,))

if not missoes:
    st.info("🎯 Nenhuma missão definida para hoje. O seu Mentor de Carreira está pronto.")
    if st.button("🧠 Gerar Missões de Hoje com IA", use_container_width=True):
        with st.spinner("Traçando estratégia para a sua efetivação..."):
            prompt = """Atue como um Gestor Sênior e Mentor da área de Survey (levantamentos, inspeções, offshore/onshore).
O usuário é estagiário e tem a meta de ser efetivado como Surveyor Junior no início do próximo ano.

Crie 3 missões diárias curtas, práticas e teóricas para o dia de hoje. O foco deve ser:
1. Habilidade Técnica (ex: leitura de dados, equipamentos, normas, softwares).
2. Postura Profissional (ex: comunicação com a equipe, proatividade, relatórios).
3. Visão de Negócio (ex: entender o impacto do survey no projeto).

Sua resposta DEVE ser APENAS um JSON válido com a seguinte estrutura, sem formatação markdown:
{
  "missions": [
    "Missão 1...",
    "Missão 2...",
    "Missão 3..."
  ]
}
"""
            res = ask_gemini(prompt)
            m = re.search(r'\\{.*\\}', res, re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group(0))
                    for task in data.get("missions", []):
                        execute("INSERT INTO career_missions (mission_date, task, completed) VALUES (?, ?, 0)", (hoje, task))
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao processar missões: {e}")
            else:
                st.error("A IA não retornou o formato esperado. Tente novamente.")
else:
    st.subheader("📋 Missões de Hoje")
    alterou = False
    for m in missoes:
        novo = st.checkbox(m["task"], value=bool(m["completed"]), key=f"mission_{m['id']}")
        if novo != bool(m["completed"]):
            execute("UPDATE career_missions SET completed = ? WHERE id = ?", (1 if novo else 0, m["id"]))
            alterou = True
    
    if alterou:
        st.rerun()

    if all(m["completed"] for m in missoes):
        st.success("🏆 Todas as missões concluídas! O Surveyor Junior está cada vez mais perto.")

    st.divider()
    if st.button("🔄 Gerar Novas Missões (Substituir as de hoje)", use_container_width=True):
        execute("DELETE FROM career_missions WHERE mission_date = ?", (hoje,))
        st.rerun()
'''
    write_validated(p, content)

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: cria modulo de carreira com missoes diarias para surveyor junior"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V4.1 — MÓDULO DE CARREIRA (SURVEY)")
    print("=" * 60)

    etapas = [
        ("Criar tabela de missões (schema.py)", fix_schema_career),
        ("Adicionar página no menu (app.py)", fix_app_nav_career),
        ("Criar interface de carreira (14_Carreira.py)", create_career_page),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 min).")
    print("2. No menu esquerdo, clique na nova aba '💼 Carreira'.")
    print("3. Clique em 'Gerar Missões de Hoje com IA'.")
    print("4. A IA vai cuspir 3 missões focadas em te preparar para a efetivação.")
    print("5. Vá marcando conforme for concluindo no seu dia.")

if __name__ == "__main__":
    aplicar()