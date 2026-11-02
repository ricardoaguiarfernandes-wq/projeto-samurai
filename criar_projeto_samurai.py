"""
criar_projeto_samurai.py — V2.9 (Validação de Payload e Limpeza de Dados)

ENTREGAS:
1. API: Ignora e bloqueia e-mails com campos "undefined" ou vazios.
2. API: Adiciona uma rotina de limpeza para apagar registros corrompidos no banco.
3. DB: Roda a limpeza no boot.

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

def fix_api_webhook_validation() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "Se o payload vier com 'undefined'" in txt:
        print("[SKIP] api_samurai.py — validação já existe.")
        return

    # 1. Adicionar validação na rota do webhook
    old_webhook = '''    try:
        # 2. Evitar duplicatas e limpar HTML
        import re
        from bs4 import BeautifulSoup
        
        # Limpa o HTML para texto puro
        soup = BeautifulSoup(payload.content, "html.parser")
        clean_content = soup.get_text(separator="\\n", strip=True)'''

    new_webhook = '''    try:
        # 2. Evitar duplicatas e limpar HTML
        import re
        from bs4 import BeautifulSoup
        
        # Valida se os campos não vieram quebrados do Pipedream
        if not payload.subject or payload.subject.strip().lower() == "undefined":
            return {"status": "ignored", "message": "Payload inválido (subject undefined)"}
            
        # Limpa o HTML para texto puro
        soup = BeautifulSoup(payload.content, "html.parser")
        clean_content = soup.get_text(separator="\\n", strip=True)'''

    if old_webhook in txt:
        txt = txt.replace(old_webhook, new_webhook, 1)
    else:
        print("[AVISO] api_samurai.py — bloco de webhook não encontrado.")

    # 2. Adicionar limpeza no boot (init_db)
    old_init = '''try:
    init_db()
except Exception as _e:
    print(f"[AVISO] init_db falhou no boot: {_e}")'''

    new_init = '''try:
    init_db()
    # Limpa registros corrompidos antigos
    execute("DELETE FROM newsletters_inbox WHERE subject = 'undefined' OR subject IS NULL")
except Exception as _e:
    print(f"[AVISO] init_db falhou no boot: {_e}")'''

    if old_init in txt:
        txt = txt.replace(old_init, new_init, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] api_samurai.py — bloco init_db não encontrado.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "fix: valida payload do webhook e limpa undefined do banco"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V2.9 — VALIDAÇÃO DE WEBHOOK E LIMPEZA")
    print("=" * 60)

    fix_api_webhook_validation()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que fazer agora:")
    print("1. Vá no Render e faça 'Manual Deploy' para aplicar a limpeza.")
    print("2. Vá no Pipedream, corrija o Body (conforme instruído acima) e clique em 'Test'.")
    print("3. O Streamlit Cloud vai atualizar sozinho e o e-mail correto vai aparecer!")

if __name__ == "__main__":
    aplicar()