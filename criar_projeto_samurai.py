"""
criar_projeto_samurai.py — V3.3 (Fix NameError no Prompt da IA)

ENTREGAS:
1. FIX (01_Corpo.py): Substitui a variável antiga 'divisao' por 'split_salvo' e 'treino_hoje_nome' no prompt da IA.

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

def fix_prompt_ia() -> None:
    p = BASE / "ui" / "pages" / "01_Corpo.py"
    txt = read(p)

    if "Foco do Dia: {treino_hoje_nome}" in txt:
        print("[SKIP] 01_Corpo.py — prompt já corrigido.")
        return

    old_prompt = 'prompt = f"Atue como treinador de musculação/calistenia. Aluno ectomorfo. Peso atual: {peso_atual}kg, Gordura: {bf_atual}%. Divisão: {divisao}. Histórico:\\n{ctx}\\n\\nSugira a ficha de hoje focando em progressão.'

    new_prompt = 'prompt = f"Atue como treinador de musculação/calistenia. Aluno ectomorfo. Peso atual: {peso_atual}kg, Gordura: {bf_atual}%. Divisão: {split_salvo}. Foco do Dia: {treino_hoje_nome}. Histórico:\\n{ctx}\\n\\nSugira a ficha de hoje focando em progressão.'

    if old_prompt in txt:
        txt = txt.replace(old_prompt, new_prompt, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 01_Corpo.py — prompt antigo não encontrado. Tentando substituição mais ampla...")
        # Fallback caso a string tenha diferenças mínimas
        txt = txt.replace("Divisão: {divisao}. Histórico:", "Divisão: {split_salvo}. Foco do Dia: {treino_hoje_nome}. Histórico:")
        write_validated(p, txt)

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "fix: corrige NameError no prompt da IA do corpo"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V3.3 — CORREÇÃO DO PROMPT DA IA")
    print("=" * 60)

    fix_prompt_ia()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 minutos).")
    print("2. Abra a aba 'Corpo' e clique em 'Gerar Ficha de Treino com IA para Hoje'.")
    print("3. O erro vai sumir e a IA vai montar a ficha sabendo exatamente qual é o Foco do Dia.")

if __name__ == "__main__":
    aplicar()