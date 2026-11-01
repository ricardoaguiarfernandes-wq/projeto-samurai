"""
melhoria.py — Corrige o erro de instalação do Streamlit Cloud.
Remove as dependências pesadas (faster-whisper, yt-dlp) que causaram conflito.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path

# =============================================================================
# CONFIG
# =============================================================================
BASE = Path(__file__).resolve().parent
PADROES_SECRETOS = [
    re.compile(r"AQ\.Ab8RN6[A-Za-z0-9_\-]{20,}"),
    re.compile(r"postgresql://[^:\s]+:[^@\s]+@"),
]
ARQUIVOS_PROIBIDOS = {"config.json", ".env", "secrets.toml"}

# =============================================================================
# CONTEÚDO LIMPO DO REQUIREMENTS.TXT
# =============================================================================
# Mantemos apenas o essencial para o Samurai funcionar na nuvem.
# Removemos yt-dlp e faster-whisper.
NOVO_REQUIREMENTS = '''streamlit>=1.38.0
pandas>=2.2.0
yfinance>=0.2.40
requests>=2.31.0
feedparser>=6.0.10
pymupdf>=1.24.0
google-genai>=1.0.0
google-generativeai>=0.8.0
psycopg2-binary>=2.9.9
psutil>=5.9.0
readtime>=3.0.0
trafilatura>=1.6.0
fastapi>=0.110.0
uvicorn>=0.29.0
pydantic>=2.0.0
gTTS>=2.5.0
fpdf2>=2.7.8
plotly>=5.18.0
beautifulsoup4>=4.12.0
youtube-transcript-api>=0.6.2
'''

# =============================================================================
# HELPERS DE SINCRONIZAÇÃO
# =============================================================================
def _run(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, cwd=BASE, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return 1, str(e)

def _verificar_stage():
    _, out = _run(["git", "diff", "--cached", "--name-only"])
    for rel in [l for l in out.splitlines() if l.strip()]:
        if Path(rel).name in ARQUIVOS_PROIBIDOS:
            raise RuntimeError(f"🚨 Segredo detectado: {rel}")

# =============================================================================
# EXECUÇÃO
# =============================================================================
def aplicar_melhoria():
    print("=" * 60)
    print("⚔️  CORRIGINDO ERRO DE INSTALAÇÃO (STREAMLIT CLOUD)")
    print("=" * 60)

    # 1. Limpar requirements.txt
    arq_req = BASE / "requirements.txt"
    try:
        # Escreve o conteúdo limpo
        arq_req.write_text(NOVO_REQUIREMENTS, encoding="utf-8")
        print("[OK] requirements.txt limpo. Dependências pesadas removidas.")
    except Exception as e:
        print(f"[ERRO] Falha ao escrever requirements.txt: {e}")
        sys.exit(1)

    # 2. Sincronização com GitHub
    print("\n☁️  SINCRONIZANDO COM O SERVIDOR (GitHub)")
    _run(["git", "add", "-A"])
    _run(["git", "rm", "--cached", "PROJETO_SAMURAI*.md"])
    
    try:
        _verificar_stage()
    except RuntimeError as e:
        _run(["git", "reset"])
        print(e)
        sys.exit(1)

    code, out = _run(["git", "commit", "-m", "Fix: Limpa requirements.txt para restaurar deploy no Streamlit Cloud"])
    if code != 0 and "nothing to commit" not in out:
        print(f"[ERRO] Commit falhou: {out}")
        sys.exit(1)
    
    print("[OK] Commit realizado.")
    _run(["git", "pull", "origin", "main", "--rebase", "--no-edit"])
    
    code, out = _run(["git", "push", "origin", "main"])
    if code != 0:
        print(f"[ERRO] Push falhou: {out}")
        sys.exit(1)
    
    print("[OK] Push concluído. O Streamlit Cloud vai reinstalar as dependências e voltar ao ar.")
    print("=" * 60)

if __name__ == "__main__":
    aplicar_melhoria()