"""
criar_projeto_samurai.py — V6.3 (Fix Notícias Vazias)

ENTREGAS:
1. FIX (api_samurai.py): Remove o filtro rígido de data e melhora o scraping do ALERJ/Macaé.

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

    new_endpoint = r'''
# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS
# ============================================================
@app.get("/api/daily-news", dependencies=[Depends(require_token)])
def daily_news():
    import feedparser
    import requests
    from bs4 import BeautifulSoup

    noticias = []

    # 1. Câmara dos Deputados (RSS)
    try:
        feed = feedparser.parse("https://www.camara.leg.br/noticias/rss/ultimas-noticias")
        for entry in feed.entries[:4]:
            noticias.append(f"[Câmara] {entry.title}")
    except Exception as e:
        print(f"Erro Câmara RSS: {e}")

    # 2. Senado Federal (RSS)
    try:
        feed = feedparser.parse("https://www12.senado.leg.br/noticias/RSS")
        for entry in feed.entries[:4]:
            noticias.append(f"[Senado] {entry.title}")
    except Exception as e:
        print(f"Erro Senado RSS: {e}")

    # 3. ALERJ (Scraping)
    try:
        r = requests.get("https://www.alerj.rj.gov.br/Comunicacao/SalaDeImprensa/Noticias", timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        # Procura links que contenham 'Noticia' na URL e tenham texto longo
        for a in soup.find_all("a", href=True):
            if "Noticia" in a["href"] or "noticias" in a["href"]:
                titulo = a.get_text(strip=True)
                if titulo and len(titulo) > 30 and not titulo.startswith("http"):
                    noticias.append(f"[ALERJ] {titulo}")
                    if len([n for n in noticias if "[ALERJ]" in n]) >= 3:
                        break
    except Exception as e:
        print(f"Erro ALERJ scraping: {e}")

    # 4. Câmara de Macaé (Scraping)
    try:
        r = requests.get("https://cmmacae.rj.gov.br/noticias/", timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        # Tenta pegar h2, h3 ou títulos de links
        for h in soup.find_all(["h2", "h3", "h4"]):
            titulo = h.get_text(strip=True)
            if titulo and len(titulo) > 30:
                noticias.append(f"[Macaé] {titulo}")
                if len([n for n in noticias if "[Macaé]" in n]) >= 3:
                    break
    except Exception as e:
        print(f"Erro Macaé scraping: {e}")

    if not noticias:
        return {"text": "📰 Nenhuma notícia encontrada no momento."}

    texto_final = "🏛️ **Notícias Legislativas**\n\n" + "\n".join([f"• {n}" for n in noticias[:12]])
    return {"text": texto_final}

'''

    start_marker = '@app.get("/api/daily-news", dependencies=[Depends(require_token)])'
    end_marker = 'if __name__ == "__main__":'
    
    start_idx = txt.find(start_marker)
    end_idx = txt.find(end_marker)

    if start_idx != -1 and end_idx != -1:
        txt = txt[:start_idx] + new_endpoint + "\n" + txt[end_idx:]
        write_validated(p, txt)
    else:
        print("[ERRO] Marcadores não encontrados para substituição.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "fix(api): melhora raspagem de noticias e remove filtro de data quebrado"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V6.3 — FIX NOTÍCIAS VAZIAS")
    print("=" * 60)

    fix_api_news()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Render atualizar (fique de olho no painel até ficar 'Live').")
    print("2. Vá no GitHub Actions e clique em 'Re-run jobs' na aba 'Samurai Daily News'.")
    print("3. Desta vez, as notícias devem chegar no seu Telegram (mesmo que o site da ALERJ ou Macaé falhem, as da Câmara e Senado vão passar).")

if __name__ == "__main__":
    aplicar()