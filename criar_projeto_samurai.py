"""
criar_projeto_samurai.py — V5.1 (Conselho de Mestres - Injeção Segura)

ENTREGAS:
1. FIX: Remove o Regex e usa corte de string (find/slice) para evitar erros de sintaxe no arquivo gerado.
2. API: Implementa o Conselho de Mestres (Financeiro, Treinador e Filósofo) no endpoint /api/brief.

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

def _git_run_safe(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git"] + args, cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)

def read(p: Path) -> str: return p.read_text(encoding="utf-8")
def write_validated(p: Path, content: str) -> None:
    if p.suffix == ".py":
        try: ast.parse(content, filename=str(p))
        except SyntaxError as e:
            print(f"[ABORTA] Sintaxe quebrada em {p}: {e}"); sys.exit(1)
    p.write_text(content, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")

def fix_api_multi_agents() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "Conselho de Mestres" in txt:
        print("[SKIP] api_samurai.py — conselho já implementado.")
        return

    # Usando raw string (r''') para não estourar os caracteres de escape do Python
    new_brief_code = r'''@app.get("/api/brief", dependencies=[Depends(require_token)])
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

'''

    # Usa corte de string em vez de Regex para evitar problemas de escape
    start_marker = '@app.get("/api/brief", dependencies=[Depends(require_token)])'
    end_marker = '# ============================================================\n# WEBHOOK DO TELEGRAM'
    
    start_idx = txt.find(start_marker)
    end_idx = txt.find(end_marker)

    if start_idx != -1 and end_idx != -1:
        # Mantém o que está antes do brief, insere o novo brief e mantém o resto do arquivo
        txt = txt[:start_idx] + new_brief_code + "\n" + txt[end_idx:]
        write_validated(p, txt)
    else:
        print("[ERRO] Não foi possível localizar os marcadores para injeção do Conselho.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat(api): conselho de mestres multi-agentes e injecao segura sem regex"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V5.1 — CONSELHO DE MESTRES (INJEÇÃO SEGURA)")
    print("=" * 60)

    fix_api_multi_agents()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Render atualizar (1-2 min).")
    print("2. Vá no GitHub Actions e clique em 'Run workflow' para forçar um novo Brief.")
    print("3. A mensagem no Telegram vai refletir o debate dos 3 Mestres.")

if __name__ == "__main__":
    aplicar()