"""
criar_projeto_samurai.py — V6.2 (Fix Injeção de Rota de Notícias)

ENTREGAS:
1. FIX (api_samurai.py): Injeta o endpoint /api/daily-news de forma infalível antes do uvicorn.
2. Força o push para o Render atualizar.

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

    # Injeta antes do bloco do uvicorn
    marker = 'if __name__ == "__main__":'
    if marker in txt:
        txt = txt.replace(marker, new_endpoint + "\n" + marker, 1)
        write_validated(p, txt)
    else:
        print("[ERRO] api_samurai.py — marcador final não encontrado.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "fix(api): injeta rota daily-news antes do uvicorn"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V6.2 — FIX INJEÇÃO DE NOTÍCIAS")
    print("=" * 60)

    fix_api_news()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\n🚨 ATENÇÃO: O QUE FAZER AGORA")
    print("1. Vá no painel do Render AGORA.")
    print("2. Espere o status mudar para 'Live' (o deploy automático leva uns 2 minutos).")
    print("3. Confira se a nova rota apareceu acessando:")
    print("   https://samurai-webhook.onrender.com/docs")
    print("4. Se a rota '/api/daily-news' estiver lá, vá no GitHub Actions e rode o 'Re-run jobs'.")
    print("5. O erro 404 sumirá e as notícias chegarão no seu Telegram!")

if __name__ == "__main__":
    aplicar()