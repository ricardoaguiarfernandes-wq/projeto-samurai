import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from pathlib import Path
from flaredantic import FlareTunnel, TunnelConfig
import threading

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "samurai.db"

app = FastAPI(title="Samurai Webhook")

class EmailPayload(BaseModel):
    subject: str
    sender: str
    content: str

@app.post("/webhook/email")
async def receive_email(payload: EmailPayload):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO newsletters_inbox (subject, sender, content) VALUES (?, ?, ?)",
            (payload.subject, payload.sender, payload.content)
        )
        conn.commit()
        conn.close()
        print(f"📥 Email recebido: {payload.subject}")
        return {"status": "success", "message": "Newsletter recebida e salva!"}
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
        return {"status": "error", "message": str(e)}

def iniciar_tunel():
    """Inicia o túnel Cloudflare em segundo plano e exibe a URL."""
    try:
        config = TunnelConfig(port=8000)
        tunnel = FlareTunnel(config)
        tunnel.start()
        print("=" * 60)
        print("🔗 URL PÚBLICA DO WEBHOOK (COPIE PARA O POWER AUTOMATE):")
        print(f"👉 {tunnel.tunnel_url}/webhook/email")
        print("=" * 60)
        print("(Deixe esta janela aberta enquanto o app estiver rodando)")
        return tunnel
    except Exception as e:
        print(f"⚠️ Erro ao criar túnel Cloudflare: {e}")
        print("O webhook funcionará apenas na rede local.")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("⚔️  SERVIDOR DE WEBHOOK INICIADO")
    print("=" * 60)
    
    # Inicia o túnel em uma thread separada para não bloquear o Uvicorn
    tunel = iniciar_tunel()
    
    # Inicia o servidor FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000)
