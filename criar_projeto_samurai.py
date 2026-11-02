"""
criar_projeto_samurai.py — V7.3 (Google News, Formatação Telegram e Status Alerts)

ENTREGAS:
1. FIX (api_samurai.py): Usa Google News RSS para Macaé e ALERJ (evita bloqueio).
2. FIX (api_samurai.py): Prompt de notícias formatado com tags HTML do Telegram.
3. FIX (stock_alerts_telegram.py): Manda mensagem mesmo se as ações não caírem.
4. FIX (scripts telegram): Adiciona 'disable_web_page_preview' para não gerar aquele link gigante do Google Calendar.

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
# 1. API (NOTÍCIAS VIA GOOGLE NEWS E HTML)
# ============================================================
def fix_api_news_google() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    new_endpoint = r'''
# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS (Com Resumo IA)
# ============================================================
@app.get("/api/daily-news", dependencies=[Depends(require_token)])
def daily_news():
    import feedparser
    from bs4 import BeautifulSoup
    from services.ai import ask_gemini

    noticias_brutas = []
    links_vistos = set()

    # 1. Câmara dos Deputados (RSS Oficial)
    try:
        feed = feedparser.parse("https://www.camara.leg.br/noticias/rss/ultimas-noticias")
        for entry in feed.entries[:3]:
            resumo = getattr(entry, 'summary', '')
            clean_resumo = BeautifulSoup(resumo, "html.parser").get_text(strip=True)
            noticias_brutas.append(f"FONTE: Câmara\nTÍTULO: {entry.title}\nRESUMO: {clean_resumo}")
    except Exception as e:
        print(f"Erro Câmara RSS: {e}")

    # 2. Senado Federal (RSS Oficial)
    try:
        feed = feedparser.parse("https://www12.senado.leg.br/noticias/RSS")
        for entry in feed.entries[:3]:
            resumo = getattr(entry, 'summary', '')
            clean_resumo = BeautifulSoup(resumo, "html.parser").get_text(strip=True)
            noticias_brutas.append(f"FONTE: Senado\nTÍTULO: {entry.title}\nRESUMO: {clean_resumo}")
    except Exception as e:
        print(f"Erro Senado RSS: {e}")

    # 3. ALERJ (Via Google News para burlar bloqueio)
    try:
        feed = feedparser.parse("https://news.google.com/rss/search?q=alerj+noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419")
        for entry in feed.entries[:2]:
            if entry.title not in links_vistos:
                links_vistos.add(entry.title)
                noticias_brutas.append(f"FONTE: ALERJ\nTÍTULO: {entry.title}\nRESUMO: Notícia recente da ALERJ.")
    except Exception as e:
        print(f"Erro ALERJ Google News: {e}")

    # 4. Câmara de Macaé (Via Google News para burlar bloqueio)
    try:
        feed = feedparser.parse("https://news.google.com/rss/search?q=camara+macae+noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419")
        for entry in feed.entries[:2]:
            if entry.title not in links_vistos:
                links_vistos.add(entry.title)
                noticias_brutas.append(f"FONTE: Macaé\nTÍTULO: {entry.title}\nRESUMO: Notícia recente da Câmara de Macaé.")
    except Exception as e:
        print(f"Erro Macaé Google News: {e}")

    if not noticias_brutas:
        return {"text": "📰 Nenhuma notícia encontrada no momento."}

    texto_bruto_concatenado = "\n\n---\n\n".join(noticias_brutas)
    
    prompt = f"""Atue como o Analista Político do Projeto Samurai.
Abaixo estão as notícias brutas coletadas hoje.

Sua missão:
1. Para CADA notícia, crie um resumo explicativo curto (2 a 3 linhas).
2. Formate a saída usando HTML para o Telegram: Use <b>Título</b> e <i>Resumo</i>. NÃO use # ou **.
3. Organize por fonte (Câmara, Senado, Macaé, ALERJ).
4. Seja direto e sem introduções.

NOTÍCIAS BRUTAS:
{texto_bruto_concatenado}
"""

    try:
        resumo_final = ask_gemini(prompt)
        # O Telegram precisa da tag <b> e <i>, que o Gemini já vai gerar.
        texto_final = "<b>🏛️ Notícias Legislativas Resumidas</b>\n\n" + resumo_final
    except Exception as e:
        texto_final = "Erro ao gerar resumo com a IA."

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

# ============================================================
# 2. STOCK ALERTS (Sempre envia mensagem)
# ============================================================
def fix_stock_alerts() -> None:
    p = BASE / "stock_alerts_telegram.py"
    if not p.exists(): return

    txt = read(p)
    if "Nenhuma queda brusca" in txt:
        print("[SKIP] stock_alerts_telegram.py — já configurado.")
        return

    old_cond = '''        if alertas:
            msg = "🎯 **Caçador de Oportunidades**\\n\\n" + "\\n".join(alertas)
            requests.post(f"https://api.telegram.org/bot{tg}/sendMessage", json={"chat_id": chat, "text": msg, "parse_mode": "Markdown"})'''

    new_cond = '''        if alertas:
            msg = "🎯 <b>Caçador de Oportunidades</b>\\n\\n" + "\\n".join(alertas)
        else:
            msg = "📈 <b>Status do Mercado</b>\\n\\nNenhuma queda brusca (acima de 2%) nas suas ações hoje. O mercado está estável."
            
        requests.post(f"https://api.telegram.org/bot{tg}/sendMessage", json={"chat_id": chat, "text": msg, "parse_mode": "HTML"})'''

    if old_cond in txt:
        txt = txt.replace(old_cond, new_cond, 1)
        write_validated(p, txt)

# ============================================================
# 3. OUTROS SCRIPTS (Desabilitar Preview e HTML)
# ============================================================
def fix_telegram_scripts() -> None:
    # Brief
    p1 = BASE / "daily_brief_telegram.py"
    if p1.exists():
        txt = read(p1)
        if "disable_web_page_preview" not in txt:
            txt = txt.replace('"parse_mode": "Markdown"', '"parse_mode": "HTML", "disable_web_page_preview": True')
            write_validated(p1, txt)

    # News
    p2 = BASE / "daily_news_telegram.py"
    if p2.exists():
        txt = read(p2)
        if "disable_web_page_preview" not in txt:
            txt = txt.replace('"parse_mode": "Markdown"', '"parse_mode": "HTML", "disable_web_page_preview": True')
            write_validated(p2, txt)

    # Weekly Review
    p3 = BASE / "weekly_review_telegram.py"
    if p3.exists():
        txt = read(p3)
        if "disable_web_page_preview" not in txt:
            txt = txt.replace('"parse_mode": "Markdown"', '"parse_mode": "HTML", "disable_web_page_preview": True')
            write_validated(p3, txt)

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "fix: raspagem google news, formato html telegram e alertas diarios"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
        
        # Força Deploy
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
    print("V7.3 — FIX NOTÍCIAS E ALERTAS")
    print("=" * 60)

    fix_api_news_google()
    fix_stock_alerts()
    fix_telegram_scripts()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Render atualizar.")
    print("2. No Telegram, envie o comando '/news' (ou rode o 'Samurai Daily News' no GitHub).")
    print("3. Veja se Macaé e ALERJ aparecem (via Google News) e se o texto está formatado corretamente.")
    print("4. Vá no GitHub Actions > Samurai Stock Alerts > Run workflow. Vai chegar no Telegram mesmo se as ações não caírem.")

if __name__ == "__main__":
    aplicar()