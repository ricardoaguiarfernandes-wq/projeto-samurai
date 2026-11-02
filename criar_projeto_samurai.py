"""
criar_projeto_samurai.py — V2.2 (Fixes Críticos + PDF + Notícias + Marmita Global)

ENTREGAS:
1. FIX (00_Home.py): Trata o erro da tabela user_stats (cria se não existir).
2. FIX (01_Corpo.py): Adiciona o import de query_one.
3. FIX (11_Alimentacao.py): Move o seletor de marmita para o topo (global).
4. NEW (02_Mente.py): Implementa o leitor e resumidor de PDF de verdade.
5. FIX (03_Informacao.py): Permite gerar o Brief mesmo sem newsletters.

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

def scan_stage_secrets() -> list[str]:
    problemas = []
    r = _git_run_safe(["diff", "--cached", "--name-only"])
    for f in (r.stdout or "").splitlines():
        f = f.strip()
        if not f: continue
        if Path(f).name in {".env", "config.json", "secrets.toml"} or f in {".streamlit/secrets.toml", ".streamlit/config.toml"}:
            problemas.append(f"Arquivo sensível: {f}")
    r = _git_run_safe(["diff", "--cached", "--unified=0"])
    for linha in (r.stdout or "").splitlines():
        if not linha.startswith("+") or linha.startswith("+++"): continue
        if re.search(r"postgres(?:ql)?://[^:]+:[^@\s]+@", linha):
            problemas.append(f"URL Postgres no diff: {linha[:80]}")
    return problemas

def read(p: Path) -> str: return p.read_text(encoding="utf-8")
def write_validated(p: Path, content: str) -> None:
    if p.suffix == ".py":
        try: ast.parse(content, filename=str(p))
        except SyntaxError as e:
            print(f"[ABORTA] Sintaxe quebrada em {p}: {e}"); sys.exit(1)
    p.write_text(content, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")

# ============================================================
# 1. HOME (Tratar banco e XP)
# ============================================================
def fix_home_db() -> None:
    p = BASE / "ui" / "pages" / "00_Home.py"
    txt = read(p)
    if "CREATE TABLE IF NOT EXISTS user_stats" in txt:
        print("[SKIP] 00_Home.py — tabela user_stats já tratada.")
        return

    old_stats = '''# --- GAMIFICAÇÃO ---
stats = query_one("SELECT xp FROM user_stats WHERE id = 1") or {"xp": 0}'''
    new_stats = '''# --- GAMIFICAÇÃO ---
try:
    stats = query_one("SELECT xp FROM user_stats WHERE id = 1") or {"xp": 0}
except Exception:
    execute("CREATE TABLE IF NOT EXISTS user_stats (id INTEGER PRIMARY KEY, xp INTEGER NOT NULL DEFAULT 0, level INTEGER NOT NULL DEFAULT 1)")
    execute("INSERT INTO user_stats (id, xp, level) VALUES (1, 0, 1)")
    stats = {"xp": 0}'''

    if old_stats in txt:
        txt = txt.replace(old_stats, new_stats, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 00_Home.py — bloco de gamificação não encontrado.")

# ============================================================
# 2. CORPO (Import query_one)
# ============================================================
def fix_corpo_import() -> None:
    p = BASE / "ui" / "pages" / "01_Corpo.py"
    txt = read(p)
    if "from core.database import execute, query_all, query_one" in txt:
        print("[SKIP] 01_Corpo.py — import já correto.")
        return

    old_imp = "from core.database import execute, query_all"
    new_imp = "from core.database import execute, query_all, query_one"
    if old_imp in txt:
        txt = txt.replace(old_imp, new_imp, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 01_Corpo.py — import não encontrado.")

# ============================================================
# 3. ALIMENTAÇÃO (Marmita Global)
# ============================================================
def fix_alimentacao_global() -> None:
    p = BASE / "ui" / "pages" / "11_Alimentacao.py"
    txt = read(p)

    if "st.radio(\"Destino da refeição:\"" in txt:
        print("[SKIP] 11_Alimentacao.py — seletor global já existe.")
        return

    # Move o seletor para o topo
    old_title = 'st.title("🍏 Alimentação")\nst.caption("Nutrição hipercalórica para Ectomorfos.")'
    new_title = '''st.title("🍏 Alimentação")
st.caption("Nutrição hipercalórica para Ectomorfos.")

tipo_refeicao = st.radio("Destino da refeição:", ["Para agora (Na hora)", "Para marmita (Dura +3 dias)"], horizontal=True)'''

    if old_title in txt:
        txt = txt.replace(old_title, new_title, 1)

    # Remove o seletor de dentro do Chef
    old_chef = 'st.subheader("🤖 Chef Samurai (Criar Nova Receita)")\ntipo_refeicao = st.radio("O destino desta refeição é:", ["Para agora (Na hora)", "Para marmita (Dura +3 dias)"], horizontal=True)'
    new_chef = 'st.subheader("🤖 Chef Samurai (Criar Nova Receita)")'
    if old_chef in txt:
        txt = txt.replace(old_chef, new_chef, 1)

    # Atualiza o prompt do Chef
    old_prompt = 'prompt = f"Crie uma receita hipercalórica para {ref}. O formato é: {tipo_refeicao}. Ingredientes: {ing}. Se for marmita, foque em ingredientes que aguentam dias na geladeira e expliquem como armazenar. Formate com Ingredientes, Preparo e Por que é bom para ectomorfos."'
    new_prompt = 'prompt = f"Crie uma receita hipercalórica para {ref}. O destino é: {tipo_refeicao}. Ingredientes: {ing}. Se for marmita, foque em ingredientes que aguentam dias na geladeira e expliquem como armazenar. Formate com Ingredientes, Preparo e Por que é bom para ectomorfos."'
    if old_prompt in txt:
        txt = txt.replace(old_prompt, new_prompt, 1)

    write_validated(p, txt)

# ============================================================
# 4. MENTE (Leitor de PDF)
# ============================================================
def fix_mente_pdf() -> None:
    p = BASE / "ui" / "pages" / "02_Mente.py"
    txt = read(p)

    if "fitz.open" in txt:
        print("[SKIP] 02_Mente.py — leitor de PDF já existe.")
        return

    old_leitura = '''with tab_leitura:
    st.write("Função de PDF mantida.")'''

    new_leitura = '''with tab_leitura:
    st.write("Faça o upload de um livro em PDF para extrair o texto e gerar um resumo com a IA.")
    uploaded_file = st.file_uploader("Envie seu PDF", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("📚 Extrair Texto e Resumir com IA", use_container_width=True):
            with st.spinner("Lendo e processando PDF (pode demorar um pouco)..."):
                try:
                    import fitz
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    
                    if text.strip():
                        prompt = f"Atue como um estudioso e mentor. Resuma os principais pontos do seguinte texto extraído de um livro:\\n\\n{text[:20000]}"
                        resumo = ask_gemini(prompt)
                        st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Resumo do Livro</div><div style="white-space: pre-wrap;">{resumo}</div></div>', unsafe_allow_html=True)
                    else:
                        st.warning("O PDF não contém texto legível (pode ser apenas imagens escaneadas).")
                except ImportError:
                    st.error("A biblioteca 'pymupdf' não está instalada. Rode: pip install pymupdf")
                except Exception as e:
                    st.error(f"Erro ao ler o PDF: {e}")'''

    if old_leitura in txt:
        txt = txt.replace(old_leitura, new_leitura, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 02_Mente.py — bloco de leitura não encontrado.")

# ============================================================
# 5. INFORMAÇÃO (Fix Botão de Notícias)
# ============================================================
def fix_informacao_layout() -> None:
    p = BASE / "ui" / "pages" / "03_Informacao.py"
    txt = read(p)

    if "if not emails:\n        st.info(\"Nenhuma newsletter recebida ainda. (O webhook aguarda e-mails).\")" in txt:
        print("[SKIP] 03_Informacao.py — layout já corrigido.")
        return

    old_news = '''with tab_newsletter:
    emails = query_all("SELECT * FROM newsletters_inbox ORDER BY received_at DESC LIMIT 5")
    if not emails:
        st.info("Nenhuma newsletter recebida ainda.")
    else:
        if st.button("📰 Gerar 'The Samurai Brief' do Dia (IA)", use_container_width=True):
            with st.spinner("Resumindo newsletters..."):
                from bs4 import BeautifulSoup
                texto = ""
                for e in emails[:3]:
                    soup = BeautifulSoup(e['content'], "html.parser")
                    texto += f"--- {e['subject']} ---\\n{soup.get_text(strip=True)}\\n"
                prompt = f"Atue como editor da newsletter The Hustle. Resuma os pontos principais:\\n{texto}"
                resumo = ask_gemini(prompt)
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Edição de Hoje</div><div style="white-space: pre-wrap;">{resumo}</div></div>""", unsafe_allow_html=True)
        
        for e in emails:
            with st.expander(f"✉️ {e['subject']}"):
                st.markdown(f"<div style='max-height: 400px; overflow-y: auto;'>{e['content']}</div>", unsafe_allow_html=True)'''

    new_news = '''with tab_newsletter:
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

    if old_news in txt:
        txt = txt.replace(old_news, new_news, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 03_Informacao.py — bloco de newsletter não encontrado (pode ter strings diferentes).")

# ============================================================
# SYNC GIT
# ============================================================
def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    
    problemas = scan_stage_secrets()
    if problemas:
        print("\n[ABORTA] SEGREDOS DETECTADOS:")
        for p_ in problemas: print(f"  X {p_}")
        _git_run_safe(["reset"])
        sys.exit(1)
    print("[OK] Varredura de segredos: limpa")

    msg = "fix: resolve erros de db local, implementa pdf, layout de news e marmita global"
    _git_run_safe(["commit", "-m", msg])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

# ============================================================
# MAIN
# ============================================================
def aplicar() -> None:
    print("=" * 60)
    print("V2.2 — FIXES CRÍTICOS + PDF + NOTÍCIAS + MARMITA GLOBAL")
    print("=" * 60)

    etapas = [
        ("Corrigir DB na Home (00_Home.py)", fix_home_db),
        ("Corrigir import no Corpo (01_Corpo.py)", fix_corpo_import),
        ("Marmita global (11_Alimentacao.py)", fix_alimentacao_global),
        ("Implementar leitor de PDF (02_Mente.py)", fix_mente_pdf),
        ("Corrigir layout de notícias (03_Informacao.py)", fix_informacao_layout),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. A página Home deve carregar sem o erro do SQLite.")
    print("2. Em Corpo, o formulário de peso deve funcionar normalmente.")
    print("3. Em Alimentação, o seletor de Na hora/Marmita agora fica no topo.")
    print("4. Em Mente, você já pode fazer upload de PDFs de verdade.")
    print("5. Em Informação, o botão de gerar Brief já vai aparecer mesmo sem e-mails.")

if __name__ == "__main__":
    aplicar()