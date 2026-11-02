"""
criar_projeto_samurai.py — V3.5 (Chat com Analista Financeiro)

ENTREGAS:
1. UI (04_Patrimonio.py): Adiciona a aba "💬 Chat com Analista".
2. LÓGICA: Injeta a carteira atual do usuário no contexto da conversa.
3. IA: Prompt focado em análise quantamental, dividendos e alocação.

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

def fix_patrimonio_chat() -> None:
    p = BASE / "ui" / "pages" / "04_Patrimonio.py"
    txt = read(p)

    if "Chat com Analista" in txt:
        print("[SKIP] 04_Patrimonio.py — Chat já existe.")
        return

    # 1. Adicionar a nova aba no topo
    old_tabs = 'tab_ia, tab_acoes, tab_rf = st.tabs(["🤖 Consultor Quantamental", "📊 Ações/FIIs", "🏦 Renda Fixa"])'
    new_tabs = 'tab_ia, tab_chat, tab_acoes, tab_rf = st.tabs(["🤖 Consultor Quantamental", "💬 Chat com Analista", "📊 Ações/FIIs", "🏦 Renda Fixa"])'
    
    if old_tabs in txt:
        txt = txt.replace(old_tabs, new_tabs, 1)
    else:
        print("[AVISO] 04_Patrimonio.py — abas não encontradas no formato esperado.")

    # 2. Adicionar o bloco do chat no final do arquivo
    chat_block = '''
# ==============================================================================
# ABA CHAT: Analista Quantamental
# ==============================================================================
with tab_chat:
    st.header("💬 Chat com o Mentor Financeiro")
    st.write("Pergunte sobre ações específicas, dividendos, riscos ou peça conselhos sobre a sua carteira.")
    
    # Pega a carteira atual para dar contexto à IA
    acoes_db = query_all("SELECT * FROM portfolio WHERE ticker NOT LIKE 'RF:%'")
    rf_db = query_all("SELECT * FROM patrimony_fixed_income")
    
    ctx_carteira = "CARTEIRA ATUAL DO USUÁRIO:\\n"
    if acoes_db:
        ctx_carteira += "Ações/FIIs:\\n"
        for a in acoes_db:
            ctx_carteira += f"- {a['ticker']}: {a['quantity']} cotas, Preço Médio R$ {a['average_price']:.2f}\\n"
    else:
        ctx_carteira += "Ações: Carteira vazia.\\n"
        
    if rf_db:
        ctx_carteira += "Renda Fixa:\\n"
        for r in rf_db:
            ctx_carteira += f"- {r['name']}: R$ {r['amount']} ({r['rate']})\\n"
    else:
        ctx_carteira += "Renda Fixa: Carteira vazia.\\n"

    if "fin_chat" not in st.session_state:
        st.session_state.fin_chat = []

    # Exibe o histórico
    for msg in st.session_state.fin_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input do usuário
    if prompt_user := st.chat_input("Ex: Vale a pena comprar CXSE3 agora? Ou: Analise minha carteira."):
        st.session_state.fin_chat.append({"role": "user", "content": prompt_user})
        with st.chat_message("user"):
            st.markdown(prompt_user)

        with st.chat_message("assistant"):
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
                st.markdown(resposta)
                
        st.session_state.fin_chat.append({"role": "assistant", "content": resposta})
'''

    # Anexa o bloco ao final do arquivo
    txt += chat_block
    write_validated(p, txt)

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: adiciona chat com analista financeiro na pagina de patrimonio"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V3.5 — CHAT COM ANALISTA FINANCEIRO")
    print("=" * 60)

    fix_patrimonio_chat()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit Cloud atualizar (1-2 min).")
    print("2. Abra a aba 'Patrimônio' e clique na nova aba '💬 Chat com Analista'.")
    print("3. Pergunte algo como: 'O que você acha da minha carteira atual?' ou 'Quais as vantagens de segurar TAEE11?'")
    print("4. A IA vai ler os dados reais do seu banco e responder como um analista profissional.")

if __name__ == "__main__":
    aplicar()