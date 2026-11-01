"""
Gera um arquivo Markdown com o mapa completo do projeto.
Ignora arquivos sensíveis E censura chaves de API (Regex) para nunca bloquear o GitHub.
"""
from __future__ import annotations

import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
IGNORE_DIRS = {
    "__pycache__", "data", ".venv", "venv", ".git",
    ".idea", ".vscode", "node_modules", ".pytest_cache",
}
IGNORE_EXT = {".db", ".sqlite", ".sqlite3", ".pyc", ".pyo", ".log", ".png", ".jpg", ".jpeg"}

# Arquivos que NUNCA devem ser lidos
SENSITIVE_FILES = {"config.json", "secrets.toml", ".env", ".env.local", ".env.production"}
SENSITIVE_PATHS = {".streamlit/secrets.toml", ".streamlit/config.toml"}

# === PATCH SAMURAI: CENSURA DE SEGREDOS ===
# Se o gerador encontrar esses padrões em QUALQUER arquivo, ele substitui pelo texto abaixo
PADROES_SECRETOS = [
    (re.compile(r"AQ\.Ab8RN6[A-Za-z0-9_\-]{20,}"), "*** CHAVE GEMINI REMOVIDA POR SEGURANCA ***"),
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "*** CHAVE OPENAI REMOVIDA POR SEGURANCA ***"),
    (re.compile(r"postgresql://[^:\s]+:[^@\s]+@"), "*** URL SUPABASE REMOVIDA POR SEGURANCA ***"),
]
# ==========================================

OUTPUT = BASE / "PROJETO_SAMURAI.md"
# === PATCH SAMURAI: SEGREDOS ===
ARQUIVOS_PROIBIDOS = {"config.json", "secrets.toml", ".env"}
# ================================

LANG_MAP = {
    ".py": "python", ".bat": "bat", ".txt": "text",
    ".md": "markdown", ".json": "json", ".toml": "toml",
    ".css": "css", ".html": "html", ".js": "javascript",
}

def is_ignored(rel_path: Path) -> bool:
    # Ignora diretórios
    if any(part in IGNORE_DIRS for part in rel_path.parts):
        return True
    # Ignora extensões
    if rel_path.suffix.lower() in IGNORE_EXT:
        return True
    # Ignora arquivos sensíveis
    if rel_path.name in SENSITIVE_FILES:
        return True
    
    # Ignora caminhos específicos E os próprios mapas gerados (para não ler o mapa antigo)
    caminho_str = rel_path.as_posix()
    if caminho_str in SENSITIVE_PATHS or caminho_str.endswith("secrets.toml"):
        return True
    if rel_path.name.startswith("PROJETO_SAMURAI") and rel_path.name.endswith(".md"):
        return True
        
    return False

def sanitizar_texto(texto: str) -> str:
    """Substitui chaves de API conhecidas por texto seguro."""
    for padrao, substituicao in PADROES_SECRETOS:
        texto = padrao.sub(substituicao, texto)
    return texto

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
        
        if rel.name == OUTPUT.name:
            continue
            
        lang = LANG_MAP.get(path.suffix.lower(), "text")
        linhas.append(f"\n## `{rel.as_posix()}`\n")
        try:
            conteudo = path.read_text(encoding="utf-8")
            # Aplica a censura antes de adicionar ao Markdown
            conteudo = sanitizar_texto(conteudo)
        except (UnicodeDecodeError, OSError):
            conteudo = "<<arquivo binário ou ilegível>>"
            
        linhas.append(f"```{lang}")
        linhas.append(conteudo)
        linhas.append("```\n")

    OUTPUT.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[OK] Mapa gerado: {OUTPUT}")
    print(f"[OK] {len(arquivos)} arquivo(s) incluído(s) (segredos censurados).")

if __name__ == "__main__":
    generate()  