"""
criar_projeto_samurai.py — V2.0 Step 1: API do Samurai

ENTREGAS:
1. FIX core/database.py : get_db_url() e is_postgres() agora leem SUPABASE_URL
                          via os.environ (Fallback p/ Render/CI, mantém st.secrets)
2. FIX core/schema.py   : get_ddl() usa core.database.is_postgres() (não st.secrets)
3. FIX services/ai.py   : get_api_key() agora lee GEMINI_API_KEY via os.environ
                          (Fallback p/ Render/CI, mantém st.secrets e config.json)
4. NEW api_samurai.py   : FastAPI unificada V2.0 — auth Bearer, 10 endpoints
                          (/api/status, /api/habits, /api/checkin, /api/portfolio,
                          /api/brief, /webhook/email + /health)
5. NEW render.yaml      : infra-as-code (build, start, env vars)
6. FIX webhook_render.py: re-export de api_samurai:app (Render atual continua OK)

REGRA DE OURO: 'gemini-3.5-flash-lite' é INTOCÁVEL.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent


# ============================================================
# SEGURANÇA — varredura de segredos no stage
# ============================================================

PROIBIDOS_NOMES = {".env", ".env.local", ".env.production",
                   "config.json", "secrets.toml"}
PROIBIDOS_CAMINHOS = {".streamlit/secrets.toml", ".streamlit/config.toml"}

PADROES_SECRETOS = [
    (re.compile(r"AQ\.[A-Za-z0-9_\-]{20,}"), "Gemini API Key"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{30,}"), "Google API Key"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI Key"),
    (re.compile(r"postgres(?:ql)?://[^:]+:[^@\s]+@"), "Supabase URL c/ credenciais"),
]


def _git_run_safe(args: list[str]) -> subprocess.CompletedProcess:
    """Wrapper git com UTF-8 forçado (evita UnicodeDecodeError no Windows)."""
    r = subprocess.run(
        ["git"] + args, cwd=BASE, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )
    if r.stdout is None: r.stdout = ""
    if r.stderr is None: r.stderr = ""
    return r


def scan_stage_secrets() -> list[str]:
    problemas: list[str] = []

    r = _git_run_safe(["diff", "--cached", "--name-only"])
    for f in (r.stdout or "").splitlines():
        f = f.strip()
        if not f: continue
        if Path(f).name in PROIBIDOS_NOMES or f in PROIBIDOS_CAMINHOS:
            problemas.append(f"Arquivo sensível no stage: {f}")

    r = _git_run_safe(["diff", "--cached", "--unified=0"])
    for linha in (r.stdout or "").splitlines():
        if not linha.startswith("+") or linha.startswith("+++"):
            continue
        for pat, nome in PADROES_SECRETOS:
            if pat.search(linha):
                problemas.append(f"Padrão secreto ({nome}): {linha[:80]}")
                break
    return problemas


# ============================================================
# UTILITÁRIOS
# ============================================================

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write_validated(p: Path, content: str) -> None:
    if p.suffix == ".py":
        try:
            ast.parse(content, filename=str(p))
        except SyntaxError as e:
            print(f"[ABORTA] Sintaxe quebrada em {p}: {e}")
            sys.exit(1)
    p.write_text(content, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")


# ============================================================
# FIX 1 — core/database.py: env fallback
# ============================================================

def fix_database_env_fallback() -> None:
    p = BASE / "core" / "database.py"
    txt = read(p)

    if 'os.environ.get("SUPABASE_URL"' in txt:
        print("[SKIP] database.py — env fallback já aplicado.")
        return

    # get_db_url
    old_get = (
        'def get_db_url():\n'
        '    try:\n'
        '        if "SUPABASE_URL" in st.secrets:\n'
        '            return st.secrets["SUPABASE_URL"]\n'
        '    except Exception:\n'
        '        pass\n'
        '    return None\n'
    )
    new_get = (
        'def get_db_url():\n'
        '    # 1) Streamlit Cloud\n'
        '    try:\n'
        '        if "SUPABASE_URL" in st.secrets:\n'
        '            return st.secrets["SUPABASE_URL"]\n'
        '    except Exception:\n'
        '        pass\n'
        '    # 2) Variavel de ambiente (Render, CI, local)\n'
        '    import os\n'
        '    url = os.environ.get("SUPABASE_URL", "").strip()\n'
        '    if url:\n'
        '        return url\n'
        '    return None\n'
    )
    if old_get not in txt:
        print("[AVISO] database.py — bloco get_db_url nao encontrado.")
        return
    txt = txt.replace(old_get, new_get, 1)

    # is_postgres
    old_pg = (
        'def is_postgres() -> bool:\n'
        '    try:\n'
        '        return "SUPABASE_URL" in st.secrets and HAS_PG\n'
        '    except Exception:\n'
        '        return False\n'
    )
    new_pg = (
        'def is_postgres() -> bool:\n'
        '    if not HAS_PG:\n'
        '        return False\n'
        '    try:\n'
        '        if "SUPABASE_URL" in st.secrets:\n'
        '            return True\n'
        '    except Exception:\n'
        '        pass\n'
        '    import os\n'
        '    return bool(os.environ.get("SUPABASE_URL", "").strip())\n'
    )
    if old_pg not in txt:
        print("[AVISO] database.py — bloco is_postgres nao encontrado.")
        return
    txt = txt.replace(old_pg, new_pg, 1)

    write_validated(p, txt)


# ============================================================
# FIX 2 — core/schema.py: usa is_postgres()
# ============================================================

def fix_schema_env_fallback() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)

    if "from core.database import is_postgres" in txt:
        print("[SKIP] schema.py — já usa is_postgres().")
        return

    old = (
        'def get_ddl():\n'
        '    is_pg = False\n'
        '    try:\n'
        '        import streamlit as st\n'
        '        is_pg = "SUPABASE_URL" in st.secrets\n'
        '    except Exception: pass\n'
        '\n'
        '    ddl_base = [\n'
    )
    new = (
        'def get_ddl():\n'
        '    from core.database import is_postgres\n'
        '    is_pg = is_postgres()\n'
        '\n'
        '    ddl_base = [\n'
    )
    if old not in txt:
        print("[AVISO] schema.py — bloco get_ddl nao encontrado.")
        return
    txt = txt.replace(old, new, 1)
    write_validated(p, txt)


# ============================================================
# FIX 3 — services/ai.py: env fallback
# ============================================================

def fix_ai_env_fallback() -> None:
    p = BASE / "services" / "ai.py"
    txt = read(p)

    if 'os.environ.get("GEMINI_API_KEY"' in txt:
        print("[SKIP] ai.py — env fallback já aplicado.")
        return

    old = (
        'def get_api_key() -> str:\n'
        '    # Tenta pegar dos Secrets do Streamlit Cloud (Nuvem)\n'
        '    try:\n'
        '        if "gemini_api_key" in st.secrets:\n'
        '            return st.secrets["gemini_api_key"]\n'
        '    except Exception:\n'
        '        pass\n'
        '        \n'
        '    # Fallback local (config.json)\n'
        '    if CONFIG_PATH.exists():\n'
        '        try:\n'
        '            with open(CONFIG_PATH, "r", encoding="utf-8") as f:\n'
        '                return json.load(f).get("gemini_api_key", "")\n'
        '        except Exception:\n'
        '            pass\n'
        '    return ""\n'
    )
    new = (
        'def get_api_key() -> str:\n'
        '    # 1) Streamlit Cloud\n'
        '    try:\n'
        '        if "gemini_api_key" in st.secrets:\n'
        '            return st.secrets["gemini_api_key"]\n'
        '    except Exception:\n'
        '        pass\n'
        '    # 2) Variavel de ambiente (Render, CI, local)\n'
        '    import os\n'
        '    env_key = os.environ.get("GEMINI_API_KEY", "").strip()\n'
        '    if env_key:\n'
        '        return env_key\n'
        '    # 3) Fallback local (config.json)\n'
        '    if CONFIG_PATH.exists():\n'
        '        try:\n'
        '            with open(CONFIG_PATH, "r", encoding="utf-8") as f:\n'
        '                return json.load(f).get("gemini_api_key", "")\n'
        '        except Exception:\n'
        '            pass\n'
        '    return ""\n'
    )
    if old not in txt:
        print("[AVISO] ai.py — bloco get_api_key nao encontrado (conservador: nao mexe).")
        return
    txt = txt.replace(old, new, 1)
    write_validated(p, txt)


# ============================================================
# NEW 4 — api_samurai.py
# ============================================================

API_CODE = '''"""
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
    total_habits = (query_one(
        "SELECT COUNT(*) AS c FROM habits WHERE active = 1"
    ) or {}).get("c") or 0
    done_today = (query_one(
        "SELECT COUNT(*) AS c FROM habit_logs WHERE log_date = ? AND done = 1",
        (today_iso,),
    ) or {}).get("c") or 0

    checkins = query_all(
        "SELECT energy, stress, sleep_hours FROM daily_checkins WHERE checkin_date >= ?",
        (week_ago,),
    )
    logs = query_all("SELECT done FROM habit_logs WHERE log_date >= ?", (week_ago,))
    done = sum(1 for r in logs if r["done"])
    possible = total_habits * 7
    taxa = done / possible if possible > 0 else 0.0

    if checkins:
        avg_energy = sum(r["energy"] for r in checkins) / len(checkins)
        avg_stress = sum(r["stress"] for r in checkins) / len(checkins)
        avg_sleep = sum(r["sleep_hours"] for r in checkins) / len(checkins)
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
    status = get_status()
    habits = list_habits()["habits"]
    pending = [h["name"] for h in habits if not h["done"]]

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
    m = _re.search(r"\\{.*\\}", raw, _re.DOTALL)
    if not m:
        return {"error": "IA nao retornou JSON", "raw": raw[:500]}
    try:
        brief = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        return {"error": f"JSON invalido: {e}", "raw": raw[:500]}

    # Texto pronto para WhatsApp/Telegram
    try:
        txt = (
            f"{brief.get('greeting', 'Bom dia.')}\\n\\n"
            f"Risco: {brief.get('burnout_alert', '?')}\\n\\n"
            f"Top 3 prioridades:\\n"
            + "\\n".join(f"  {i+1}. {p}" for i, p in enumerate(brief.get("top_3_priorities", [])))
            + f"\\n\\nTreino: {brief.get('training', '-')}\\n\\n"
            f"Versiculo: {brief.get('verse_of_the_day', '-')}\\n\\n"
            f"{brief.get('closing', '')}"
        )
    except Exception:
        txt = ""

    brief["text"] = txt
    return brief


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
'''


def create_api_samurai() -> None:
    p = BASE / "api_samurai.py"
    if p.exists():
        print("[SKIP] api_samurai.py já existe.")
        return
    write_validated(p, API_CODE)


# ============================================================
# NEW 5 — render.yaml
# ============================================================

RENDER_YAML = '''services:
  - type: web
    name: samurai-api
    runtime: python
    plan: free
    region: oregon
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api_samurai:app --host 0.0.0.0 --port $PORT
    autoDeploy: true
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      - key: SUPABASE_URL
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: SAMURAI_API_TOKEN
        sync: false
      - key: RENDER_DEPLOY_HOOK_URL
        sync: false
'''


def create_render_yaml() -> None:
    p = BASE / "render.yaml"
    if p.exists():
        print("[SKIP] render.yaml já existe.")
        return
    p.write_text(RENDER_YAML, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")


# ============================================================
# FIX 6 — webhook_render.py: re-export
# ============================================================

WEBHOOK_RENDER_REEXXPORT = '''"""
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
'''


def fix_webhook_render_reexport() -> None:
    p = BASE / "webhook_render.py"
    if not p.exists():
        print("[SKIP] webhook_render.py nao existe.")
        return
    txt = read(p)
    if "from api_samurai import app" in txt:
        print("[SKIP] webhook_render.py — re-export já aplicado.")
        return
    write_validated(p, WEBHOOK_RENDER_REEXXPORT)


# ============================================================
# SYNC GIT + DEPLOY
# ============================================================

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    r = _git_run_safe(["add", "-A"])
    if r.returncode != 0:
        print(f"[ERRO] git add falhou:\n{r.stderr}")
        sys.exit(1)
    print("[OK] git add -A")

    problemas = scan_stage_secrets()
    if problemas:
        print("\n[ABORTA] SEGREDOS DETECTADOS NO STAGE:")
        for p_ in problemas:
            print(f"  X {p_}")
        print("\nRollback do stage...")
        _git_run_safe(["reset"])
        print("[ABORTA] Push cancelado.")
        sys.exit(1)
    print("[OK] Varredura de segredos: limpa")

    msg = "feat(v2.0): API do Samurai (FastAPI) + env fallback + render.yaml"
    r = _git_run_safe(["commit", "-m", msg])
    if r.returncode != 0:
        saida = (r.stdout or "") + (r.stderr or "")
        if "nothing to commit" in saida or "no changes added" in saida:
            print("[SKIP] Nada para commitar. Continuando para push.")
        else:
            print(f"[ERRO] git commit falhou:\n{r.stdout}\n{r.stderr}")
            sys.exit(1)
    else:
        print("[OK] git commit")

    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode != 0:
        print(f"[ERRO] git push falhou:\n{r.stderr}")
        sys.exit(1)
    print("[OK] git push")

    hook = os.environ.get("RENDER_DEPLOY_HOOK_URL", "").strip()
    if hook:
        try:
            import requests
            resp = requests.get(hook, timeout=15)
            print(f"[OK] Deploy Render disparado (HTTP {resp.status_code})")
        except Exception as e:
            print(f"[AVISO] Falha ao disparar deploy Render: {e}")
    else:
        print("[INFO] RENDER_DEPLOY_HOOK_URL nao configurada (push ja dispara).")


# ============================================================
# MAIN
# ============================================================

def aplicar() -> None:
    print("=" * 60)
    print("V2.0 STEP 1 — API DO SAMURAI")
    print("=" * 60)

    etapas = [
        ("Fix env fallback (core/database.py)",       fix_database_env_fallback),
        ("Fix env fallback (core/schema.py)",         fix_schema_env_fallback),
        ("Fix env fallback (services/ai.py)",         fix_ai_env_fallback),
        ("Criar API unificada (api_samurai.py)",      create_api_samurai),
        ("Criar infra Render (render.yaml)",          create_render_yaml),
        ("Shim de compat (webhook_render.py)",        fix_webhook_render_reexport),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        try:
            fn()
        except SystemExit:
            raise
        except Exception as e:
            print(f"[ABORTA] Erro em '{label}': {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    sync_git()

    print("\n" + "=" * 60)
    print("OK — V2.0 STEP 1 CONCLUIDO")
    print("=" * 60)
    print("\nPROXIMOS PASSOS MANUAIS (no Render Dashboard):")
    print("  1. Configurar env var SAMURAI_API_TOKEN (invente uma senha longa)")
    print("  2. Configurar GEMINI_API_KEY (mesma chave do config.json)")
    print("  3. Configurar SUPABASE_URL (ja deve existir)")
    print("  4. (opcional) RENDER_DEPLOY_HOOK_URL para deploy manual")
    print("\n  Testar localmente:")
    print("    uvicorn api_samurai:app --reload --port 8000")
    print("    curl http://localhost:8000/health")
    print("    curl -H 'Authorization: Bearer SEU_TOKEN' http://localhost:8000/api/status")


if __name__ == "__main__":
    aplicar()