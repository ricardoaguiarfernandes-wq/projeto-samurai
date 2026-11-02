import os, requests, sys
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
            msg = "🎯 <b>Caçador de Oportunidades</b>\n\n" + "\n".join(alertas)
        else:
            msg = "📈 <b>Status do Mercado</b>\n\nNenhuma queda brusca (acima de 2%) nas suas ações hoje. O mercado está estável."
            
        requests.post(f"https://api.telegram.org/bot{tg}/sendMessage", json={"chat_id": chat, "text": msg, "parse_mode": "HTML"})
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    run()
