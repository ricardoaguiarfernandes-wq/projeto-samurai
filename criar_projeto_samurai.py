"""
criar_projeto_samurai.py — V6.4 (Força Deploy no Render e Corrige Notícias)

ENTREGAS:
1. FIX (Notícias): Melhora a raspagem da Câmara e Senado.
2. DEPLOY FORÇADO: O script agora lê o seu .env.render e dispara o Deploy Hook automaticamente após o git push.

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
import os
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
# 1. CORREÇÃO DAS NOTÍCIAS
# ============================================================
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
        print("[AVISO] api_samurai.py — rota de notícias já pode estar atualizada.")

# ============================================================
# 2. DISPARAR DEPLOY NO RENDER
# ============================================================
def force_render_deploy():
    print("\n🚀 FORÇANDO DEPLOY NO RENDER...")
    
    # Tenta pegar a URL do hook
    hook_url = os.environ.get("RENDER_DEPLOY_HOOK_URL")
    
    if not hook_url:
        # Se não estiver nas variáveis de ambiente, tenta ler do .env.render
        env_file = BASE / ".env.render"
        if env_file.exists():
            for line in read(env_file).splitlines():
                if line.startswith("RENDER_DEPLOY_HOOK_URL="):
                    hook_url = line.split("=", 1)[1].strip()
                    break
                    
    if not hook_url:
        print("[AVISO] RENDER_DEPLOY_HOOK_URL não encontrada. O Render não será reiniciado automaticamente.")
        print("        Vá no painel do Render e clique em 'Manual Deploy'.")
        return

    try:
        import requests
        response = requests.get(hook_url, timeout=15)
        if response.status_code in [200, 201]:
            print("[OK] Deploy disparado com sucesso no Render! Aguarde 2 minutos.")
        else:
            print(f"[AVISO] O Render respondeu com status {response.status_code}.")
    except Exception as e:
        print(f"[ERRO] Falha ao contatar o Render: {e}")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "fix: forca deploy no render e melhora raspagem de noticias"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído!")
        # Chama a função de deploy após o push dar certo
        force_render_deploy()
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V6.4 — FORÇAR DEPLOY NO RENDER")
    print("=" * 60)

    fix_api_news()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que fazer agora:")
    print("1. Espere cerca de 2 minutos (o Render está reiniciando agora via API).")
    print("2. Vá no GitHub Actions e clique em 'Re-run jobs' (na aba Samurai Daily News).")
    print("3. As notícias devem chegar no seu Telegram.")

if __name__ == "__main__":
    aplicar()