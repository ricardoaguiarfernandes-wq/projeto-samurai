"""
aplicar_patch.py — Aplica patches + sincroniza com servidor (GitHub + Cloud).
Ordem corrigida: add -> commit -> pull -> push.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

# =============================================================================
# CONFIG
# =============================================================================
BASE = Path(__file__).resolve().parent
WINDOW_TITLE   = "Projeto Samurai"
INICIAR_BAT    = BASE / "INICIAR.bat"

PADROES_SECRETOS = [
    re.compile(r"AQ\.Ab8RN6[A-Za-z0-9_\-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"postgresql://[^:\s]+:[^@\s]+@"),
]
ARQUIVOS_PROIBIDOS = {"config.json", ".env", "secrets.toml"}
PREFIXO_MD_GERADO = "PROJETO_SAMURAI"

# =============================================================================
# PATCHES
# =============================================================================
PATCHES = [
    {
        "arquivo": "core/database.py",
        "validar_python": True,
        "descricao": "RETURNING id so quando a tabela tem coluna 'id'",
        "antigo": """            if is_pg:
                sql_upper = sql.upper()
                if sql_upper.strip().startswith("INSERT") and "RETURNING" not in sql_upper:
                    sql += " RETURNING id"
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cur.execute(sql, params)
                conn.commit()
                try:
                    res = cur.fetchone()
                    return res["id"] if res else 0
                except Exception:
                    return 0
            else:""",
        "novo": """            if is_pg:
                sql_upper = sql.upper().strip()
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                if sql_upper.startswith("INSERT") and "RETURNING" not in sql_upper:
                    # === PATCH SAMURAI: RETURNING ===
                    try:
                        cur.execute(sql + " RETURNING id", params)
                        conn.commit()
                        try:
                            res = cur.fetchone()
                            return res["id"] if res else 0
                        except Exception:
                            return 0
                    except psycopg2.errors.UndefinedColumn:
                        conn.rollback()
                        cur.execute(sql, params)
                        conn.commit()
                        return 0
                else:
                    cur.execute(sql, params)
                    conn.commit()
                    try:
                        res = cur.fetchone()
                        if res:
                            try:
                                return res["id"]
                            except (KeyError, TypeError):
                                return 0
                        return 0
                    except Exception:
                        return 0
            else:""",
    },
    {
        "arquivo": "gerar_codigo.py",
        "antigo": 'OUTPUT = BASE / "PROJETO_SAMURAI.md"',
        "novo": (
            'OUTPUT = BASE / "PROJETO_SAMURAI.md"\n'
            '# === PATCH SAMURAI: SEGREDOS ===\n'
            'ARQUIVOS_PROIBIDOS = {"config.json", "secrets.toml", ".env"}\n'
            '# ================================'
        ),
        "descricao": "gerar_codigo.py: define ARQUIVOS_PROIBIDOS",
        "validar_python": True,
    },
    {
        "arquivo": "gerar_codigo.py",
        "antigo": (
            "def is_ignored(path: Path) -> bool:\n"
            "    if any(part in IGNORE_DIRS for part in path.parts):"
        ),
        "novo": (
            "def is_ignored(path: Path) -> bool:\n"
            "    if path.name in ARQUIVOS_PROIBIDOS:  # === PATCH SAMURAI: SEGREDOS ===\n"
            "        return True\n"
            "    if any(part in IGNORE_DIRS for part in path.parts):"
        ),
        "descricao": "gerar_codigo.py: filtra config/secrets do mapa",
        "validar_python": True,
    },
    {
        "arquivo": ".gitignore",
        "antigo": "# Sistema\n.DS_Store\nThumbs.db",
        "novo": (
            "# Sistema\n.DS_Store\nThumbs.db\n\n"
            "# Mapas gerados (podem conter snapshot do codigo, incluindo config.json)\n"
            "PROJETO_SAMURAI*.md"
        ),
        "descricao": ".gitignore: ignora PROJETO_SAMURAI*.md",
        "validar_python": False,
        "skip_if": "PROJETO_SAMURAI*.md",
    },
]

# =============================================================================
# HELPERS
# =============================================================================
def _run(cmd, timeout=120):
    try:
        r = subprocess.run(
            cmd, cwd=BASE, capture_output=True, text=True, 
            encoding="utf-8", errors="replace", timeout=timeout
        )
        out = r.stdout if r.stdout else ""
        err = r.stderr if r.stderr else ""
        return r.returncode, (out + err).strip()
    except subprocess.TimeoutExpired:
        return 1, "TIMEOUT"
    except FileNotFoundError:
        return 127, "COMANDO NAO ENCONTRADO"
    except Exception as e:
        return 1, f"ERRO INTERNO: {str(e)}"

def _aplicar_um(patch):
    caminho = BASE / patch["arquivo"]
    if not caminho.exists():
        return f"[SKIP] {patch['arquivo']} — arquivo nao existe"
    texto = caminho.read_text(encoding="utf-8")
    antigo, novo = patch["antigo"], patch["novo"]

    if patch.get("skip_if") and patch["skip_if"] in texto:
        return f"[SKIP] {patch['arquivo']} — ja aplicado (skip_if)"

    if antigo not in texto:
        return f"[SKIP] {patch['arquivo']} — alvo nao encontrado (ja aplicado?)"

    novo_texto = texto.replace(antigo, novo, 1)

    if patch.get("validar_python", True):
        try:
            ast.parse(novo_texto)
        except SyntaxError as e:
            raise SyntaxError(f"AST falhou em {patch['arquivo']} linha {e.lineno}: {e.msg}")

    caminho.write_text(novo_texto, encoding="utf-8")
    return f"[OK] {patch['arquivo']} — {patch['descricao']}"

def aplicar_patches():
    print("=" * 62)
    print("⚔️  APLICANDO PATCHES")
    print("=" * 62)
    ok = skip = 0
    for p in PATCHES:
        try:
            r = _aplicar_um(p)
        except Exception as e:
            print(f"[ERRO] {e}")
            sys.exit(1)
        print(r)
        ok   += r.startswith("[OK]")
        skip += r.startswith("[SKIP]")
    print(f"Resumo: {ok} aplicado(s), {skip} pulado(s).")

# =============================================================================
# SEGURANCA
# =============================================================================
def _verificar_stage():
    _, out = _run(["git", "diff", "--cached", "--name-only"])
    staged = [l for l in out.splitlines() if l.strip()]
    problemas = []
    for rel in staged:
        nome = Path(rel).name
        if nome in ARQUIVOS_PROIBIDOS:
            problemas.append(f"  - {rel} (arquivo sensivel)")
            continue
        if nome.startswith(PREFIXO_MD_GERADO) and nome.endswith(".md"):
            try:
                conteudo = (BASE / rel).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                conteudo = ""
            for pat in PADROES_SECRETOS:
                if pat.search(conteudo):
                    problemas.append(f"  - {rel} (contem segredo)")
                    break
    if problemas:
        raise RuntimeError(
            "🚨 PUSH BLOQUEADO — segredos no stage:\n"
            + "\n".join(problemas)
            + "\n\nRemova com 'git restore --staged <arquivo>' ou delete os .md."
        )

# =============================================================================
# SYNC COM SERVIDOR (ORDEM CORRIGIDA)
# =============================================================================
def sincronizar(mensagem="Patch automatico — atualiza codigo e servidor"):
    print("\n" + "=" * 62)
    print("☁️  SINCRONIZANDO COM O SERVIDOR")
    print("=" * 62)

    if not (BASE / ".git").exists():
        raise RuntimeError("Pasta nao e repositorio git.")

    # 1. Adiciona tudo
    _run(["git", "add", "-A"])
    
    # 2. Garante que mapas gerados NÃO estão no stage
    _run(["git", "rm", "--cached", "PROJETO_SAMURAI*.md"])

    # 3. Verifica segredos
    try:
        _verificar_stage()
    except RuntimeError:
        _run(["git", "reset"])
        raise
    print("[OK] Nenhum segredo no stage.")

    # 4. Commit local
    code, out = _run(["git", "commit", "-m", mensagem])
    if code != 0 and "nothing to commit" not in out and "nada a submeter" not in out:
        raise RuntimeError(f"git commit falhou:\n{out}")
    print(f"[OK] Commit: {mensagem}")

    # 5. Pull (agora não tem unstaged changes, então o rebase funciona)
    code, out = _run(["git", "pull", "origin", "main", "--rebase", "--no-edit"])
    if code != 0 and "couldn't find remote ref" not in out.lower():
        print(f"[AVISO] pull: {out[:150]}")
    else:
        print("[OK] Pull concluido.")

    # 6. Push
    code, out = _run(["git", "push", "origin", "main"])
    if code != 0:
        raise RuntimeError(f"git push falhou:\n{out}")
    print("[OK] Push para GitHub concluido.")
    print("[INFO] Streamlit Cloud e Render vao atualizar automaticamente.")

    hook = os.environ.get("RENDER_DEPLOY_HOOK", "").strip()
    if hook:
        try:
            urllib.request.urlopen(hook, timeout=10)
            print("[OK] Render deploy disparado via hook.")
        except Exception as e:
            print(f"[AVISO] Render hook falhou: {e}")
    print("=" * 62)

# =============================================================================
# RESTART LOCAL
# =============================================================================
def reiniciar_local():
    print("\n🔄 Reiniciando servidor local...")
    os.system(f'taskkill /F /FI "WINDOWTITLE eq {WINDOW_TITLE}" >nul 2>&1')
    if INICIAR_BAT.exists():
        os.startfile(str(INICIAR_BAT))
        print("[OK] Servidor local reiniciado.")
    else:
        print(f"[AVISO] {INICIAR_BAT} nao encontrado.")

# =============================================================================
# ENTRY
# =============================================================================
def main():
    args = sys.argv[1:]
    no_push   = "--no-push" in args
    only_push = "--only-push" in args

    if not only_push:
        aplicar_patches()

    if not no_push:
        try:
            sincronizar("Fix: RETURNING id, remove mapas com segredos e atualiza webhook")
        except Exception as e:
            print(f"\n[ERRO] Sync falhou:\n{e}")
            if only_push:
                sys.exit(1)
            print("\n[AVISO] Local OK, servidor NAO atualizado.")

    if not only_push:
        reiniciar_local()

    print("\n" + "=" * 62)
    print("✅ CONCLUIDO")
    print("=" * 62)

if __name__ == "__main__":
    main()