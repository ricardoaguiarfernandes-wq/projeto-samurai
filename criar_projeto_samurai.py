"""
criar_projeto_samurai.py — V9.2 (Leitura Diária em 30 Dias)

ENTREGAS:
1. FIX (12_Filosofia.py): Altera a divisão do texto. Em vez de dividir por "Capítulos", divide o texto total em 30 partes iguais.
2. UI: Atualiza os botões e títulos para refletirem a métrica de "Dias" (Dia 1 de 30, etc).

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

def update_filosofia_page() -> None:
    p = BASE / "ui" / "pages" / "12_Filosofia.py"
    txt = read(p)

    if "def divide_em_30_dias" in txt:
        print("[SKIP] 12_Filosofia.py — leitura de 30 dias já implementada.")
        return

    # Substitui a função show_book_tab inteira
    import re
    pattern = re.compile(r"def show_book_tab\(filename, book_name\):.*?(?=with tab_gp:)", re.DOTALL)
    
    nova_funcao = '''def divide_em_30_dias(texto):
    """Divide o texto em exatamente 30 partes proporcionais, cortando nos espaços."""
    total_caracteres = len(texto)
    chars_por_dia = total_caracteres // 30
    partes = []
    inicio = 0
    
    for i in range(30):
        if i == 29: # O último dia pega todo o resto
            fim = total_caracteres
        else:
            fim = inicio + chars_por_dia
            # Avança até o próximo espaço para não cortar palavras
            while fim < total_caracteres and not texto[fim].isspace():
                fim += 1
                
        partes.append(texto[inicio:fim].strip())
        inicio = fim
        
    return partes

def show_book_tab(filename, book_name):
    filepath = ASSETS_DIR / filename
    if not filepath.exists():
        st.error(f"Arquivo {filename} não encontrado na pasta assets.")
        return

    text = filepath.read_text(encoding="utf-8")
    
    # Usa a nova divisão por volume de texto
    dias = divide_em_30_dias(text)
    
    state_key = f"idx_{filename}"
    if state_key not in st.session_state:
        st.session_state[state_key] = 0

    idx = st.session_state[state_key]
    if idx >= len(dias):
        idx = 0
        st.session_state[state_key] = 0

    st.subheader(f"📖 {book_name} — Dia {idx+1} de 30")
    
    # Área de Leitura
    with st.expander("Ler o texto base de hoje", expanded=True):
        display_text = dias[idx]
        st.markdown(f"<div style='white-space: pre-wrap; line-height: 1.6;'>{display_text}</div>", unsafe_allow_html=True)

    # Navegação
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Dia Anterior", key=f"prev_{filename}", use_container_width=True):
        st.session_state[state_key] = max(0, idx - 1)
        st.rerun()
    if col2.button("Próximo Dia ➡️", key=f"next_{filename}", use_container_width=True):
        st.session_state[state_key] = min(len(dias) - 1, idx + 1)
        st.rerun()

    st.divider()
    
    # Aula com IA
    st.write("#### 🎓 Aula do Mentor")
    if st.button("🧠 Gerar Aula Prática com IA", key=f"ia_{filename}", use_container_width=True):
        with st.spinner("O Mentor está preparando sua aula diária..."):
            prompt = f"""Atue como o mestre e mentor Felipe Alves, ensinando os conceitos dos seus livros.
O usuário está estudando o livro '{book_name}', no dia {idx+1} de 30.
Aqui está o trecho da leitura de hoje:
{dias[idx][:6000]}

Sua missão:
1. Crie 3 tópicos de reflexão sobre o texto (explicando o conceito de forma clara).
2. Crie 1 exercício prático para o usuário aplicar HOJE na vida real (ex: "Hoje, observe a postura das pessoas no elevador", "Ao conversar com alguém, faça a pausa de 2 segundos antes de responder").
3. Dê uma frase de impacto final, estilo Samurai.
Seja direto, empolgante e prático.
"""
            resposta = ask_gemini(prompt)
            st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Aula do Dia {idx+1}</div><div style="white-space: pre-wrap;">{resposta}</div></div>', unsafe_allow_html=True)

'''

    if pattern.search(txt):
        txt = pattern.sub(nova_funcao, txt, count=1)
        write_validated(p, txt)
    else:
        print("[ERRO] 12_Filosofia.py — função show_book_tab não encontrada.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: divide leitura dos grimorios em 30 dias por volume de texto"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V9.2 — LEITURA DIÁRIA EM 30 DIAS")
    print("=" * 60)

    update_filosofia_page()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Streamlit atualizar.")
    print("2. Vá em 'Filosofia' > 'Grimório Proibido'.")
    print("3. O título mudou para 'Dia X de 30'.")
    print("4. Os botões agora avançam a leitura baseados na quantidade de texto, cortando sempre no espaço para não quebrar palavras.")

if __name__ == "__main__":
    aplicar()