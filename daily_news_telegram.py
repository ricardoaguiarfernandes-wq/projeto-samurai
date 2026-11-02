import os
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
