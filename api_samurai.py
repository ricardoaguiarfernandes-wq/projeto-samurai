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

from fastapi import Depends, FastAPI, Header, HTTPException, BackgroundTasks
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

    # 1. Calcula o treino do dia baseado na rotação
    treino_hoje = "Treino não configurado"
    try:
        settings = query_one("SELECT workout_split, workout_start_date FROM user_settings WHERE id = 1")
        if settings and settings.get("workout_start_date"):
            from datetime import datetime
            start_dt = datetime.strptime(settings["workout_start_date"], "%Y-%m-%d").date()
            dias = (date.today() - start_dt).days
            split = settings["workout_split"]
            
            if "Push/Pull/Legs + Corrida" in split:
                seq = ["Push (Peito, Ombro, Tríceps)", "Legs (Pernas)", "Pull (Costas, Bíceps)", "Corrida (Cardio)"]
            elif "ABC" in split:
                seq = ["A (Peito, Tríceps, Ombro)", "B (Costas, Bíceps)", "C (Pernas)", "Descanso"]
            elif "Calistenia - PPL" in split:
                seq = ["Push", "Pull", "Legs", "Descanso"]
            else:
                seq = ["Full Body", "Descanso"]
                
            treino_hoje = seq[dias % len(seq)]
    except Exception as e:
        print(f"Erro ao calcular treino: {e}")

    # 2. Busca as notícias do dia
    try:
        emails = query_all("SELECT subject, content FROM newsletters_inbox ORDER BY received_at DESC LIMIT 3")
        noticias_ctx = "\n".join([f"[{e['subject']}] {e['content'][:800]}" for e in emails])
    except Exception:
        noticias_ctx = "Nenhuma noticia recebida hoje."

    # 3. Busca o status da carteira
    try:
        portfolio = query_all("SELECT ticker, quantity FROM portfolio LIMIT 5")
        carteira_ctx = ", ".join([f"{p['ticker']} ({p['quantity']})" for p in portfolio]) if portfolio else "Carteira vazia."
    except Exception:
        carteira_ctx = "Erro ao ler carteira."

    # 4. Busca as missões de carreira pendentes
    try:
        missoes = query_all("SELECT task FROM career_missions WHERE mission_date = ? AND completed = 0", (today_iso,))
        carreira_ctx = "\n".join([f"- {m['task']}" for m in missoes]) if missoes else "Nenhuma missão pendente."
    except Exception:
        carreira_ctx = "Erro ao ler carreira."

    prompt = f"""Atue como o Conselho de Mestres do Projeto Samurai. Você é a fusão de três especialistas:
1. Mestre Financeiro (Foco: Proteção patrimonial, notícias e longo prazo).
2. Mestre Treinador (Foco: Hipertrofia, cardio, recuperação e Burnout).
3. Mestre Filósofo COF (Foco: Disciplina, estoicismo e consistência).

Sua missão é debater internamente os dados do dia e gerar uma diretriz unificada para o Ricardo.

DADOS DO DIA ({today_iso}):
- Check-in de Hoje: {status["checkin"] or "não realizado"}
- Burnout (7d): {status["burnout"]["score"]}/100 (Energia: {status["burnout"]["avg_energy"]}, Sono: {status["burnout"]["avg_sleep"]}h, Estresse: {status["burnout"]["avg_stress"]})
- Hábitos Pendentes: {pending if pending else "todos concluídos"}
- Treino Programado: {treino_hoje}
- Missões de Carreira (Survey): 
{carreira_ctx}

CONTEXTO EXTERNO:
- Notícias Recentes: 
{noticias_ctx}
- Carteira de Investimentos: {carteira_ctx}

REGRAS DO DEBATE (Você deve aplicar isso na sua resposta):
1. **Mestre Financeiro:** Se as notícias mostrarem crise ou a carteira estiver vazia, ele dirá para segurar a emoção e focar em aprender, não em gastar.
2. **Mestre Treinador:** Se o Burnout for Alto/Crítico (>60) ou o sono <6h, ele DEVE vetar treinos pesados. O Treino deve ser alterado para "Recuperação/Mobilidade", ignorando a rotação original.
3. **Mestre Filósofo:** Ele vai equilibrar os dois, focando na constância e não na intensidade hoje.

Sua resposta DEVE ser um JSON válido com EXATAMENTE estas chaves (sem texto antes ou depois):
{{
  "greeting": "<cumprimento curto, 1 linha, tom de mestre>",
  "burnout_alert": "<Baixo|Medio|Alto|Critico>",
  "top_3_priorities": ["<prioridade 1>", "<prioridade 2>", "<prioridade 3>"],
  "training": "<recomendacao de treino do dia, adaptada pelo Treinador>",
  "verse_of_the_day": "<referencia biblica + versiculo curto, sem inventar>",
  "closing": "<frase de encerramento, 1 linha, tom samurai>"
}}

REGRAS ESTRITAS:
- NUNCA use "ou". Crave a escolha.
- Se o Treinador alterou o treino por causa do Burnout, explique rapidamente no campo "training".
- O campo "verse_of_the_day" deve ser real.
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
    
    # Salva no banco para aparecer no Streamlit
    try:
        execute(
            "INSERT INTO daily_briefs (brief_date, content) VALUES (?, ?) ON CONFLICT(brief_date) DO UPDATE SET content=excluded.content",
            (today_iso, txt)
        )
    except Exception as e:
        print(f"Erro ao salvar brief no banco: {e}")

    return brief



# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS (Câmara, Senado, ALERJ, Macaé)
# ============================================================

# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS
# ============================================================

# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS
# ============================================================

# ============================================================
# NOTÍCIAS LEGISLATIVAS DIÁRIAS (Com Resumo IA)
# ============================================================
@app.get("/api/daily-news", dependencies=[Depends(require_token)])
def daily_news():
    import feedparser
    import requests
    from bs4 import BeautifulSoup
    from services.ai import ask_gemini

    noticias_brutas = []
    links_vistos = set()

    # 1. Câmara dos Deputados (RSS)
    try:
        feed = feedparser.parse("https://www.camara.leg.br/noticias/rss/ultimas-noticias")
        for entry in feed.entries[:3]:
            resumo = getattr(entry, 'summary', '')
            # Limpa HTML do resumo
            clean_resumo = BeautifulSoup(resumo, "html.parser").get_text(strip=True)
            noticias_brutas.append(f"FONTE: Câmara\nTÍTULO: {entry.title}\nRESUMO: {clean_resumo}")
    except Exception as e:
        print(f"Erro Câmara RSS: {e}")

    # 2. Senado Federal (RSS)
    try:
        feed = feedparser.parse("https://www12.senado.leg.br/noticias/RSS")
        for entry in feed.entries[:3]:
            resumo = getattr(entry, 'summary', '')
            clean_resumo = BeautifulSoup(resumo, "html.parser").get_text(strip=True)
            noticias_brutas.append(f"FONTE: Senado\nTÍTULO: {entry.title}\nRESUMO: {clean_resumo}")
    except Exception as e:
        print(f"Erro Senado RSS: {e}")

    # 3. ALERJ (Scraping)
    try:
        r = requests.get("https://www.alerj.rj.gov.br/Comunicacao/SalaDeImprensa/Noticias", timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            if "Noticia" in a["href"] or "noticias" in a["href"]:
                titulo = a.get_text(strip=True)
                if titulo and len(titulo) > 30 and not titulo.startswith("http"):
                    if titulo not in links_vistos:
                        links_vistos.add(titulo)
                        noticias_brutas.append(f"FONTE: ALERJ\nTÍTULO: {titulo}\nRESUMO: Notícia do site da ALERJ.")
                    if len([n for n in noticias_brutas if "ALERJ" in n]) >= 2:
                        break
    except Exception as e:
        print(f"Erro ALERJ scraping: {e}")

    # 4. Câmara de Macaé (Scraping)
    try:
        r = requests.get("https://cmmacae.rj.gov.br/noticias/", timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        for h in soup.find_all(["h2", "h3", "h4"]):
            titulo = h.get_text(strip=True)
            if titulo and len(titulo) > 30:
                if titulo not in links_vistos:
                    links_vistos.add(titulo)
                    noticias_brutas.append(f"FONTE: Macaé\nTÍTULO: {titulo}\nRESUMO: Notícia do site da Câmara de Macaé.")
                if len([n for n in noticias_brutas if "Macaé" in n]) >= 2:
                    break
    except Exception as e:
        print(f"Erro Macaé scraping: {e}")

    if not noticias_brutas:
        return {"text": "📰 Nenhuma notícia encontrada no momento."}

    # Agora, enviamos tudo para a IA mastigar e resumir
    texto_bruto_concatenado = "\n\n---\n\n".join(noticias_brutas)
    
    prompt = f"""Atue como o Analista Político do Projeto Samurai.
Abaixo estão as notícias brutas coletadas hoje dos sites oficiais.

Sua missão:
1. Para CADA notícia, crie um resumo explicativo curto (2 a 3 linhas).
2. O resumo deve explicar "o que aconteceu" e "qual o impacto prático" para o cidadão.
3. Formate a saída como uma lista em Markdown (bullet points). Use negrito no título e texto normal no resumo.
4. Organize por fonte (Câmara, Senado, Macaé, ALERJ) se possível.
5. Seja direto, sem enrolação e sem introduções (não escreva "aqui estão as notícias").

NOTÍCIAS BRUTAS:
{texto_bruto_concatenado}
"""

    try:
        resumo_final = ask_gemini(prompt)
        texto_final = "🏛️ **Notícias Legislativas Resumidas**\n\n" + resumo_final
    except Exception as e:
        texto_final = "Erro ao gerar resumo com a IA. Aqui estão os títulos brutos:\n\n" + texto_bruto_concatenado

    return {"text": texto_final}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
