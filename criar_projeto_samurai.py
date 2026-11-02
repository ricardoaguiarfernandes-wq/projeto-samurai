"""
criar_projeto_samurai.py — V3.4 (Filosofia Iniciante-Avançado e Foco na Corrida)

ENTREGAS:
1. UI (01_Corpo.py): Atualiza o prompt da IA para focar 100% no treino do dia (se for Corrida, só fala de corrida). Adiciona a filosofia Iniciante -> Avançado.
2. API (api_samurai.py): Atualiza o prompt do Brief Diário com a mesma filosofia e adaptação ao dia de Corrida.

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
# 1. CORPO (Prompt de Treino)
# ============================================================
def fix_corpo_prompt() -> None:
    p = BASE / "ui" / "pages" / "01_Corpo.py"
    txt = read(p)

    if "Filosofia Samurai (Iniciante -> Avançado)" in txt:
        print("[SKIP] 01_Corpo.py — prompt já atualizado.")
        return

    old_prompt = 'prompt = f"Atue como treinador de musculação/calistenia. Aluno ectomorfo. Peso atual: {peso_atual}kg, Gordura: {bf_atual}%. Divisão: {split_salvo}. Foco do Dia: {treino_hoje_nome}. Histórico:\\n{ctx}\\n\\nSugira a ficha de hoje focando em progressão. Seja direto e motivador.\\nIMPORTANTE: No final da sua resposta, adicione um bloco de código JSON contendo APENAS os nomes dos exercícios sugeridos.\\nExemplo:\\n```json\\n{{\\"exercicios\\": [\\"Supino Reto\\", \\"Agachamento Livre\\", \\"Puxada Frontal\\", \\"Rosca Direta\\"]}}\\n```\\nNão escreva nada após o bloco JSON."'

    new_prompt = 'prompt = f"""Atue como o Treinador Samurai. Aluno ectomorfo. Peso: {peso_atual}kg, BF: {bf_atual}%. Divisão atual: {split_salvo}. O Foco do Dia é: {treino_hoje_nome}. Histórico recente:\\n{ctx}\\n\\nFilosofia Samurai (Iniciante -> Avançado): O aluno está no nível INICIANTE. Seu papel é guiá-lo com exercícios e intensidade de iniciante, mas sempre preparando o terreno para o nível AVANÇADO. Foco em evolução constante.\\n\\nREGRAS DO TREINO DE HOJE:\\n1. Se o Foco for "Corrida": Crie um treino de corrida/cardio para iniciantes (ex: intervalos de caminhada e corrida leve). NÃO sugira musculação nesse dia.\\n2. Se o Foco for Musculação (Push/Pull/Legs): Crie a ficha de musculação correspondente.\\n3. Seja direto e motivador.\\n\\nIMPORTANTE: No final da sua resposta, adicione um bloco de código JSON contendo APENAS os nomes dos exercícios sugeridos.\\nExemplo:\\n```json\\n{{\\"exercicios\\": [\\"Corrida Leve\\", \\"Caminhada\\"]}}\\n```\\nNão escreva nada após o bloco JSON."""'

    if old_prompt in txt:
        txt = txt.replace(old_prompt, new_prompt, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 01_Corpo.py — prompt antigo não encontrado. Verifique se há diferenças de aspas.")

# ============================================================
# 2. API BRIEF (Prompt do Telegram)
# ============================================================
def fix_api_brief_prompt() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "Filosofia Samurai:" in txt:
        print("[SKIP] api_samurai.py — prompt já atualizado.")
        return

    old_rules = '''REGRAS ESTRITAS:
- NUNCA use "ou". Crave a escolha.
- Se burnout >= 60, incluir "Descanso e sono" em top_3_priorities.
- O campo "training" DEVE ser exatamente "{treino_hoje}", adaptando apenas a intensidade baseada no burnout.
- Versiculo deve ser real (nao invente referencia nem texto).
- Responda APENAS o JSON. Nada fora do bloco.'''

    new_rules = '''REGRAS ESTRITAS:
- NUNCA use "ou". Crave a escolha.
- Se burnout >= 60, incluir "Descanso e sono" em top_3_priorities.
- O campo "training" DEVE ser exatamente "{treino_hoje}". 
- Filosofia Samurai: O usuário está no nível INICIANTE. O treino recomendado deve ser para iniciantes, com foco em evolução para o nível AVANÇADO.
- Se o treino for "Corrida", foque apenas em dicas de corrida/cardio. NÃO mencione musculação ou dicas de "ectomorfo".
- Versiculo deve ser real (nao invente referencia nem texto).
- Responda APENAS o JSON. Nada fora do bloco.'''

    if old_rules in txt:
        txt = txt.replace(old_rules, new_rules, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] api_samurai.py — regras do prompt não encontradas.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: aplica filosofia iniciante-avancado e foco exclusivo no treino do dia"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V3.4 — FILOSOFIA INICIANTE E FOCO NA CORRIDA")
    print("=" * 60)

    fix_corpo_prompt()
    fix_api_brief_prompt()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit e o Render atualizarem (1-2 min).")
    print("2. Na aba 'Corpo', force uma simulação de dia de Corrida (se hoje não for o 4º dia).")
    print("3. Clique em 'Gerar Ficha de Treino com IA' e veja se a IA foca 100% em corrida para iniciante.")
    print("4. Amanhã, veja se o Brief do Telegram seguiu essa mesma regra.")

if __name__ == "__main__":
    aplicar()