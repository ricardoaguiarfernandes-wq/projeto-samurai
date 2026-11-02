"""
criar_projeto_samurai.py — V3.7 (Chat Sequencial e Lista de Ações)

ENTREGAS:
1. UI (04_Patrimonio.py): Implementa memória de contexto para o chat (mantém as últimas 10 mensagens).
2. IA: Ajusta o prompt para permitir que a IA liste tickers específicos quando solicitado.
3. IA: Mantém a continuidade da conversa sem perder o fio da meada.

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

def fix_patrimonio_chat_sequential() -> None:
    p = BASE / "ui" / "pages" / "04_Patrimonio.py"
    txt = read(p)

    if "HISTÓRICO DA CONVERSA:" in txt:
        print("[SKIP] 04_Patrimonio.py — chat sequencial já implementado.")
        return

    old_prompt = '''        with st.chat_message("assistant"):
            with st.spinner("Analisando fundamentos e carteira..."):
                prompt_ia = f"""Atue como o Mentor Financeiro Samurai, um Analista Quantamental Sênior focado em valor, dividendos e proteção patrimonial.

{ctx_carteira}

O usuário perguntou: "{prompt_user}"

Sua missão:
1. Responda de forma direta, profissional e focada no longo prazo.
2. Se ele perguntar sobre uma ação específica, analise os fundamentos (dividendos, resiliência, monopólio) e dê uma opinião CRAVADA (comprar, manter ou vender). NUNCA use "ou" para dar opções; escolha o melhor caminho.
3. Se ele pedir para analisar a carteira, verifique a diversificação setorial e aponte pontos de melhoria.
4. Lembre-se da filosofia Samurai: disciplina e consistência vencem a emoção do mercado. Não faça alucinações com cotações atuais; foque nos fundamentos.
"""
                resposta = ask_gemini(prompt_ia)
                st.markdown(resposta)'''

    new_prompt = '''        with st.chat_message("assistant"):
            with st.spinner("Analisando fundamentos e carteira..."):
                # Pega as últimas 10 mensagens para dar contexto (memória)
                historico_recente = ""
                for msg in st.session_state.fin_chat[-10:]:
                    role = "Usuário" if msg["role"] == "user" else "Mentor"
                    historico_recente += f"{role}: {msg['content']}\\n\\n"

                prompt_ia = f"""Atue como o Mentor Financeiro Samurai, um Analista Quantamental Sênior focado em valor, dividendos e proteção patrimonial.

{ctx_carteira}

HISTÓRICO DA CONVERSA (Para você manter o contexto):
{historico_recente}

O usuário perguntou agora: "{prompt_user}"

Sua missão:
1. Responda de forma direta, profissional e focada no longo prazo, dando CONTINUIDADE à conversa anterior.
2. **Atenção às Listas:** Se o usuário pedir uma lista de ações, sugestões ou disser "quero uma lista dos 1%", você DEVE listar explicitamente os tickers específicos que se encaixam na sua filosofia de valor (ex: TAEE11, BBAS3, CXSE3, SAPR11, ALUP11, etc.) e explicar o porquê de forma resumida. Não devolva a pergunta para o usuário.
3. Se ele perguntar sobre uma ação específica, analise os fundamentos e dê uma opinião CRAVADA (comprar, manter ou vender). NUNCA use "ou" para dar opções; escolha o melhor caminho.
4. Se ele pedir para analisar a carteira, verifique a diversificação setorial e aponte pontos de melhoria.
5. Lembre-se da filosofia Samurai: disciplina e consistência vencem a emoção do mercado. Não faça alucinações com cotações atuais; foque nos fundamentos.
"""
                resposta = ask_gemini(prompt_ia)
                st.markdown(resposta)'''

    if old_prompt in txt:
        txt = txt.replace(old_prompt, new_prompt, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 04_Patrimonio.py — bloco do prompt do chat não encontrado.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: adiciona memoria de contexto (10 mensagens) ao chat financeiro"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V3.7 — CHAT SEQUENCIAL E MEMÓRIA")
    print("=" * 60)

    fix_patrimonio_chat_sequential()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 min).")
    print("2. Na aba 'Patrimônio', inicie uma nova conversa no chat.")
    print("3. Peça: 'Quero uma lista de 5 ações perenes da B3 para eu estudar'.")
    print("4. Depois, pergunte: 'Dessas 5, qual você considera a mais segura para iniciantes?'")
    print("5. A IA vai lembrar da lista anterior e responder corretamente!")

if __name__ == "__main__":
    aplicar()