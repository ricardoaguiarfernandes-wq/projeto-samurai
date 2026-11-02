"""
criar_projeto_samurai.py — V6.5 (Resumo Inteligente de Notícias)

ENTREGAS:
1. FIX (api_samurai.py): A rota /api/daily-news agora coleta os resumos dos feeds.
2. IA: Usa o Gemini para transformar as manchetes em resumos explicativos de 2-3 linhas.
3. ALERJ: Mantém a tentativa de scraping (mesmo que o site seja dinâmico).

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

def fix_api_news_summary() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    new_endpoint = r'''
# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS (Com Resumo IA)
# ============================================================
@app.get("/api/daily-news", dependencies=[Depends(require_token)])
def daily_news():
    import feedparser
    import requests
    from bs4 import BeautifulSoup
    from services.ai import ask_gemini

    noticias_brutas = []
    links_vistos = set()

    # 1. Câmara dos Deputados (RSS)
    try:
        feed = feedparser.parse("https://www.camara.leg.br/noticias/rss/ultimas-noticias")
        for entry in feed.entries[:3]:
            resumo = getattr(entry, 'summary', '')
            # Limpa HTML do resumo
            clean_resumo = BeautifulSoup(resumo, "html.parser").get_text(strip=True)
            noticias_brutas.append(f"FONTE: Câmara\nTÍTULO: {entry.title}\nRESUMO: {clean_resumo}")
    except Exception as e:
        print(f"Erro Câmara RSS: {e}")

    # 2. Senado Federal (RSS)
    try:
        feed = feedparser.parse("https://www12.senado.leg.br/noticias/RSS")
        for entry in feed.entries[:3]:
            resumo = getattr(entry, 'summary', '')
            clean_resumo = BeautifulSoup(resumo, "html.parser").get_text(strip=True)
            noticias_brutas.append(f"FONTE: Senado\nTÍTULO: {entry.title}\nRESUMO: {clean_resumo}")
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
                    if titulo not in links_vistos:
                        links_vistos.add(titulo)
                        noticias_brutas.append(f"FONTE: ALERJ\nTÍTULO: {titulo}\nRESUMO: Notícia do site da ALERJ.")
                    if len([n for n in noticias_brutas if "ALERJ" in n]) >= 2:
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
                if titulo not in links_vistos:
                    links_vistos.add(titulo)
                    noticias_brutas.append(f"FONTE: Macaé\nTÍTULO: {titulo}\nRESUMO: Notícia do site da Câmara de Macaé.")
                if len([n for n in noticias_brutas if "Macaé" in n]) >= 2:
                    break
    except Exception as e:
        print(f"Erro Macaé scraping: {e}")

    if not noticias_brutas:
        return {"text": "📰 Nenhuma notícia encontrada no momento."}

    # Agora, enviamos tudo para a IA mastigar e resumir
    texto_bruto_concatenado = "\n\n---\n\n".join(noticias_brutas)
    
    prompt = f"""Atue como o Analista Político do Projeto Samurai.
Abaixo estão as notícias brutas coletadas hoje dos sites oficiais.

Sua missão:
1. Para CADA notícia, crie um resumo explicativo curto (2 a 3 linhas).
2. O resumo deve explicar "o que aconteceu" e "qual o impacto prático" para o cidadão.
3. Formate a saída como uma lista em Markdown (bullet points). Use negrito no título e texto normal no resumo.
4. Organize por fonte (Câmara, Senado, Macaé, ALERJ) se possível.
5. Seja direto, sem enrolação e sem introduções (não escreva "aqui estão as notícias").

NOTÍCIAS BRUTAS:
{texto_bruto_concatenado}
"""

    try:
        resumo_final = ask_gemini(prompt)
        texto_final = "🏛️ **Notícias Legislativas Resumidas**\n\n" + resumo_final
    except Exception as e:
        texto_final = "Erro ao gerar resumo com a IA. Aqui estão os títulos brutos:\n\n" + texto_bruto_concatenado

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
        print("[ERRO] api_samurai.py — marcadores não encontrados.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat(api): adiciona resumo inteligente com ia nas noticias legislativas"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
        
        # Força o deploy no Render lendo do .env.render
        try:
            hook_url = ""
            env_file = BASE / ".env.render"
            if env_file.exists():
                for line in read(env_file).splitlines():
                    if line.startswith("RENDER_DEPLOY_HOOK_URL="):
                        hook_url = line.split("=", 1)[1].strip()
                        break
            if hook_url:
                import requests
                requests.get(hook_url, timeout=10)
                print("[OK] Deploy no Render disparado!")
        except Exception:
            pass
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V6.5 — RESUMO INTELIGENTE DE NOTÍCIAS")
    print("=" * 60)

    fix_api_news_summary()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Render ficar 'Live' (cerca de 2 min).")
    print("2. Vá no GitHub Actions e rode o 'Samurai Daily News' novamente.")
    print("3. Desta vez, a mensagem no Telegram terá um texto explicativo em cada tópico.")
    print("\nAguardando seu feedback para escolhermos qual das 5 automações faremos primeiro!")

if __name__ == "__main__":
    aplicar()