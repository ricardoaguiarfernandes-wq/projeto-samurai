import os
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
