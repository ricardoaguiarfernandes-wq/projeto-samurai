"""
criar_projeto_samurai.py — V2.6 (Blindagem do Webhook de Email e Integração ao Brief)

ENTREGAS:
1. SEGURANÇA: Adiciona verificação X-Webhook-Token na rota /webhook/email.
2. DB: Remove o HTML bruto e salva apenas texto limpo no banco.
3. LÓGICA: Impede e-mails duplicados.
4. INTEGRAÇÃO: O endpoint /api/brief agora lê os últimos e-mails e envia para a IA.

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

# ============================================================
# 1. API — Blindagem do Webhook e Integração ao Brief
# ============================================================
def fix_api_webhook_email() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "X-Webhook-Token" in txt:
        print("[SKIP] api_samurai.py — webhook já blindado.")
        return

    # 1.1 Atualizar a rota de email
    old_webhook = '''@app.post("/webhook/email")
async def receive_email(payload: EmailPayload):
    try:
        execute(
            "INSERT INTO newsletters_inbox (subject, sender, content) VALUES (?, ?, ?)",
            (payload.subject, payload.sender, payload.content),
        )
        return {"status": "success", "message": "Newsletter salva!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}'''

    new_webhook = '''@app.post("/webhook/email")
async def receive_email(payload: EmailPayload, x_webhook_token: str = Header(None)):
    # 1. Segurança
    expected_token = os.environ.get("WEBHOOK_EMAIL_TOKEN", "samurai-secret-email")
    if x_webhook_token != expected_token:
        raise HTTPException(status_code=401, detail="Token de webhook invalido.")

    try:
        # 2. Evitar duplicatas e limpar HTML
        import re
        from bs4 import BeautifulSoup
        
        # Limpa o HTML para texto puro
        soup = BeautifulSoup(payload.content, "html.parser")
        clean_content = soup.get_text(separator="\\n", strip=True)
        
        # Verifica se já existe (baseado no assunto e remetente)
        existe = query_one(
            "SELECT id FROM newsletters_inbox WHERE subject = ? AND sender = ?",
            (payload.subject, payload.sender)
        )
        
        if existe:
            return {"status": "ignored", "message": "Email duplicado."}

        # 3. Salva no banco
        execute(
            "INSERT INTO newsletters_inbox (subject, sender, content) VALUES (?, ?, ?)",
            (payload.subject, payload.sender, clean_content),
        )
        return {"status": "success", "message": "Newsletter limpa e salva!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}'''

    if old_webhook in txt:
        txt = txt.replace(old_webhook, new_webhook, 1)
    else:
        print("[AVISO] api_samurai.py — rota de email antiga não encontrada.")

    # 1.2 Injetar os e-mails no prompt do Brief
    old_prompt = '''    prompt = f"""Voce e o Mentor Samurai, sistema operacional pessoal do Ricardo.
Data: {today_iso}.
Dados do dia:'''

    new_prompt = '''    # Busca as notícias do dia para incluir no brief
    try:
        emails = query_all("SELECT subject, content FROM newsletters_inbox ORDER BY received_at DESC LIMIT 3")
        noticias_ctx = "\\n".join([f"[{e['subject']}] {e['content'][:1000]}" for e in emails])
    except Exception:
        noticias_ctx = "Nenhuma noticia recebida hoje."

    prompt = f"""Voce e o Mentor Samurai, sistema operacional pessoal do Ricardo.
Data: {today_iso}.

NOTICIAS DE HOJE (Newsletters):
{noticias_ctx}

Dados do dia:'''

    if old_prompt in txt:
        txt = txt.replace(old_prompt, new_prompt, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] api_samurai.py — bloco do prompt do brief não encontrado.")

# ============================================================
# 2. CRIAR SCRIPT PARA O POWER AUTOMATE
# ============================================================
def create_power_automate_guide() -> None:
    p = BASE / "power_automate.json"
    if p.exists():
        print("[SKIP] power_automate.json já existe.")
        return
    
    conteudo = '''{
  "instrucoes": "No Power Automate, crie um fluxo de 'Quando um novo e-mail chegar'. Adicione uma ação HTTP POST para o seu endpoint.",
  "URL": "https://samurai-webhook.onrender.com/webhook/email",
  "Method": "POST",
  "Headers": {
    "Content-Type": "application/json",
    "X-Webhook-Token": "samurai-secret-email"
  },
  "Body": {
    "subject": "@{triggerOutputs()?['body/subject']}",
    "sender": "@{triggerOutputs()?['body/from']}",
    "content": "@{triggerOutputs()?['body/body']}"
  }
}'''
    p.write_text(conteudo, encoding="utf-8")
    print(f"[OK] {p.name} (guia para configurar o Power Automate)")

# ============================================================
# SYNC GIT
# ============================================================
def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: blinda webhook de email, limpa html e integra ao brief diario"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

# ============================================================
# MAIN
# ============================================================
def aplicar() -> None:
    print("=" * 60)
    print("V2.6 — BLINDAGEM E INTEGRAÇÃO DO WEBHOOK DE E-MAIL")
    print("=" * 60)

    etapas = [
        ("Blindar API e integrar brief (api_samurai.py)", fix_api_webhook_email),
        ("Gerar guia do Power Automate", create_power_automate_guide),
    ]

    for i, (label, fn) in enumerate(etapas, 1):
        print(f"\n[{i}/{len(etapas)}] {label}")
        fn()

    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que você precisa fazer agora no Power Automate:")
    print("1. Na ação 'HTTP', adicione um novo Header chamado 'X-Webhook-Token'")
    print("2. O valor do token é: samurai-secret-email")
    print("   (Você pode mudar isso no Render, na variável WEBHOOK_EMAIL_TOKEN).")
    print("3. O Power Automate deve enviar o body EXATAMENTE no formato JSON.")
    print("4. Agora, quando a IA gerar o Brief das 6h, ela vai ler as notícias que chegaram!")

if __name__ == "__main__":
    aplicar()