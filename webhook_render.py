import os
import sys
import traceback
from pathlib import Path

print(">>> [webhook_render] Iniciando modulo...", file=sys.stderr)
print(f">>> [webhook_render] CWD: {os.getcwd()}", file=sys.stderr)

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    import psycopg2
    print(">>> [webhook_render] Imports OK", file=sys.stderr)
except Exception as e:
    print(f">>> [webhook_render] ERRO NOS IMPORTS: {e}", file=sys.stderr)
    traceback.print_exc()
    psycopg2 = None

app = FastAPI(title="Samurai Webhook")

class EmailPayload(BaseModel):
    subject: str
    sender: str
    content: str

@app.get("/")
def health():
    return {
        "status": "ok",
        "has_postgres": psycopg2 is not None,
        "has_supabase_url": bool(os.environ.get("SUPABASE_URL"))
    }

@app.post("/webhook/email")
async def receive_email(payload: EmailPayload):
    db_url = os.environ.get("SUPABASE_URL")
    if not db_url:
        return {"status": "error", "message": "SUPABASE_URL nao configurada."}
    if not psycopg2:
        return {"status": "error", "message": "psycopg2 nao disponivel."}

    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO newsletters_inbox (subject, sender, content) VALUES (%s, %s, %s)",
            (payload.subject, payload.sender, payload.content),
        )
        conn.commit()
        conn.close()
        print(f"📥 Email recebido: {payload.subject}", file=sys.stderr)
        return {"status": "success", "message": "Newsletter salva!"}
    except Exception as e:
        print(f"❌ Erro no banco: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))