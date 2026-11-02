"""
criar_projeto_samurai.py — V2.4 (Salvar Brief no DB e Exibir no Streamlit)

ENTREGAS:
1. DB: Cria a tabela 'daily_briefs' para guardar o texto gerado pela IA.
2. API: Altera o endpoint /api/brief para fazer INSERT na tabela antes de retornar.
3. UI: Altera a página Informação para ler da tabela 'daily_briefs'.
4. UI: Mantém a caixa de entrada de e-mails brutos (opcional) separada.

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
# 1. SCHEMA — Tabela daily_briefs
# ============================================================
def fix_schema_briefs() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)
    if "daily_briefs" in txt:
        print("[SKIP] schema.py — daily_briefs já existe.")
        return
    
    marker = '"""CREATE TABLE IF NOT EXISTS patrimony_fixed_income (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, rate TEXT);""",'
    nova_linha = marker + '\n        """CREATE TABLE IF NOT EXISTS daily_briefs (id INTEGER PRIMARY KEY AUTOINCREMENT, brief_date TEXT NOT NULL UNIQUE, content TEXT NOT NULL);""",'
    
    if marker in txt:
        txt = txt.replace(marker, nova_linha, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] schema.py — marcador não encontrado.")

# ============================================================
# 2. API — Salvar o Brief no DB
# ============================================================
def fix_api_save_brief() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "INSERT INTO daily_briefs" in txt:
        print("[SKIP] api_samurai.py — já salva o brief no DB.")
        return

    # Onde o brief é retornado
    old_return = '''    brief["text"] = txt
    return brief'''

    new_return = '''    brief["text"] = txt
    
    # Salva no banco para aparecer no Streamlit
    try:
        execute(
            "INSERT INTO daily_briefs (brief_date, content) VALUES (?, ?) ON CONFLICT(brief_date) DO UPDATE SET content=excluded.content",
            (today_iso, txt)
        )
    except Exception as e:
        print(f"Erro ao salvar brief no banco: {e}")

    return brief'''

    if old_return in txt:
        txt = txt.replace(old_return, new_return, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] api_samurai.py — bloco de retorno do brief não encontrado.")

# ============================================================
# 3. UI INFORMAÇÃO — Ler da tabela daily_briefs
# ============================================================
def fix_ui_informacao_briefs() -> None:
    p = BASE / "ui" / "pages" / "03_Informacao.py"
    txt = read(p)

    if "daily_briefs" in txt:
        print("[SKIP] 03_Informacao.py — já lê os briefs.")
        return

    # Substitui toda a aba de newsletter
    old_tab = '''with tab_newsletter:
    emails = query_all("SELECT * FROM newsletters_inbox ORDER BY received_at DESC LIMIT 5")
    
    if st.button("📰 Gerar 'The Samurai Brief' do Dia (IA)", use_container_width=True):
        with st.spinner("Lendo notícias e gerando o Brief..."):
            from bs4 import BeautifulSoup
            texto = ""
            for e in emails[:3]:
                soup = BeautifulSoup(e['content'], "html.parser")
                texto += f"--- {e['subject']} ---\\n{soup.get_text(strip=True)}\\n"
            
            if not texto:
                texto = "Nenhuma newsletter importada. Crie um brief baseado nas principais notícias do dia (finanças, tecnologia, geopolítica)."
                
            prompt = f"Atue como editor da newsletter The Hustle. Resuma os pontos principais:\\n{texto}"
            resumo = ask_gemini(prompt)
            st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Edição de Hoje</div><div style="white-space: pre-wrap;">{resumo}</div></div>""", unsafe_allow_html=True)
            
    if not emails:
        st.info("Nenhuma newsletter recebida ainda. O botão acima gerará um brief com notícias gerais.")
    else:
        for e in emails:
            with st.expander(f"✉️ {e['subject']}"):
                st.markdown(f"<div style='max-height: 400px; overflow-y: auto;'>{e['content']}</div>", unsafe_allow_html=True)'''

    new_tab = '''with tab_newsletter:
    st.subheader("📜 Histórico do Samurai Brief")
    briefs = query_all("SELECT * FROM daily_briefs ORDER BY brief_date DESC LIMIT 7")
    
    if not briefs:
        st.info("Nenhum Brief gerado ainda. O Telegram deve enviar o primeiro amanhã às 6h.")
    else:
        for b in briefs:
            with st.expander(f"📅 Brief de {b['brief_date']}"):
                st.markdown(f'<div class="samurai-card" style="border-left-color: #8B0000;"><div style="white-space: pre-wrap;">{b["content"]}</div></div>', unsafe_allow_html=True)

    st.divider()
    st.subheader("📥 Caixa de Entrada (E-mails Brutos)")
    emails = query_all("SELECT * FROM newsletters_inbox ORDER BY received_at DESC LIMIT 5")
    if not emails:
        st.caption("Nenhum e-mail recebido via Power Automate.")
    else:
        for e in emails:
            with st.expander(f"✉️ {e['subject']}"):
                st.markdown(f"<div style='max-height: 300px; overflow-y: auto;'>{e['content']}</div>", unsafe_allow_html=True)'''

    if old_tab in txt:
        txt = txt.replace(old_tab, new_tab, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 03_Informacao.py — bloco da aba de newsletter não encontrado.")

# ============================================================
# SYNC GIT
# ============================================================
def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: salva daily brief no banco e exibe historico no streamlit"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído! O Render e o Streamlit vão atualizar em instantes.")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

# ============================================================
# MAIN
# ============================================================
def aplicar() -> None:
    print("=" * 60)
    print("V2.4 — SALVAR BRIEF NO BANCO E EXIBIR NO STREAMLIT")
    print("=" * 60)

    etapas = [
        ("Criar tabela daily_briefs (schema.py)", fix_schema_briefs),
        ("Salvar brief no DB via API (api_samurai.py)", fix_api_save_brief),
        ("Exibir histórico no Streamlit (03_Informacao.py)", fix_ui_informacao_briefs),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que fazer agora:")
    print("1. O Render vai atualizar (pode demorar 2 min).")
    print("2. Para testar, force o envio de um brief manualmente clicando em 'Run workflow' no GitHub Actions.")
    print("3. Depois que o robô do GitHub terminar, recarregue a aba Informação no Streamlit.")
    print("4. O seu Brief aparecerá no histórico!")

if __name__ == "__main__":
    aplicar()