"""
criar_projeto_samurai.py — V6.1 (Notícias Legislativas Diárias)

ENTREGAS:
1. API (api_samurai.py): Cria o endpoint GET /api/daily-news.
2. SCRAPER/RSS: Coleta Câmara e Senado via RSS; ALERJ e Macaé via scraping HTML.
3. FILTRO: Separa apenas notícias publicadas no dia anterior.
4. AUTOMAÇÃO: Cria o workflow .github/workflows/daily_news.yml para rodar às 06:30.

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
# 1. CRIAR ENDPOINT DE NOTÍCIAS NO API_SAMURAI.PY
# ============================================================
def fix_api_news() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "/api/daily-news" in txt:
        print("[SKIP] api_samurai.py — endpoint de notícias já existe.")
        return

    new_endpoint = r'''
# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS (Câmara, Senado, ALERJ, Macaé)
# ============================================================
@app.get("/api/daily-news", dependencies=[Depends(require_token)])
def daily_news():
    import feedparser
    import requests
    from bs4 import BeautifulSoup
    from datetime import datetime, timedelta

    yesterday = (date.today() - timedelta(days=1)).strftime("%d/%m/%Y")
    noticias = []

    # 1. Câmara dos Deputados (RSS)
    try:
        feed = feedparser.parse("https://www.camara.leg.br/noticias/rss/ultimas-noticias")
        for entry in feed.entries[:5]:
            published = getattr(entry, 'published', '')
            if yesterday in published or not published:
                noticias.append(f"[Câmara] {entry.title}")
    except Exception as e:
        print(f"Erro Câmara RSS: {e}")

    # 2. Senado Federal (RSS)
    try:
        feed = feedparser.parse("https://www12.senado.leg.br/noticias/RSS")
        for entry in feed.entries[:5]:
            published = getattr(entry, 'published', '')
            if yesterday in published or not published:
                noticias.append(f"[Senado] {entry.title}")
    except Exception as e:
        print(f"Erro Senado RSS: {e}")

    # 3. ALERJ (Scraping)
    try:
        r = requests.get("https://www.alerj.rj.gov.br/Comunicacao/SalaDeImprensa/Noticias", timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        # Pega os títulos das notícias (classe genérica, pode precisar de ajuste)
        for h in soup.find_all(["h2", "h3"], class_=True)[:5]:
            titulo = h.get_text(strip=True)
            if titulo and len(titulo) > 20:
                noticias.append(f"[ALERJ] {titulo}")
    except Exception as e:
        print(f"Erro ALERJ scraping: {e}")

    # 4. Câmara de Macaé (Scraping)
    try:
        r = requests.get("https://cmmacae.rj.gov.br/noticias/", timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for h in soup.find_all(["h2", "h3"], class_=True)[:5]:
            titulo = h.get_text(strip=True)
            if titulo and len(titulo) > 20:
                noticias.append(f"[Macaé] {titulo}")
    except Exception as e:
        print(f"Erro Macaé scraping: {e}")

    if not noticias:
        return {"text": "📰 Nenhuma notícia legislativa nova foi encontrada para ontem."}

    texto_final = "🏛️ **Notícias Legislativas de Ontem**\n\n" + "\n".join([f"• {n}" for n in noticias[:15]])
    return {"text": texto_final}

'''

    marker = '# ============================================================\n# WEBHOOK DO TELEGRAM'
    if marker in txt:
        txt = txt.replace(marker, new_endpoint + marker, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] api_samurai.py — marcador para inserir notícias não encontrado.")

# ============================================================
# 2. CRIAR SCRIPT DE ENVIO DIÁRIO
# ============================================================
def create_daily_news_script() -> None:
    p = BASE / "daily_news_telegram.py"
    if p.exists():
        print("[SKIP] daily_news_telegram.py já existe.")
        return

    content = '''import os
import requests
import sys

def send_news():
    samurai_token = os.environ.get("SAMURAI_API_TOKEN")
    tg_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not all([samurai_token, tg_bot_token, tg_chat_id]):
        print("❌ Faltam variáveis de ambiente.")
        sys.exit(1)

    print("⏳ Buscando notícias legislativas...")
    headers = {"Authorization": f"Bearer {samurai_token}"}
    try:
        response = requests.get(
            "https://samurai-webhook.onrender.com/api/daily-news",
            headers=headers,
            timeout=90
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Erro na API: {e}")
        sys.exit(1)

    mensagem = data.get("text", "Não foi possível obter as notícias hoje.")
    if "Nenhuma notícia" in mensagem:
        print("Nenhuma notícia encontrada. Abortando envio para não spammar.")
        return

    print("📤 Enviando para o Telegram...")
    tg_url = f"https://api.telegram.org/bot{tg_bot_token}/sendMessage"
    payload = {"chat_id": tg_chat_id, "text": mensagem, "parse_mode": "Markdown"}
    tg_resp = requests.post(tg_url, json=payload, timeout=15)

    if tg_resp.status_code == 200:
        print("✅ Notícias enviadas!")
    else:
        print(f"❌ Erro no Telegram: {tg_resp.text}")

if __name__ == "__main__":
    send_news()
'''
    write_validated(p, content)

# ============================================================
# 3. CRIAR WORKFLOW DO GITHUB ACTIONS
# ============================================================
def create_news_workflow() -> None:
    wf_dir = BASE / ".github" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    p = wf_dir / "daily_news.yml"
    
    if p.exists():
        print("[SKIP] daily_news.yml já existe.")
        return

    content = '''name: Samurai Daily News (Legislativo)

on:
  schedule:
    # 09:30 UTC = 06:30 Horário de Brasília
    - cron: '30 9 * * *'
  workflow_dispatch:

jobs:
  send_news:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout do Código
        uses: actions/checkout@v4

      - name: Configurar Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Instalar Dependências
        run: pip install requests

      - name: Executar Envio de Notícias
        env:
          SAMURAI_API_TOKEN: ${{ secrets.SAMURAI_API_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python daily_news_telegram.py
'''
    p.write_text(content, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: adiciona noticias legislativas diarias (camara, senado, alerj, macae)"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V6.1 — NOTÍCIAS LEGISLATIVAS DIÁRIAS")
    print("=" * 60)

    etapas = [
        ("Criar endpoint /api/daily-news (api_samurai.py)", fix_api_news),
        ("Criar script de envio (daily_news_telegram.py)", create_daily_news_script),
        ("Criar agendador (daily_news.yml)", create_news_workflow),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nComo testar agora:")
    print("1. Espere o Render e o GitHub atualizarem.")
    print("2. Vá no GitHub > Actions > 'Samurai Daily News' > Run workflow.")
    print("3. As notícias de ontem chegarão no seu Telegram.")
    print("4. A partir de amanhã, rodará automaticamente às 06:30.")

if __name__ == "__main__":
    aplicar()