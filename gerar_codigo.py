"""
Gera um arquivo Markdown com o mapa completo do projeto.
Ignora __pycache__, data, .venv, .git, .idea, .vscode, node_modules e binários.
Uso:  py -3 gerar_codigo.py
Saída: PROJETO_SAMURAI.md na raiz.
"""
from __future__ import annotations

from pathlib import Path

BASE = Path(__file__).resolve().parent
IGNORE_DIRS = {
    "__pycache__", "data", ".venv", "venv", ".git",
    ".idea", ".vscode", "node_modules", ".pytest_cache",
}
IGNORE_EXT = {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg"}
OUTPUT = BASE / "PROJETO_SAMURAI.md"

LANG_MAP = {
    ".py": "python", ".bat": "bat", ".txt": "text",
    ".md": "markdown", ".json": "json", ".toml": "toml",
    ".css": "css", ".html": "html", ".js": "javascript",
}


def is_ignored(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return True
    if path.suffix.lower() in IGNORE_EXT:
        return True
    return False


def generate() -> None:
    linhas: list[str] = ["# ⚔️ Projeto Samurai — Mapa do Código\n"]
    linhas.append("> Gerado automaticamente por `gerar_codigo.py`\n")
    linhas.append(f"> Raiz: `{BASE.name}`\n\n---\n")

    arquivos = sorted(
        p for p in BASE.rglob("*")
        if p.is_file() and not is_ignored(p.relative_to(BASE))
    )

    for path in arquivos:
        rel = path.relative_to(BASE)
        lang = LANG_MAP.get(path.suffix.lower(), "text")
        linhas.append(f"\n## `{rel.as_posix()}`\n")
        try:
            conteudo = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            conteudo = "<<arquivo binário ou ilegível>>"
        linhas.append(f"```{lang}")
        linhas.append(conteudo)
        linhas.append("```\n")

    OUTPUT.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[OK] Mapa gerado: {OUTPUT}")
    print(f"[OK] {len(arquivos)} arquivo(s) incluído(s).")


if __name__ == "__main__":
    generate()
