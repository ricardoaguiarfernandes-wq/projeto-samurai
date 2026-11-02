import os, requests, sys
from datetime import date, timedelta

def run():
    token = os.environ.get("SAMURAI_API_TOKEN")
    tg = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Pega o status geral (Burnout/Habitos) via API
        r = requests.get("https://samurai-webhook.onrender.com/api/status", headers=headers, timeout=90).json()
        
        msg = f"📊 **Fechamento Semanal**\n\n"
        msg += f"Risco de Burnout: {r['burnout']['score']}/100\n"
        msg += f"Taxa de Hábitos: {r['burnout']['habit_rate']}%\n"
        msg += f"Média de Energia: {r['burnout']['avg_energy']}/10\n"
        msg += f"Média de Sono: {r['burnout']['avg_sleep']}h\n\n"
        
        if r['burnout']['score'] >= 60:
            msg += "⚠️ *Atenção:* Seu corpo está pedindo descanso. Reduza o ritmo na próxima semana.\n"
        else:
            msg += "🔥 *Excelente:* Você está no caminho da disciplina. Mantenha o foco!\n"
            
        requests.post(f"https://api.telegram.org/bot{tg}/sendMessage", json={"chat_id": chat, "text": msg, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    run()
