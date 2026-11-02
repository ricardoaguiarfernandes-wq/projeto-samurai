"""
api_samurai.py — API do Samurai V2.0

FastAPI unificada. Substitui o antigo webhook_render.py e expoe:
- /health                  (sem auth)
- /api/status              (resumo do dia + burnout)
- /api/habits              (habitos + status de hoje)
- /api/habits/{id}/toggle  (marcar/desmarcar/forcar)
- /api/checkin             (GET/POST do check-in diario)
- /api/portfolio           (acoes + renda fixa)
- /api/brief               (brief diario IA — JSON + text pronto p/ WhatsApp)
- /webhook/email           (compat — recebe newsletter via Power Automate)

Auth: Bearer token em SAMURAI_API_TOKEN (env var) ou st.secrets["api_token"].
Banco: hibrido via core.database (SQLite local / Supabase em prod).
"""
from __future__ import annotations

import hmac
import io
import requests
import json
import os
import re as _re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from core.database import execute, query_all, query_one, is_postgres
from core.schema import init_db

app = FastAPI(
    title="Samurai API",
    description="API pessoal do Projeto Samurai V2.0",
    version="2.0.0",
)

# Inicializa o banco (nao fatal se falhar no boot — ex: Supabase indisponivel).
try:
    init_db()
except Exception as _e:
    print(f"[AVISO] init_db falhou no boot: {_e}")


# ============================================================
# AUTENTICACAO
# ============================================================

def _get_expected_token() -> Optional[str]:
    tok = os.environ.get("SAMURAI_API_TOKEN", "").strip()
    if tok:
        return tok
    try:
        import streamlit as st  # type: ignore
        if "api_token" in st.secrets:
            return str(st.secrets["api_token"])
    except Exception:
        pass
    return None



def safe_int(v) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0

def safe_float(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0

def require_token(authorization: Optional[str] = Header(None)) -> None:
    expected = _get_expected_token()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Servidor sem SAMURAI_API_TOKEN configurado.",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente.")
    sent = authorization[len("Bearer "):].strip()
    if not hmac.compare_digest(sent, expected):
        raise HTTPException(status_code=403, detail="Token invalido.")


# ============================================================
# MODELOS
# ============================================================

class HabitToggle(BaseModel):
    done: Optional[bool] = None


class CheckinIn(BaseModel):
    energy: int = Field(..., ge=1, le=10)
    sleep_hours: float = Field(..., ge=0, le=16)
    mood: str = "Neutro"
    stress: int = Field(..., ge=1, le=10)
    notes: Optional[str] = None


class EmailPayload(BaseModel):
    subject: str
    sender: str
    content: str


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def root():
    return {"app": "Samurai API", "version": "2.0.0", "status": "ok"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "has_postgres": is_postgres(),
        "today": date.today().isoformat(),
    }


# ============================================================
# STATUS + BURNOUT
# ============================================================

@app.get("/api/status", dependencies=[Depends(require_token)])
def get_status():
    today_iso = date.today().isoformat()
    week_ago = (date.today() - timedelta(days=7)).isoformat()

    checkin = query_one(
        "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
    )
    total_habits = safe_int((query_one(
        "SELECT COUNT(*) AS c FROM habits WHERE active = 1"
    ) or {}).get("c"))
    done_today = safe_int((query_one(
        "SELECT COUNT(*) AS c FROM habit_logs WHERE log_date = ? AND done = 1",
        (today_iso,),
    ) or {}).get("c"))

    checkins = query_all(
        "SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?",
        (week_ago,),
    )
    logs = query_all("SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,))
    
    done = sum(1 for r in logs if safe_int(r.get("done")) == 1)
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(safe_float(r.get("energy")) for r in checkins) / len(checkins)
        avg_stress = sum(safe_float(r.get("stress")) for r in checkins) / len(checkins)
        avg_sleep = sum(safe_float(r.get("sleep_hours")) for r in checkins) / len(checkins)
    else:
        avg_energy, avg_stress, avg_sleep = 5.0, 5.0, 7.0

    e_score = (10 - avg_energy) / 10 * 30
    s_score = avg_stress / 10 * 30
    sl_score = max(0, 8 - avg_sleep) / 8 * 20
    h_score = (1 - taxa) * 20
    burnout = max(0.0, min(100.0, e_score + s_score + sl_score + h_score))

    return {
        "date": today_iso,
        "checkin": checkin,
        "habits": {
            "total": total_habits,
            "done": done_today,
            "pending": max(0, total_habits - done_today),
        },
        "burnout": {
            "score": round(burnout, 1),
            "avg_energy": round(avg_energy, 1),
            "avg_stress": round(avg_stress, 1),
            "avg_sleep": round(avg_sleep, 1),
            "habit_rate": round(taxa * 100, 1),
        },
    }


# ============================================================
# HABITOS
# ============================================================

@app.get("/api/habits", dependencies=[Depends(require_token)])
def list_habits():
    today_iso = date.today().isoformat()
    rows = query_all(
        """
        SELECT h.id, h.name, h.pillar, COALESCE(l.done, 0) AS done
        FROM habits h
        LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ?
        WHERE h.active = 1
        ORDER BY h.pillar, h.name
        """,
        (today_iso,),
    )
    return {"date": today_iso, "habits": rows}


@app.post("/api/habits/{habit_id}/toggle", dependencies=[Depends(require_token)])
def toggle_habit(habit_id: int, body: HabitToggle):
    today_iso = date.today().isoformat()
    habit = query_one("SELECT id FROM habits WHERE id = ?", (habit_id,))
    if not habit:
        raise HTTPException(status_code=404, detail="Habito nao encontrado.")

    if body.done is None:
        current = query_one(
            "SELECT done FROM habit_logs WHERE habit_id = ? AND log_date = ?",
            (habit_id, today_iso),
        )
        new_val = 0 if (current and current["done"]) else 1
    else:
        new_val = 1 if body.done else 0

    execute(
        """
        INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?)
        ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done
        """,
        (habit_id, today_iso, new_val),
    )
    
    # Gamificação: ganha 10 XP ao concluir
    if new_val == 1:
        try:
            execute("UPDATE user_stats SET xp = xp + 10 WHERE id = 1")
        except Exception:
            pass
            
    return {"habit_id": habit_id, "date": today_iso, "done": bool(new_val)}


# ============================================================
# CHECK-IN
# ============================================================

@app.get("/api/checkin", dependencies=[Depends(require_token)])
def get_checkin():
    today_iso = date.today().isoformat()
    row = query_one(
        "SELECT * FROM daily_checkins WHERE checkin_date = ?", (today_iso,)
    )
    return {"date": today_iso, "checkin": row}


@app.post("/api/checkin", dependencies=[Depends(require_token)])
def upsert_checkin(body: CheckinIn):
    today_iso = date.today().isoformat()
    execute(
        """
        INSERT INTO daily_checkins (checkin_date, energy, sleep_hours, mood, stress, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(checkin_date) DO UPDATE SET
            energy = excluded.energy,
            sleep_hours = excluded.sleep_hours,
            mood = excluded.mood,
            stress = excluded.stress,
            notes = excluded.notes
        """,
        (today_iso, body.energy, body.sleep_hours, body.mood, body.stress, body.notes),
    )
    return {"date": today_iso, "saved": True}


# ============================================================
# PATRIMONIO
# ============================================================

@app.get("/api/portfolio", dependencies=[Depends(require_token)])
def get_portfolio():
    portfolio = query_all("SELECT * FROM portfolio")
    try:
        fixed = query_all("SELECT * FROM patrimony_fixed_income")
    except Exception:
        fixed = []
    return {"portfolio": portfolio, "fixed_income": fixed}


# ============================================================
# BRIEF DIARIO (IA — JSON estruturado + text pronto)
# ============================================================

@app.get("/api/brief", dependencies=[Depends(require_token)])
def daily_brief():
    from services.ai import ask_gemini

    today_iso = date.today().isoformat()
    try:
        status = get_status()
    except Exception as e:
        return {"error": f"Falha ao ler status: {e}"}
    
    try:
        habits = list_habits().get("habits", [])
        pending = [h["name"] for h in habits if not safe_int(h.get("done"))]
    except Exception:
        pending = []

    prompt = f"""Voce e o Mentor Samurai, sistema operacional pessoal do Ricardo.
Data: {today_iso}.
Dados do dia:
- Check-in: {status["checkin"] or "nao realizado"}
- Burnout score (7d): {status["burnout"]["score"]}/100 (energia {status["burnout"]["avg_energy"]}, sono {status["burnout"]["avg_sleep"]}h, stress {status["burnout"]["avg_stress"]})
- Habitos pendentes: {pending if pending else "todos concluidos"}
- Taxa de habitos 7d: {status["burnout"]["habit_rate"]}%

Sua resposta DEVE ser um JSON valido com EXATAMENTE estas chaves (sem texto antes ou depois):
{{
  "greeting": "<cumprimento curto, 1 linha>",
  "burnout_alert": "<Baixo|Medio|Alto|Critico>",
  "top_3_priorities": ["<prioridade 1>", "<prioridade 2>", "<prioridade 3>"],
  "training": "<recomendacao de treino do dia, 1 linha>",
  "verse_of_the_day": "<referencia biblica + versiculo curto, sem inventar>",
  "closing": "<frase de encerramento, 1 linha, tom samurai>"
}}

REGRAS ESTRITAS:
- NUNCA use "ou". Crave a escolha.
- Se burnout >= 60, incluir "Descanso e sono" em top_3_priorities.
- Versiculo deve ser real (nao invente referencia nem texto).
- Responda APENAS o JSON. Nada fora do bloco.
"""
    raw = ask_gemini(prompt)
    m = _re.search(r"\{.*\}", raw, _re.DOTALL)
    if not m:
        return {"error": "IA nao retornou JSON", "raw": raw[:500]}
    try:
        brief = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return {"error": f"JSON invalido: {e}", "raw": raw[:500]}

    # Texto pronto para WhatsApp/Telegram
    try:
        txt = (
            f"{brief.get('greeting', 'Bom dia.')}\n\n"
            f"Risco: {brief.get('burnout_alert', '?')}\n\n"
            f"Top 3 prioridades:\n"
            + "\n".join(f"  {i+1}. {p}" for i, p in enumerate(brief.get("top_3_priorities", [])))
            + f"\n\nTreino: {brief.get('training', '-')}\n\n"
            f"Versiculo: {brief.get('verse_of_the_day', '-')}\n\n"
            f"{brief.get('closing', '')}"
        )
    except Exception:
        txt = ""

    brief["text"] = txt
    return brief


# ============================================================
# WEBHOOK DO TELEGRAM (Recebe Fotos e Textos)
# ============================================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

@app.post("/webhook/telegram")
async def receive_telegram(update: dict):
    if not TELEGRAM_BOT_TOKEN:
        return {"status": "error", "message": "Token do Telegram nao configurado no Render."}
    
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    if not chat_id:
        return {"status": "ignored"}
        
    def reply(text: str):
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10
        )

    # --- MODO 1: FOTO (Auto-Categorização de Gastos) ---
    if "photo" in message:
        reply("📸 Analisando comprovante e categorizando...")
        file_id = message["photo"][-1]["file_id"]
        
        # Baixa a imagem do Telegram
        r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getFile?file_id={file_id}", timeout=10)
        file_path = r.json().get("result", {}).get("file_path")
        
        if file_path:
            img_bytes = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path}", timeout=10).content
            
            from services.ai import ask_gemini_vision
            prompt = """Extraia os dados deste comprovante e retorne APENAS um JSON válido, sem markdown:
            {"amount": 0.0, "description": "Nome do Local", "category": "Alimentação/Transporte/Lazer/Outros"}
            Se não for um comprovante, retorne {"error": "not_a_receipt"}."""
            
            res = ask_gemini_vision(img_bytes, prompt)
            m = re.search(r'\{.*\}', res, re.DOTALL)
            
            if m:
                try:
                    data = json.loads(m.group(0))
                    if "error" in data:
                        reply("⚠️ Não consegui identificar um comprovante nessa imagem.")
                    else:
                        execute(
                            "INSERT INTO expenses (expense_date, description, amount, category) VALUES (?, ?, ?, ?)",
                            (date.today().isoformat(), data.get("description", "Desconhecido"), data.get("amount", 0.0), data.get("category", "Outros"))
                        )
                        reply(f"✅ Gasto registrado: *{data.get('description')}* \nValor: R$ {data.get('amount'):.2f} \nCategoria: {data.get('category')}")
                except Exception as e:
                    reply(f"⚠️ Erro ao processar JSON: {e}")
            else:
                reply("⚠️ A IA não conseguiu ler o comprovante.")
        else:
            reply("⚠️ Falha ao baixar a imagem do Telegram.")

    # --- MODO 2: TEXTO (Memória do Diário / RAG) ---
    elif "text" in message:
        text = message["text"]
        
        if text.startswith("/start"):
            reply("🥋 Bem-vindo ao Dojo Digital. Envie uma foto de comprovante ou digite sua dúvida para consultar o diário.")
            return {"status": "ok"}
            
        reply("🧠 Consultando as memórias do seu diário...")
        entries = query_all("SELECT entry_date, content FROM journal_entries ORDER BY entry_date DESC LIMIT 20")
        
        if not entries:
            reply("Ainda não tenho registros no seu diário para consultar.")
            return {"status": "ok"}
            
        ctx = "\n".join([f"[{e['entry_date']}] {e['content']}" for e in entries])
        
        from services.ai import ask_gemini
        prompt = f"""Atue como meu Mentor Samurai. Baseado APENAS nestes registros recentes do meu diário:
{ctx}

Responda à minha pergunta: "{text}"
Se a resposta não estiver nos registros, diga que não encontrou. Seja direto e empático."""
        
        res = ask_gemini(prompt)
        reply(res)
        
    return {"status": "ok"}

# ============================================================
# WEBHOOK DE EMAIL (compat — substitui webhook_render antigo)
# ============================================================

@app.post("/webhook/email")
async def receive_email(payload: EmailPayload):
    try:
        execute(
            "INSERT INTO newsletters_inbox (subject, sender, content) VALUES (?, ?, ?)",
            (payload.subject, payload.sender, payload.content),
        )
        return {"status": "success", "message": "Newsletter salva!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
