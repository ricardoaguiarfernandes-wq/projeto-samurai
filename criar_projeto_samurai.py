import ast
import os
import sys
import subprocess
from pathlib import Path

BASE = Path(r"C:\Users\Ricardo Fernandes\Desktop\Projeto Samurai")

def aplicar_patch():
    print("=" * 60)
    print("⚔️  PREPARANDO O PROJETO PARA O GITHUB E STREAMLIT CLOUD")
    print("=" * 60)

    if not BASE.exists():
        sys.exit(1)

    # 1. Criar o .gitignore (Para não subir chaves e banco de dados local)
    gitignore_file = BASE / ".gitignore"
    gitignore_content = """# Ambiente Virtual
.venv/
venv/
env/

# Python
__pycache__/
*.pyc
*.pyo

# Dados e Banco (Banco local não deve subir)
data/
*.db
*.sqlite

# Configurações Locais (NUNCA suba sua chave de API)
config.json

# Streamlit
.streamlit/secrets.toml

# Sistema
.DS_Store
Thumbs.db
"""
    gitignore_file.write_text(gitignore_content, encoding="utf-8")
    print("[OK] Criado: .gitignore (proteção de segurança ativada)")

    # 2. Atualizar services/ai.py para ler do st.secrets (Nuvem) ou config.json (Local)
    ai_file = BASE / "services" / "ai.py"
    ai_txt = ai_file.read_text(encoding="utf-8")
    
    if "import streamlit as st" not in ai_txt:
        ai_txt = ai_txt.replace("import json", "import json\nimport streamlit as st")
        ai_txt = ai_txt.replace(
            "def get_api_key() -> str:\n    if CONFIG_PATH.exists():",
            """def get_api_key() -> str:
    # Tenta pegar dos Secrets do Streamlit Cloud (Nuvem)
    try:
        if "gemini_api_key" in st.secrets:
            return st.secrets["gemini_api_key"]
    except Exception:
        pass
        
    # Fallback local (config.json)
    if CONFIG_PATH.exists():"""
        )
        ai_file.write_text(ai_txt, encoding="utf-8")
        print("[OK] services/ai.py atualizado (Compatível com Streamlit Cloud)")

    # 3. Criar o README.md
    readme_file = BASE / "README.md"
    readme_content = """# ⚔️ Projeto Samurai

Um Sistema Operacional Pessoal (Personal OS) focado em desenvolvimento humano, disciplina e consistência.

## 🚀 Tecnologias
- **Streamlit**: Interface Web Mobile-First
- **SQLite**: Banco de dados local
- **Google Gemini**: Inteligência Artificial (Mentor Samurai)
- **FastAPI**: Webhook para receber newsletters (via Power Automate)
- **Cloudflare Tunnel**: Exposição segura do Webhook

## 🏛️ Pilares
1. Corpo (Calistenia e Mobilidade)
2. Mente (Leitura de PDFs e Resumos IA)
3. Informação (Finanças, Notícias e Legislativo)
4. Patrimônio (Carteira de Investimentos e DailyFin)
5. Descanso & Lazer (Guia de viagens e Macaé)
6. Autoconhecimento (Diário e Meditação)
7. Consistência (Hábitos e Anti-Burnout)
8. Religião & Bíblia (Plano de Leitura em 1 ano)
9. Newsletter (Curadoria diária estilo The Hustle)

## ⚙️ Como rodar localmente
1. Clone o repositório.
2. Instale as dependências: `pip install -r requirements.txt`
3. Crie o arquivo `config.json` com sua chave: `{"gemini_api_key": "SUA_CHAVE"}`
4. Rode o `INICIAR.bat`.
"""
    readme_file.write_text(readme_content, encoding="utf-8")
    print("[OK] Criado: README.md")

    # 4. Inicializar o Git e fazer o commit
    print("\nInicializando o Git...")
    try:
        # Verifica se já é um repositório git
        if not (BASE / ".git").exists():
            subprocess.run(["git", "init"], cwd=BASE, check=True, stdout=subprocess.DEVNULL)
            print("[OK] Repositório Git inicializado.")
        else:
            print("[SKIP] Repositório Git já existe.")

        # Adiciona todos os arquivos e commita
        subprocess.run(["git", "add", "."], cwd=BASE, check=True)
        subprocess.run(["git", "commit", "-m", "Projeto Samurai: Versão Mobile e IA"], cwd=BASE, check=True, stdout=subprocess.DEVNULL)
        print("[OK] Arquivos adicionados e commit realizado.")
    except subprocess.CalledProcessError as e:
        print(f"[AVISO] O Git já pode ter os arquivos ou houve um erro: {e}")
    except FileNotFoundError:
        print("[ERRO] Git não encontrado. Instale o Git (git-scm.com) e tente novamente.")
        sys.exit(1)

    print("\n" + "="*60)
    print("✅ PREPARAÇÃO CONCLUÍDA!")
    print("="*60)
    print("Siga os passos abaixo para colocar no ar:")
    print("1. Acesse github.com/new e crie um repositório chamado 'projeto-samurai'.")
    print("   NÃO marque para adicionar README ou .gitignore (já criamos).")
    print("2. Copie o link do repositório que o GitHub gerar.")
    print("3. No CMD, rode os comandos:")
    print("   git branch -M main")
    print("   git remote add origin SEU_LINK_AQUI")
    print("   git push -u origin main")
    print("="*60)

if __name__ == "__main__":
    aplicar_patch()