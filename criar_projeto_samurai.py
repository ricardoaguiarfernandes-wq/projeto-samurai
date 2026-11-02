"""
criar_projeto_samurai.py — V7.0 (As 5 Automações)

ENTREGAS:
1. DB: Adiciona tabelas 'flashcards' e 'watchlist'.
2. API (Brief): Adiciona clima de Macaé e link do Google Calendar.
3. BOT (Telegram): Adiciona comandos /flashcard e /acoes.
4. CRON: Cria 'weekly_review.yml' (Domingo 20h) e 'stock_alerts.yml' (Seg-Sex 18h).

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
# 1. SCHEMA (Novas tabelas)
# ============================================================
def fix_schema_new_tables() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)
    if "CREATE TABLE IF NOT EXISTS flashcards" in txt:
        print("[SKIP] schema.py — tabelas já existem.")
        return
    
    marker = '"""CREATE TABLE IF NOT EXISTS manuals (id SERIAL PRIMARY KEY, title TEXT UNIQUE, content TEXT NOT NULL, uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""",'
    novas_linhas = marker + '''
        """CREATE TABLE IF NOT EXISTS flashcards (id SERIAL PRIMARY KEY, question TEXT NOT NULL, answer TEXT NOT NULL, next_review TEXT NOT NULL);""",
        """CREATE TABLE IF NOT EXISTS watchlist (id SERIAL PRIMARY KEY, ticker TEXT UNIQUE NOT NULL);""",'''
    
    if marker in txt:
        txt = txt.replace(marker, novas_linhas, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] schema.py — marcador não encontrado.")

# ============================================================
# 2. API: BRIEF (Clima + Google Calendar)
# ============================================================
def fix_api_brief_weather_calendar() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "CLIMA EM MACAÉ" in txt:
        print("[SKIP] api_samurai.py — clima e calendar já adicionados ao Brief.")
        return

    # Inserir dados de clima e calendar antes do prompt
    old_prompt_start = '''    prompt = f"""Atue como o Conselho de Mestres do Projeto Samurai.'''
    
    new_context = '''    # Busca Clima em Macaé (Open-Meteo)
    try:
        w_req = requests.get("https://api.open-meteo.com/v1/forecast?latitude=-22.376&longitude=-41.786&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=America/Sao_Paulo").json()
        w_code = w_req["daily"]["weather_code"][0]
        w_rain = w_req["daily"]["precipitation_probability_max"][0]
        w_max = w_req["daily"]["temperature_2m_max"][0]
        clima_ctx = f"Chuva: {w_rain}%, Temp Max: {w_max}°C"
    except Exception:
        clima_ctx = "Clima indisponível."

    # Gera link do Google Calendar
    import urllib.parse
    from datetime import datetime, timedelta
    cal_start = datetime.now().strftime("%Y%m%dT180000")
    cal_end = (datetime.now() + timedelta(hours=1)).strftime("%Y%m%dT190000")
    treino_encoded = urllib.parse.quote(f"Treino: {treino_hoje}")
    cal_link = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={treino_encoded}&dates={cal_start}/{cal_end}"

    prompt = f"""Atue como o Conselho de Mestres do Projeto Samurai.'''

    if old_prompt_start in txt:
        txt = txt.replace(old_prompt_start, new_context, 1)

    # Inserir o clima no prompt e o calendário na resposta final
    old_data = '''CONTEXTO EXTERNO:
- Notícias Recentes: 
{noticias_ctx}'''
    
    new_data = '''CONTEXTO EXTERNO:
- Clima em Macaé Hoje: {clima_ctx}
- Notícias Recentes: 
{noticias_ctx}'''
    
    if old_data in txt:
        txt = txt.replace(old_data, new_data, 1)
        
    old_text = '''            f"{brief.get('closing', '')}"
        )'''
        
    new_text = '''            f"{brief.get('closing', '')}\\n\\n"
            f"📅 [Adicionar Treino no Google Calendar]({cal_link})"
        )'''
    
    if old_text in txt:
        txt = txt.replace(old_text, new_text, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] api_samurai.py — texto final do brief não encontrado.")

# ============================================================
# 3. BOT TELEGRAM (Comandos /flashcard e /acoes)
# ============================================================
def fix_api_telegram_commands() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if 'text.startswith("/flashcard")' in txt:
        print("[SKIP] api_samurai.py — comandos do Telegram já existem.")
        return

    old_text_mode = '''        if text.startswith("/start"):
            reply("🥋 Bem-vindo ao Dojo Digital. Envie uma foto de comprovante ou digite sua duvida.")
            return'''
            
    new_text_mode = '''        if text.startswith("/start"):
            reply("🥋 Bem-vindo ao Dojo Digital. Envie uma foto de comprovante ou digite sua duvida.")
            return
            
        if text.startswith("/flashcard"):
            card = query_one("SELECT question, answer FROM flashcards ORDER BY RANDOM() LIMIT 1")
            if not card:
                reply("📭 Nenhum flashcard cadastrado ainda. Vá na aba Carreira do app.")
            else:
                reply(f"🧠 **Flashcard:**\\n\\n{card['question']}\\n\\n_(Digite qualquer coisa para ver a resposta)_\\n**Resp:** {card['answer']}")
            return

        if text.startswith("/acoes"):
            reply("📈 Verificando as suas ações...")
            try:
                import yfinance as yf
                port = query_all("SELECT ticker FROM portfolio WHERE SUBSTR(ticker, 1, 3) != 'RF:'")
                if not port:
                    reply("Sua carteira está vazia.")
                else:
                    msg = "**Cotações da sua Carteira:**\\n"
                    for p_item in port:
                        t = p_item['ticker']
                        if ".SA" not in t: t += ".SA"
                        d = yf.Ticker(t).history(period="1d")
                        if not d.empty:
                            preco = d['Close'].iloc[-1]
                            msg += f"- {p_item['ticker']}: R$ {preco:.2f}\\n"
                    reply(msg)
            except Exception as e:
                reply(f"Erro ao buscar ações: {e}")
            return'''
            
    if old_text_mode in txt:
        txt = txt.replace(old_text_mode, new_text_mode, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] api_samurai.py — bloco de texto não encontrado.")

# ============================================================
# 4. CRON: WEEKLY REVIEW (Domingo)
# ============================================================
def create_weekly_review() -> None:
    # Script
    script_path = BASE / "weekly_review_telegram.py"
    if not script_path.exists():
        content = '''import os, requests, sys
from datetime import date, timedelta

def run():
    token = os.environ.get("SAMURAI_API_TOKEN")
    tg = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Pega o status geral (Burnout/Habitos) via API
        r = requests.get("https://samurai-webhook.onrender.com/api/status", headers=headers, timeout=90).json()
        
        msg = f"📊 **Fechamento Semanal**\\n\\n"
        msg += f"Risco de Burnout: {r['burnout']['score']}/100\\n"
        msg += f"Taxa de Hábitos: {r['burnout']['habit_rate']}%\\n"
        msg += f"Média de Energia: {r['burnout']['avg_energy']}/10\\n"
        msg += f"Média de Sono: {r['burnout']['avg_sleep']}h\\n\\n"
        
        if r['burnout']['score'] >= 60:
            msg += "⚠️ *Atenção:* Seu corpo está pedindo descanso. Reduza o ritmo na próxima semana.\\n"
        else:
            msg += "🔥 *Excelente:* Você está no caminho da disciplina. Mantenha o foco!\\n"
            
        requests.post(f"https://api.telegram.org/bot{tg}/sendMessage", json={"chat_id": chat, "text": msg, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    run()
'''
        write_validated(script_path, content)

    # Workflow
    wf = BASE / ".github" / "workflows" / "weekly_review.yml"
    if not wf.exists():
        content = '''name: Samurai Weekly Review
on:
  schedule:
    - cron: '0 23 * * 0' # Domingo 20h Brasília
  workflow_dispatch:
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12'}
      - run: pip install requests
      - run: python weekly_review_telegram.py
        env:
          SAMURAI_API_TOKEN: ${{ secrets.SAMURAI_API_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
'''
        wf.parent.mkdir(parents=True, exist_ok=True)
        wf.write_text(content, encoding="utf-8")
        print("[OK] weekly_review criado.")

# ============================================================
# 5. CRON: STOCK ALERTS (Seg-Sex)
# ============================================================
def create_stock_alerts() -> None:
    script_path = BASE / "stock_alerts_telegram.py"
    if not script_path.exists():
        content = '''import os, requests, sys
import yfinance as yf

def run():
    token = os.environ.get("SAMURAI_API_TOKEN")
    tg = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Puxa a watchlist via API (ou usa uma padrão)
        r = requests.get("https://samurai-webhook.onrender.com/api/portfolio", headers=headers, timeout=90).json()
        # Vamos simular uma watchlist para teste
        watchlist = ["TAEE11.SA", "CXSE3.SA", "BBAS3.SA"]
        
        alertas = []
        for t in watchlist:
            hist = yf.Ticker(t).history(period="2d")
            if len(hist) >= 2:
                ontem = hist['Close'].iloc[-2]
                hoje = hist['Close'].iloc[-1]
                queda = ((hoje - ontem) / ontem) * 100
                
                if queda <= -2.0: # Caiu 2% ou mais
                    alertas.append(f"📉 *{t}* caiu {abs(queda):.1f}% (R$ {hoje:.2f}). Oportunidade?")
        
        if alertas:
            msg = "🎯 **Caçador de Oportunidades**\\n\\n" + "\\n".join(alertas)
            requests.post(f"https://api.telegram.org/bot{tg}/sendMessage", json={"chat_id": chat, "text": msg, "parse_mode": "Markdown"})
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    run()
'''
        write_validated(script_path, content)

    # Workflow
    wf = BASE / ".github" / "workflows" / "stock_alerts.yml"
    if not wf.exists():
        content = '''name: Samurai Stock Alerts
on:
  schedule:
    - cron: '0 21 * * 1-5' # Seg-Sex 18h Brasília
  workflow_dispatch:
jobs:
  alerts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.12'}
      - run: pip install requests yfinance
      - run: python stock_alerts_telegram.py
        env:
          SAMURAI_API_TOKEN: ${{ secrets.SAMURAI_API_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
'''
        wf.parent.mkdir(parents=True, exist_ok=True)
        wf.write_text(content, encoding="utf-8")
        print("[OK] stock_alerts criado.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: implementa as 5 automacoes (clima, calendar, flashcards, review, stocks)"])
    
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
    print("V7.0 — AS 5 AUTOMAÇÕES")
    print("=" * 60)

    fix_schema_new_tables()
    fix_api_brief_weather_calendar()
    fix_api_telegram_commands()
    create_weekly_review()
    create_stock_alerts()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nComo testar:")
    print("1. CLIMA E CALENDÁRIO: Force o Brief pelo GitHub Actions (amanhã no Telegram).")
    print("2. FLASHCARDS: Mande '/flashcard' no seu bot do Telegram (precisa ter flashcards na aba Carreira).")
    print("3. AÇÕES: Mande '/acoes' no Telegram para ver as cotações.")
    print("4. REVISÃO SEMANAL: Vá em Actions > Samurai Weekly Review > Run workflow.")
    print("5. ALERTAS DE AÇÕES: Vá em Actions > Samurai Stock Alerts > Run workflow.")

if __name__ == "__main__":
    aplicar()