"""
melhoria.py — Aplica melhorias no Projeto Samurai de forma segura.
Nesta versão: Atualiza a página 10_Newsletter.py com IA e BeautifulSoup.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

# =============================================================================
# CONFIG
# =============================================================================
BASE = Path(__file__).resolve().parent
WINDOW_TITLE   = "Projeto Samurai"
INICIAR_BAT    = BASE / "INICIAR.bat"

PADROES_SECRETOS = [
    re.compile(r"AQ\.Ab8RN6[A-Za-z0-9_\-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"postgresql://[^:\s]+:[^@\s]+@"),
]
ARQUIVOS_PROIBIDOS = {"config.json", ".env", "secrets.toml"}
PREFIXO_MD_GERADO = "PROJETO_SAMURAI"

# =============================================================================
# DEFINIÇÃO DA MELHORIA
# =============================================================================
NOVO_CONTEUDO_NEWSLETTER = '''import streamlit as st
import sys
from pathlib import Path
import requests
import feedparser
import readtime
import re
import trafilatura
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.schema import init_db
from core.database import query_all
from services.ai import ask_gemini

init_db()

st.title("⚡ The Samurai Brief")
st.caption("Curadoria diária, sua caixa de entrada e resumos com IA.")

# ==============================================================================
# 1. CAIXA DE ENTRADA (PIPEDREAM / OUTLOOK)
# ==============================================================================
st.subheader("📥 Caixa de Entrada (Newsletters via E-mail)")
emails = query_all("SELECT * FROM newsletters_inbox ORDER BY received_at DESC LIMIT 5")

if not emails:
    st.info("Nenhuma newsletter recebida via Pipedream ainda. Aguarde a próxima!")
else:
    # --- GERADOR DO BRIEF DIÁRIO COM IA ---
    if st.button("📰 Gerar 'The Samurai Brief' do Dia (IA)", use_container_width=True):
        with st.spinner("O Mentor Samurai está lendo suas newsletters e criando o resumo executivo..."):
            # Pega o conteúdo dos 3 e-mails mais recentes e limpa o HTML
            texto_consolidado = ""
            for e in emails[:3]:
                soup = BeautifulSoup(e['content'], "html.parser")
                texto_limpo = soup.get_text(separator="\\n", strip=True)
                texto_consolidado += f"--- NEWSLETTER: {e['subject']} ---\\n{texto_limpo}\\n\\n"
            
            prompt = f"""Atue como um editor chefe de uma newsletter executiva matinal (estilo The Hustle / Morning Brew).
Eu vou te fornecer o texto de várias newsletters que recebi hoje. 
Sua missão é resumir os pontos MAIS IMPORTANTES (tecnologia, negócios, finanças) em um único texto curto, empolgante e direto (máximo 4 parágrafos).
Use tópicos com negrito para facilitar a leitura.

Aqui estão as newsletters de hoje:
{texto_consolidado}
"""
            resumo_brief = ask_gemini(prompt)
            
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #F9A825; margin-bottom: 20px;">
                    <div class="titulo" style="color: #F9A825; font-size: 1.1rem;">📰 Edição de Hoje</div>
                    <div style="color: #F2F2F2; font-size: 1rem; line-height: 1.6; margin-top: 10px;">{resumo_brief}</div>
                </div>""",
                unsafe_allow_html=True
            )
    st.divider()

    # --- EXIBIÇÃO DOS E-MAILS INDIVIDUAIS ---
    for e in emails:
        with st.expander(f"✉️ {e['subject']} (De: {e['sender']})"):
            st.markdown(f"**Recebido em:** {e['received_at']}")
            st.markdown("---")
            
            st.markdown(
                f"""<div style="max-height: 400px; overflow-y: auto; background-color: #1F1F1F; padding: 15px; border-radius: 8px;">
                    {e['content']}
                </div>""",
                unsafe_allow_html=True
            )

st.divider()

# ==============================================================================
# 2. LEITURA DE NOTÍCIAS (RSS)
# ==============================================================================
st.subheader("📰 Notícias do Dia (RSS em tempo real)")

FEEDS = {
    "💻 TechCrunch": "https://techcrunch.com/feed/",
    "📈 InfoMoney": "https://www.infomoney.com.br/feed/"
}

def extrair_texto_artigo(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            texto = trafilatura.extract(downloaded)
            return texto if texto else ""
    except Exception:
        pass
    return ""

@st.cache_data(ttl=3600, show_spinner=False)
def buscar_noticias():
    artigos = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    urls_para_baixar = []
    
    for fonte, url in FEEDS.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:2]:
                resumo = entry.get('summary', '')
                resumo_limpo = re.sub('<[^<]+?>', '', resumo).strip()
                artigos.append({
                    "fonte": fonte, "titulo": entry.title, "link": entry.link,
                    "resumo": resumo_limpo[:200] + "...", "texto_completo": ""
                })
                urls_para_baixar.append(entry.link)
        except Exception:
            pass

    with st.spinner("Extraindo o texto completo..."):
        with ThreadPoolExecutor(max_workers=5) as executor:
            resultados = list(executor.map(extrair_texto_artigo, urls_para_baixar))
            
    for i, texto in enumerate(resultados):
        artigos[i]["texto_completo"] = texto if texto else "Texto indisponível."
        base_tempo = texto if texto else artigos[i]["resumo"]
        artigos[i]["tempo"] = readtime.of_text(base_tempo).text

    return artigos

if st.button("🔄 Atualizar Notícias (RSS)", use_container_width=True):
    st.cache_data.clear()

with st.spinner("Lendo os feeds..."):
    artigos = buscar_noticias()

for fonte in FEEDS.keys():
    noticias_fonte = [a for a in artigos if a["fonte"] == fonte]
    if noticias_fonte:
        st.markdown(f"**{fonte}**")
        for noticia in noticias_fonte:
            st.markdown(
                f"""<div class="samurai-card" style="border-left-color: #8B0000; padding: 10px;">
                    <div style="display: flex; justify-content: space-between;">
                        <div><b>{noticia['titulo']}</b></div>
                        <div style="background: #171717; padding: 2px 8px; border-radius: 5px; border: 1px solid #8B0000;">⏱️ {noticia['tempo']}</div>
                    </div>
                    <div style="color: #CCC; font-size: 0.85rem; margin-top: 5px;">{noticia['resumo']}</div>
                </div>""",
                unsafe_allow_html=True
            )
            with st.expander("📖 Ler Artigo Completo"):
                st.markdown(noticia['texto_completo'].replace("\\n", "<br><br>"), unsafe_allow_html=True)
'''

# =============================================================================
# HELPERS
# =============================================================================
def _run(cmd, timeout=120):
    try:
        r = subprocess.run(
            cmd, cwd=BASE, capture_output=True, text=True, 
            encoding="utf-8", errors="replace", timeout=timeout
        )
        out = r.stdout if r.stdout else ""
        err = r.stderr if r.stderr else ""
        return r.returncode, (out + err).strip()
    except Exception as e:
        return 1, str(e)

def _verificar_stage():
    _, out = _run(["git", "diff", "--cached", "--name-only"])
    staged = [l for l in out.splitlines() if l.strip()]
    problemas = []
    for rel in staged:
        nome = Path(rel).name
        if nome in ARQUIVOS_PROIBIDOS:
            problemas.append(f"  - {rel} (arquivo sensivel)")
            continue
        if nome.startswith(PREFIXO_MD_GERADO) and nome.endswith(".md"):
            try:
                conteudo = (BASE / rel).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                conteudo = ""
            for pat in PADROES_SECRETOS:
                if pat.search(conteudo):
                    problemas.append(f"  - {rel} (contem segredo)")
                    break
    if problemas:
        raise RuntimeError("🚨 PUSH BLOQUEADO — segredos no stage:\n" + "\n".join(problemas))

# =============================================================================
# EXECUÇÃO
# =============================================================================
def aplicar_melhoria():
    print("=" * 60)
    print("⚔️  APLICANDO MELHORIA: SAMURAI BRIEF IA")
    print("=" * 60)

    arquivo_alvo = BASE / "ui" / "pages" / "10_Newsletter.py"

    # 1. Validação de Sintaxe (AST)
    try:
        ast.parse(NOVO_CONTEUDO_NEWSLETTER)
        print("[OK] Sintaxe do novo código validada com sucesso.")
    except SyntaxError as e:
        print(f"[ERRO] Falha na validação de sintaxe: {e}")
        sys.exit(1)

    # 2. Escrita
    if arquivo_alvo.exists() and "The Samurai Brief" in arquivo_alvo.read_text(encoding="utf-8"):
        print("[SKIP] A melhoria já foi aplicada anteriormente.")
    else:
        arquivo_alvo.write_text(NOVO_CONTEUDO_NEWSLETTER, encoding="utf-8")
        print(f"[OK] Arquivo atualizado: {arquivo_alvo.name}")

    # 3. Sincronização com GitHub
    print("\n☁️  SINCRONIZANDO COM O SERVIDOR (GitHub)")
    _run(["git", "add", "-A"])
    _run(["git", "rm", "--cached", "PROJETO_SAMURAI*.md"])
    
    try:
        _verificar_stage()
    except RuntimeError as e:
        _run(["git", "reset"])
        print(e)
        sys.exit(1)

    code, out = _run(["git", "commit", "-m", "Feat: Adiciona 'The Samurai Brief' com IA na Newsletter"])
    if code != 0 and "nothing to commit" not in out:
        print(f"[ERRO] Commit falhou: {out}")
        sys.exit(1)
    
    print("[OK] Commit realizado.")
    _run(["git", "pull", "origin", "main", "--rebase", "--no-edit"])
    
    code, out = _run(["git", "push", "origin", "main"])
    if code != 0:
        print(f"[ERRO] Push falhou: {out}")
        sys.exit(1)
    
    print("[OK] Push para GitHub concluido. Streamlit Cloud vai atualizar.")
    print("=" * 60)

if __name__ == "__main__":
    aplicar_melhoria()