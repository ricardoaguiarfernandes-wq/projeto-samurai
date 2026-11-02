"""
criar_projeto_samurai.py — Higiene de Código V1.x (revisão 2)

CHANGELOG desta revisão:
- FIX CRÍTICO: subprocess.run(..., text=True) estoura UnicodeDecodeError no
  Windows (cp1252 vs UTF-8 do git). Forçado encoding='utf-8', errors='replace'
  em TODAS as chamadas.
- Guard extra em scan_stage_secrets: `r.stdout or ""` (proteção contra None).
- Fixes 1–7 mantidos (idempotentes: já aplicados são skipped).
- 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
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
# 1. SEGURANÇA — varredura de segredos no stage
# ============================================================

PROIBIDOS_NOMES = {".env", ".env.local", ".env.production",
                   "config.json", "secrets.toml"}
PROIBIDOS_CAMINHOS = {".streamlit/secrets.toml", ".streamlit/config.toml"}

PADROES_SECRETOS = [
    (re.compile(r"AQ\.[A-Za-z0-9_\-]{20,}"), "Gemini API Key"),
    (re.compile(r"AIza[0-9A-Za-z_\-]{30,}"), "Google API Key"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "OpenAI Key"),
    (re.compile(r"postgres(?:ql)?://[^:]+:[^@\s]+@"), "Supabase/Postgres URL c/ credenciais"),
]


def _git_run_safe(args: list[str]) -> subprocess.CompletedProcess:
    """
    Wrapper ÚNICO para chamadas git com encoding robusto.
    - UTF-8 forçado (git fala UTF-8, Windows usa cp1252 por padrão).
    - errors='replace' evita UnicodeDecodeError em byte 0x81 etc.
    - .stdout/.stderr nunca serão None.
    """
    r = subprocess.run(
        ["git"] + args,
        cwd=BASE,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if r.stdout is None:
        r.stdout = ""
    if r.stderr is None:
        r.stderr = ""
    return r


def scan_stage_secrets() -> list[str]:
    """Retorna lista de problemas (vazia = OK). Nunca estoura exceção."""
    problemas: list[str] = []

    # (a) arquivos sensíveis no stage
    r = _git_run_safe(["diff", "--cached", "--name-only"])
    arquivos = [l.strip() for l in (r.stdout or "").splitlines() if l.strip()]
    for f in arquivos:
        nome = Path(f).name
        if nome in PROIBIDOS_NOMES or f in PROIBIDOS_CAMINHOS:
            problemas.append(f"Arquivo sensível no stage: {f}")

    # (b) padrões secretos em linhas adicionadas
    r = _git_run_safe(["diff", "--cached", "--unified=0"])
    diff = r.stdout or ""
    for linha in diff.splitlines():
        if not linha.startswith("+") or linha.startswith("+++"):
            continue
        for pat, nome in PADROES_SECRETOS:
            if pat.search(linha):
                problemas.append(f"Padrão secreto ({nome}) no diff: {linha[:80]}")
                break

    return problemas


# ============================================================
# 2. UTILITÁRIOS
# ============================================================

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write_validated(p: Path, content: str) -> None:
    """Grava com validação AST (só .py). Aborta se sintaxe quebrar."""
    if p.suffix == ".py":
        try:
            ast.parse(content, filename=str(p))
        except SyntaxError as e:
            print(f"[ABORTA] Sintaxe quebrada em {p}: {e}")
            sys.exit(1)
    p.write_text(content, encoding="utf-8")
    print(f"[OK] {p.relative_to(BASE)}")


# ============================================================
# 3. FIXES INDIVIDUAIS (cada um idempotente)
# ============================================================

def fix_webhook_flaredantic() -> None:
    """Guarda import de flaredantic em webhook_server.py."""
    p = BASE / "services" / "webhook_server.py"
    if not p.exists():
        print("[SKIP] webhook_server.py não existe.")
        return
    txt = read(p)

    if "HAS_FLARE" in txt:
        print("[SKIP] webhook_server.py — guard já aplicado.")
        return

    old = (
        "from flaredantic import FlareTunnel, TunnelConfig\n"
        "import threading\n"
    )
    new = (
        "import threading\n"
        "\n"
        "try:\n"
        "    from flaredantic import FlareTunnel, TunnelConfig\n"
        "    HAS_FLARE = True\n"
        "except ImportError:\n"
        "    HAS_FLARE = False\n"
        "    FlareTunnel = None\n"
        "    TunnelConfig = None\n"
    )
    if old not in txt:
        print("[SKIP] webhook_server.py — assinatura do import não bate.")
        return
    txt = txt.replace(old, new, 1)

    old_tunel = (
        'def iniciar_tunel():\n'
        '    """Inicia o túnel Cloudflare em segundo plano e exibe a URL."""\n'
        '    try:\n'
        '        config = TunnelConfig(port=8000)\n'
    )
    new_tunel = (
        'def iniciar_tunel():\n'
        '    """Inicia o túnel Cloudflare em segundo plano e exibe a URL."""\n'
        '    if not HAS_FLARE:\n'
        '        print("[AVISO] flaredantic nao instalado. Túnel Cloudflare desabilitado.")\n'
        '        print("        Webhook funcionara apenas em rede local (http://localhost:8000)")\n'
        '        print("        Para habilitar: pip install flaredantic")\n'
        '        return None\n'
        '    try:\n'
        '        config = TunnelConfig(port=8000)\n'
    )
    if old_tunel in txt:
        txt = txt.replace(old_tunel, new_tunel, 1)
    else:
        print("[AVISO] webhook_server.py — bloco iniciar_tunel não encontrado; só o import foi guardado.")

    write_validated(p, txt)


def fix_requirements_flaredantic() -> None:
    """Documenta flaredantic como opcional (comentado, não quebra pip)."""
    p = BASE / "requirements.txt"
    if not p.exists():
        print("[SKIP] requirements.txt não existe.")
        return
    txt = read(p)
    if "flaredantic" in txt:
        print("[SKIP] requirements.txt — flaredantic já documentado.")
        return
    marker = "youtube-transcript-api>=0.6.2\n"
    if marker not in txt:
        print("[SKIP] requirements.txt — marker não encontrado.")
        return
    bloco = (
        marker
        + "\n"
        + "# Tunnel Cloudflare para webhook local (opcional). Descomente se quiser usar:\n"
        + "# flaredantic>=0.0.5\n"
    )
    txt = txt.replace(marker, bloco, 1)
    p.write_text(txt, encoding="utf-8")
    print("[OK] requirements.txt — flaredantic documentado (comentado)")


def fix_schema_patrimony() -> None:
    """Adiciona DDL de patrimony_fixed_income em core/schema.py."""
    p = BASE / "core" / "schema.py"
    txt = read(p)
    if "patrimony_fixed_income" in txt:
        print("[SKIP] schema.py — patrimony_fixed_income já presente.")
        return
    marker = (
        '"""CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'expense_date TEXT NOT NULL, description TEXT NOT NULL, amount REAL NOT NULL, '
        'category TEXT, notes TEXT);""",'
    )
    if marker not in txt:
        print("[SKIP] schema.py — marker 'expenses' não encontrado.")
        return
    nova_linha = (
        "\n"
        '        """CREATE TABLE IF NOT EXISTS patrimony_fixed_income '
        '(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, rate TEXT);""",'
    )
    txt = txt.replace(marker, marker + nova_linha, 1)
    write_validated(p, txt)


def fix_patrimonio_page() -> None:
    """Remove criação redundante de tabela em 04_Patrimonio.py."""
    p = BASE / "ui" / "pages" / "04_Patrimonio.py"
    txt = read(p)
    alvo = (
        'execute("CREATE TABLE IF NOT EXISTS patrimony_fixed_income '
        '(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, amount REAL, rate TEXT)")\n'
    )
    if alvo not in txt:
        print("[SKIP] 04_Patrimonio.py — criação de tabela já removida.")
        return
    txt = txt.replace(alvo, "", 1)
    write_validated(p, txt)


def fix_delete_biblia_orfao() -> None:
    """Deleta ui/pages/09_Biblia.py (órfao, duplicado por 08_Religiao.py)."""
    p = BASE / "ui" / "pages" / "09_Biblia.py"
    if not p.exists():
        print("[SKIP] 09_Biblia.py já não existe.")
        return
    p.unlink()
    print("[OK] 09_Biblia.py DELETADO (era órfão e 100% duplicado por 08_Religiao.py)")


def fix_pdf_output() -> None:
    """Corrige output do PDF em 07_Consistencia.py (fpdf2 v2.7+ retorna bytearray)."""
    p = BASE / "ui" / "pages" / "07_Consistencia.py"
    txt = read(p)

    if "_pdf_result = pdf.output()" in txt:
        print("[SKIP] 07_Consistencia.py — PDF já corrigido.")
        return

    old = "        pdf_bytes = pdf.output(dest='S').encode('latin-1')"
    new = (
        "        _pdf_result = pdf.output()\n"
        "        if isinstance(_pdf_result, str):\n"
        "            pdf_bytes = _pdf_result.encode('latin-1')\n"
        "        else:\n"
        "            pdf_bytes = bytes(_pdf_result)"
    )

    if old not in txt:
        print("[SKIP] 07_Consistencia.py — linha alvo do PDF não encontrada.")
        return

    txt = txt.replace(old, new, 1)
    write_validated(p, txt)


def fix_religiao_checkbox() -> None:
    """Corrige bug em 08_Religiao.py: hábitos não podiam ser desmarcados."""
    p = BASE / "ui" / "pages" / "08_Religiao.py"
    txt = read(p)

    if "alterou_religiao" in txt:
        print("[SKIP] 08_Religiao.py — bug de checkbox já corrigido.")
        return

    old = (
        '    habits = query_all("SELECT h.id, h.name, COALESCE(l.done, 0) AS done FROM habits h LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ? WHERE h.pillar = \'Religião\' AND h.active = 1", (date.today().isoformat(),))\n'
        '    for h in habits:\n'
        '        if st.checkbox(h["name"], value=bool(h["done"])):\n'
        '            execute("INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, 1) ON CONFLICT(habit_id, log_date) DO UPDATE SET done = 1", (h["id"], date.today().isoformat()))'
    )
    new = (
        '    habits = query_all("SELECT h.id, h.name, COALESCE(l.done, 0) AS done FROM habits h LEFT JOIN habit_logs l ON l.habit_id = h.id AND l.log_date = ? WHERE h.pillar = \'Religião\' AND h.active = 1", (date.today().isoformat(),))\n'
        '    alterou_religiao = False\n'
        '    for h in habits:\n'
        '        novo = st.checkbox(h["name"], value=bool(h["done"]), key=f"religiao_habit_{h[\'id\']}")\n'
        '        if novo != bool(h["done"]):\n'
        '            execute("INSERT INTO habit_logs (habit_id, log_date, done) VALUES (?, ?, ?) ON CONFLICT(habit_id, log_date) DO UPDATE SET done = excluded.done", (h["id"], date.today().isoformat(), 1 if novo else 0))\n'
        '            alterou_religiao = True\n'
        '    if alterou_religiao:\n'
        '        st.rerun()'
    )

    if old not in txt:
        print("[SKIP] 08_Religiao.py — bloco de checkbox não encontrado.")
        return

    txt = txt.replace(old, new, 1)
    write_validated(p, txt)


# ============================================================
# 4. SYNC GIT + DEPLOY
# ============================================================

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("☁️  SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    # 1. Stage
    r = _git_run_safe(["add", "-A"])
    if r.returncode != 0:
        print(f"[ERRO] git add falhou:\n{r.stderr}")
        sys.exit(1)
    print("[OK] git add -A")

    # 2. Varredura de segredos
    problemas = scan_stage_secrets()
    if problemas:
        print("\n[ABORTA] SEGREDOS DETECTADOS NO STAGE:")
        for p in problemas:
            print(f"  ❌ {p}")
        print("\nRollback do stage...")
        _git_run_safe(["reset"])
        print("[ABORTA] Push cancelado. Remova os segredos e tente novamente.")
        sys.exit(1)
    print("[OK] Varredura de segredos: limpa")

    # 3. Commit
    msg = (
        "chore(v1.x): higiene — guard flaredantic, patrimony em schema, "
        "remove 09_Biblia orfao, fix PDF fpdf2, fix checkbox religiao"
    )
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

    # 4. Push
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode != 0:
        print(f"[ERRO] git push falhou:\n{r.stderr}")
        print("[DICA] Rode 'git pull --rebase' e tente novamente.")
        sys.exit(1)
    print("[OK] git push")

    # 5. Deploy hook (Render, opcional)
    hook = os.environ.get("RENDER_DEPLOY_HOOK_URL", "").strip()
    if hook:
        try:
            import requests
            resp = requests.get(hook, timeout=15)
            print(f"[OK] Deploy Render disparado (HTTP {resp.status_code})")
        except Exception as e:
            print(f"[AVISO] Falha ao disparar deploy Render: {e}")
    else:
        print("[INFO] RENDER_DEPLOY_HOOK_URL não configurada — push já dispara deploy automático.")


# ============================================================
# 5. MAIN
# ============================================================

def aplicar() -> None:
    print("=" * 60)
    print("⚔️  MELHORIA V1.x — HIGIENE DE CÓDIGO (rev 2)")
    print("=" * 60)

    etapas = [
        ("Guardar import flaredantic (webhook_server.py)", fix_webhook_flaredantic),
        ("Documentar flaredantic (requirements.txt)",      fix_requirements_flaredantic),
        ("Centralizar patrimony_fixed_income (schema.py)",  fix_schema_patrimony),
        ("Remover criação redundante (04_Patrimonio.py)",   fix_patrimonio_page),
        ("Deletar 09_Biblia.py (órfão)",                    fix_delete_biblia_orfao),
        ("Corrigir output PDF (07_Consistencia.py)",        fix_pdf_output),
        ("Corrigir checkboxes (08_Religiao.py)",            fix_religiao_checkbox),
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
    print("✅ MELHORIA V1.x CONCLUÍDA")
    print("=" * 60)


if __name__ == "__main__":
    aplicar()