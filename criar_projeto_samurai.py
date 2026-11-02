"""
criar_projeto_samurai.py — V3.1 (Consolidador de Newsletters do Dia)

ENTREGAS:
1. UI (03_Informacao.py): Adiciona a função de consolidar todas as notícias do dia.
2. IA: Usa um prompt de Editor-Chefe para remover duplicatas e mesclar informações.
3. UI: Exibe o resultado em um card destacado, pronto para leitura.

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

def _git_run_safe(args: list[str]) -> subprocess.CompletedProcess:
    r = subprocess.run(["git"] + args, cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if r.stdout is None: r.stdout = ""
    if r.stderr is None: r.stderr = ""
    return r

def read(p: Path) -> str: return p.read_text(encoding="utf-8")
def write_validated(p: Path, content: str) -> None:
    if p.suffix == ".py":
        try: ast.parse(content, filename=str(p))
        except SyntaxError as e:
            print(f"[ABORTA] Sintaxe quebrada em {p}: {e}"); sys.exit(1)
    p.write_text(content, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")

# ============================================================
# 1. CONSOLIDADOR NA UI DE INFORMAÇÃO
# ============================================================
def fix_informacao_consolidador() -> None:
    p = BASE / "ui" / "pages" / "03_Informacao.py"
    txt = read(p)

    if "Consolidador de Notícias do Dia" in txt:
        print("[SKIP] 03_Informacao.py — consolidador já existe.")
        return

    old_block = '''with tab_newsletter:
    st.subheader("📜 Histórico do Samurai Brief")'''

    new_block = '''with tab_newsletter:
    st.subheader("⚡ Consolidador de Notícias do Dia")
    st.write("A IA vai ler todas as newsletters que chegaram hoje, remover notícias repetidas e unificar as informações em um único resumo.")
    
    if st.button("🧠 Consolidar Notícias de Hoje", use_container_width=True):
        from datetime import date
        hoje = date.today().isoformat()
        
        # Busca todos os e-mails recebidos hoje
        emails_hoje = query_all("SELECT subject, content FROM newsletters_inbox WHERE received_at LIKE ?", (f"{hoje}%",))
        
        if not emails_hoje:
            st.warning("Nenhuma newsletter recebida hoje. O Pipedream precisa capturar algum e-mail primeiro.")
        else:
            with st.spinner(f"Lendo {len(emails_hoje)} newsletter(s) e consolidando com a IA..."):
                # Junta todos os textos
                texto_total = "\\n\\n".join([f"--- NEWSLETTER: {e['subject']} ---\\n{e['content']}" for e in emails_hoje])
                
                prompt = f"""Atue como o Editor-Chefe do 'Samurai Brief', um boletim diário focado em alta performance, negócios, tecnologia e geopolítica.

Abaixo está a matéria-prima bruta de várias newsletters que chegaram hoje.
Sua missão OBRIGATÓRIA:
1. **Desduplicação:** Se duas ou mais newsletters trazem a mesma notícia, REMOVA as repetições.
2. **Enriquecimento:** Se houver informações complementares sobre o mesmo fato, mescle-as em um único parágrafo robusto.
3. **Curadoria:** Descarte fofocas irrelevantes ou notícias que não agregam valor estratégico (ex: celebridades, esportes, entretenimento raso).
4. **Estrutura:** Organize o texto final em tópicos com títulos atraentes (Ex: 🚀 Tech & Inovação, 💼 Negócios, 🌍 Geopolítica, 💡 Curiosidades).
5. **Tom:** Seja direto, ágil, provocativo e informativo (estilo The Hustle).
6. **Formatação:** Use Markdown (negrito, itálico, listas).

Aqui está o conteúdo de hoje:
{texto_total[:30000]}
"""
                resumo_unificado = ask_gemini(prompt)
                st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Samurai Brief Consolidado</div><div style="white-space: pre-wrap;">{resumo_unificado}</div></div>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📜 Histórico do Samurai Brief")'''

    if old_block in txt:
        txt = txt.replace(old_block, new_block, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 03_Informacao.py — bloco da newsletter não encontrado.")

# ============================================================
# SYNC GIT
# ============================================================
def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: adiciona consolidador de newsletters do dia na UI"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

# ============================================================
# MAIN
# ============================================================
def aplicar() -> None:
    print("=" * 60)
    print("V3.1 — CONSOLIDADOR DE NEWSLETTERS")
    print("=" * 60)

    fix_informacao_consolidador()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que fazer agora:")
    print("1. Espere o Streamlit Cloud atualizar (uns 2 minutos).")
    print("2. Vá na aba 'Informação' > 'The Samurai Brief'.")
    print("3. Clique no novo botão '🧠 Consolidar Notícias de Hoje'.")
    print("4. A IA vai pegar todas as newsletters (como a do The Hustle) e transformar em um único texto mastigado e sem repetições!")

if __name__ == "__main__":
    aplicar()