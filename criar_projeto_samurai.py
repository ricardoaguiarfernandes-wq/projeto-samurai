"""
setup_telegram_v2.py — Configura o bot do Telegram e o GitHub Actions.
"""
import ast
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

# --- CONTEÚDO DOS ARQUIVOS ---

SCRIPT_TELEGRAM = '''import os
import requests
import sys

def send_telegram_message():
    samurai_token = os.environ.get("SAMURAI_API_TOKEN")
    tg_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    tg_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not all([samurai_token, tg_bot_token, tg_chat_id]):
        print("❌ Erro: Faltam variáveis de ambiente.")
        sys.exit(1)

    print("⏳ Acordando o Render e buscando o Brief diário...")
    headers = {"Authorization": f"Bearer {samurai_token}"}
    
    try:
        # Timeout alto para aguentar o Render "dormindo"
        response = requests.get(
            "https://samurai-webhook.onrender.com/api/brief", 
            headers=headers, 
            timeout=90
        )
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Erro ao conectar na API do Samurai: {e}")
        requests.post(
            f"https://api.telegram.org/bot{tg_bot_token}/sendMessage",
            json={"chat_id": tg_chat_id, "text": f"⚠️ Samurai caiu. Erro na API: {e}"}
        )
        sys.exit(1)

    if "error" in data:
        print(f"❌ Erro retornado pela IA: {data['error']}")
        sys.exit(1)

    mensagem = data.get("text", "Bom dia! Não consegui gerar o texto hoje.")
    
    print("📤 Enviando mensagem para o Telegram...")
    tg_url = f"https://api.telegram.org/bot{tg_bot_token}/sendMessage"
    payload = {"chat_id": tg_chat_id, "text": mensagem, "parse_mode": "Markdown"}
    
    tg_resp = requests.post(tg_url, json=payload, timeout=15)
    
    if tg_resp.status_code == 200:
        print("✅ Mensagem enviada com sucesso!")
    else:
        print(f"❌ Erro no Telegram: {tg_resp.text}")
        sys.exit(1)

if __name__ == "__main__":
    send_telegram_message()
'''

ACTION_YAML = '''name: Samurai Daily Brief

on:
  schedule:
    # 09:00 UTC = 06:00 Horário de Brasília
    - cron: '0 9 * * *'
  workflow_dispatch: # Permite rodar manualmente para testar

jobs:
  send_brief:
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

      - name: Executar Envio do Telegram
        env:
          SAMURAI_API_TOKEN: ${{ secrets.SAMURAI_API_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python daily_brief_telegram.py
'''

def _git(args):
    return subprocess.run(["git"] + args, cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace")

def aplicar():
    print("⚔️  GERANDO ARQUIVOS DO TELEGRAM E GITHUB ACTIONS...")
    
    # 1. Cria o script Python
    script_path = BASE / "daily_brief_telegram.py"
    ast.parse(SCRIPT_TELEGRAM) # Validação
    script_path.write_text(SCRIPT_TELEGRAM, encoding="utf-8")
    print("[OK] daily_brief_telegram.py criado.")
    
    # 2. Cria a pasta e o arquivo YML
    workflows_dir = BASE / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    yml_path = workflows_dir / "daily_brief.yml"
    yml_path.write_text(ACTION_YAML, encoding="utf-8")
    print("[OK] .github/workflows/daily_brief.yml criado.")

    # 3. Git Push
    print("\n☁️  SINCRONIZANDO COM O GITHUB...")
    _git(["add", "-A"])
    _git(["commit", "-m", "feat(v2.0): automacao Telegram via GitHub Actions"])
    r = _git(["push", "origin", "main"])
    
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[AVISO] O push falhou: {r.stderr}")

if __name__ == "__main__":
    aplicar()