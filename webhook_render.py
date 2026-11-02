"""
webhook_render.py — DEPRECATED (V2.0)

Mantido apenas como shim de compatibilidade. Toda a logica foi unificada
em api_samurai.py. Se o Render aponta para "uvicorn webhook_render:app",
continua funcionando sem alterar config — mas o recomendado e:
    uvicorn api_samurai:app --host 0.0.0.0 --port $PORT
"""
from api_samurai import app

if __name__ == "__main__":
    import os
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
