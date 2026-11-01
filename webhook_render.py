import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI(title="Samurai Webhook")

class EmailPayload(BaseModel):
    subject: str
    sender: str
    content: str

@app.post("/webhook/email")
async def receive_email(payload: EmailPayload):
    # A URL do banco deve ser configurada nas variáveis de ambiente do Render/Railway
    db_url = os.environ.get("SUPABASE_URL")
    if not db_url:
        return {"status": "error", "message": "SUPABASE_URL não configurada."}
        
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO newsletters_inbox (subject, sender, content) VALUES (%s, %s, %s)",
            (payload.subject, payload.sender, payload.content)
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Newsletter recebida e salva!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
