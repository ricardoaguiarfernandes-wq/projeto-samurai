"""
criar_projeto_samurai.py — V8.0 (Flashcards Inteligentes e Revisão Espaçada)

ENTREGAS:
1. DB: Atualiza a tabela flashcards com as colunas do algoritmo SM-2 (intervalo, fator de facilidade, proxima revisao).
2. UI (14_Carreira.py): Adiciona o gerador automático de flashcards a partir dos manuais.
3. API (Telegram): Implementa o algoritmo SM-2 no comando /flashcard. A IA avalia a resposta do usuário e calcula a próxima data de revisão.
4. UI (03_Informacao.py): Adiciona o botão para ler as notícias resumidas no Streamlit.

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
# 1. DB SCHEMA (SM-2)
# ============================================================
def fix_schema_flashcards() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)
    
    old_table = '"""CREATE TABLE IF NOT EXISTS flashcards (id SERIAL PRIMARY KEY, question TEXT NOT NULL, answer TEXT NOT NULL, next_review TEXT NOT NULL);""",'
    new_table = '"""CREATE TABLE IF NOT EXISTS flashcards (id SERIAL PRIMARY KEY, question TEXT NOT NULL, answer TEXT NOT NULL, next_review TEXT NOT NULL, interval_days INTEGER DEFAULT 1, ease_factor REAL DEFAULT 2.5, last_asked INTEGER DEFAULT 0);""",'
    
    if old_table in txt:
        txt = txt.replace(old_table, new_table, 1)
        write_validated(p, txt)
    else:
        print("[SKIP] schema.py — tabela flashcards já atualizada ou não encontrada.")

# ============================================================
# 2. UI CARREIRA (Gerador de Flashcards)
# ============================================================
def fix_career_flashcards_ui() -> None:
    p = BASE / "ui" / "pages" / "14_Carreira.py"
    txt = read(p)

    if "Gerador de Flashcards" in txt:
        print("[SKIP] 14_Carreira.py — gerador já existe.")
        return

    # Adiciona a aba no topo
    old_tabs = 'tab_missoes, tab_manuais = st.tabs(["🎯 Missões Diárias", "📚 Base de Conhecimento (Manuais)"])'
    new_tabs = 'tab_missoes, tab_manuais, tab_flashcards = st.tabs(["🎯 Missões Diárias", "📚 Base de Conhecimento (Manuais)", "🧠 Flashcards (Revisão)"])'
    if old_tabs in txt:
        txt = txt.replace(old_tabs, new_tabs, 1)

    # Adiciona o bloco da aba flashcards no final
    flashcards_block = '''
with tab_flashcards:
    st.header("Gerador de Flashcards")
    st.write("A IA vai ler os seus manuais e criar perguntas e respostas para você memorizar.")
    
    manuais_lista = query_all("SELECT title FROM manuals")
    if not manuais_lista:
        st.warning("Envie um manual na aba ao lado primeiro.")
    else:
        manual_escolhido = st.selectbox("Selecione o manual:", [m['title'] for m in manuais_lista])
        
        if st.button("🪄 Gerar Flashcards com IA", use_container_width=True):
            with st.spinner("Lendo o manual e gerando cartões..."):
                import random
                manual_data = query_one("SELECT content FROM manuals WHERE title = ?", (manual_escolhido,))
                texto_manual = manual_data['content']
                
                # Pega um chunk de 8000 caracteres para não estourar o limite
                if len(texto_manual) > 8000:
                    start_idx = random.randint(0, len(texto_manual) - 8000)
                    chunk = texto_manual[start_idx:start_idx+8000]
                else:
                    chunk = texto_manual
                    
                prompt = f"""Leia o trecho do manual técnico abaixo e crie EXATAMENTE 3 flashcards no formato JSON.
Cada flashcard deve ter uma pergunta desafiadora e uma resposta direta.

Retorne APENAS o JSON válido, sem markdown:
{{
  "flashcards": [
    {{"question": "Pergunta 1...", "answer": "Resposta 1..."}},
    {{"question": "Pergunta 2...", "answer": "Resposta 2..."}},
    {{"question": "Pergunta 3...", "answer": "Resposta 3..."}}
  ]
}}

TEXTO DO MANUAL:
{chunk}
"""
                res = ask_gemini(prompt)
                import re, json
                from datetime import date
                m = re.search(r'\\{.*\\}', res, re.DOTALL)
                if m:
                    try:
                        data = json.loads(m.group(0))
                        for card in data.get("flashcards", []):
                            execute(
                                "INSERT INTO flashcards (question, answer, next_review) VALUES (?, ?, ?)",
                                (card["question"], card["answer"], date.today().isoformat())
                            )
                        st.success("Flashcards gerados com sucesso! Vá no Telegram e digite /flashcard.")
                    except Exception as e:
                        st.error(f"Erro ao processar JSON: {e}")
                else:
                    st.error("A IA não retornou o formato esperado.")

    st.divider()
    st.subheader("📅 Cartões Pendentes Hoje")
    from datetime import date
    pendentes = query_all("SELECT question FROM flashcards WHERE next_review <= ? AND last_asked = 0", (date.today().isoformat(),))
    if not pendentes:
        st.info("Nenhum cartão pendente para hoje. Ótimo trabalho!")
    else:
        for p_card in pendentes:
            st.markdown(f"- {p_card['question']}")
'''

    txt += flashcards_block
    write_validated(p, txt)

# ============================================================
# 3. API (Algoritmo SM-2 no Telegram)
# ============================================================
def fix_api_telegram_sm2() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "SM-2" in txt:
        print("[SKIP] api_samurai.py — SM-2 já implementado.")
        return

    # Substitui toda a lógica de texto do telegram para incluir o SM-2 e a resposta
    old_flashcard = '''        if text.startswith("/flashcard"):
            card = query_one("SELECT question, answer FROM flashcards ORDER BY RANDOM() LIMIT 1")
            if not card:
                reply("📭 Nenhum flashcard cadastrado ainda. Vá na aba Carreira do app.")
            else:
                reply(f"🧠 **Flashcard:**\\n\\n{card['question']}\\n\\n_(Digite qualquer coisa para ver a resposta)_\\n**Resp:** {card['answer']}")
            return'''

    new_flashcard = '''        # --- LÓGICA DE FLASHCARDS (SM-2) ---
        from datetime import datetime, timedelta
        
        # Se o usuário estiver respondendo a um flashcard pendente
        card_pendente = query_one("SELECT * FROM flashcards WHERE last_asked = 1 LIMIT 1")
        if card_pendente and not text.startswith("/"):
            prompt_aval = f"""Atue como um avaliador técnico.
Pergunta: "{card_pendente['question']}"
Resposta Correta: "{card_pendente['answer']}"
Resposta do Aluno: "{text}"

O aluno acertou? Avalie o sentido, não precisa ser palavra por palavra. 
Se ele acertou, responda começando com "ACERTOU".
Se ele errou, responda começando com "ERROU" e explique a resposta correta.
"""
            avaliacao = ask_gemini(prompt_aval)
            
            # Algoritmo SM-2 Simplificado
            ease = card_pendente['ease_factor']
            interval = card_pendente['interval_days']
            
            if "ACERTOU" in avaliacao:
                interval = int(interval * ease)
                ease = ease + 0.1
                reply(f"✅ {avaliacao}\\n\\n_Próxima revisão em {interval} dias._")
            else:
                interval = 1 # Volta amanhã
                ease = max(1.3, ease - 0.2)
                reply(f"❌ {avaliacao}\\n\\n_Voltará amanhã._")
                
            next_review = (date.today() + timedelta(days=interval)).isoformat()
            execute("UPDATE flashcards SET last_asked = 0, interval_days = ?, ease_factor = ?, next_review = ? WHERE id = ?",
                    (interval, ease, next_review, card_pendente['id']))
            return

        if text.startswith("/flashcard"):
            card = query_one("SELECT * FROM flashcards WHERE next_review <= ? AND last_asked = 0 ORDER BY next_review ASC LIMIT 1", (date.today().isoformat(),))
            if not card:
                reply("📭 Nenhum flashcard pendente para hoje. Vá na aba Carreira do app para gerar novos.")
            else:
                execute("UPDATE flashcards SET last_asked = 1 WHERE id = ?", (card['id'],))
                reply(f"🧠 **Flashcard:**\\n\\n{card['question']}\\n\\n_(Digite a sua resposta)_")
            return'''

    if old_flashcard in txt:
        txt = txt.replace(old_flashcard, new_flashcard, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] api_samurai.py — bloco do flashcard antigo não encontrado.")

# ============================================================
# 4. UI INFORMAÇÃO (Notícias no App)
# ============================================================
def fix_informacao_news_ui() -> None:
    p = BASE / "ui" / "pages" / "03_Informacao.py"
    txt = read(p)

    if "Notícias Legislativas" in txt:
        print("[SKIP] 03_Informacao.py — notícias já implementadas.")
        return

    old_block = 'with tab_financas:'
    new_block = '''with tab_financas:
    st.subheader("🏛️ Notícias Legislativas de Hoje")
    if st.button("🧠 Gerar Resumo de Notícias", use_container_width=True):
        with st.spinner("Lendo Câmara, Senado, ALERJ e Macaé..."):
            # Simulando a chamada da API local (no Render) - vamos chamar direto a função
            try:
                # No app local não tem como chamar a API protegida, então vamos ler direto
                import feedparser
                from bs4 import BeautifulSoup
                noticias = []
                
                f1 = feedparser.parse("https://www.camara.leg.br/noticias/rss/ultimas-noticias")
                for e in f1.entries[:2]: noticias.append(f"[Câmara] {e.title}")
                f2 = feedparser.parse("https://www12.senado.leg.br/noticias/RSS")
                for e in f2.entries[:2]: noticias.append(f"[Senado] {e.title}")
                f3 = feedparser.parse("https://news.google.com/rss/search?q=alerj+noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419")
                for e in f3.entries[:2]: noticias.append(f"[ALERJ] {e.title}")
                f4 = feedparser.parse("https://news.google.com/rss/search?q=camara+macae+noticias&hl=pt-BR&gl=BR&ceid=BR:pt-419")
                for e in f4.entries[:2]: noticias.append(f"[Macaé] {e.title}")
                
                prompt = f"Resuma as notícias a seguir em tópicos e explique o impacto prático:\\n" + "\\n".join(noticias)
                resumo = ask_gemini(prompt)
                st.markdown(f'<div class="samurai-card" style="border-left-color: #8B0000;"><div style="white-space: pre-wrap;">{resumo}</div></div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro ao carregar notícias: {e}")
    st.divider()'''

    if old_block in txt:
        txt = txt.replace(old_block, new_block, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 03_Informacao.py — bloco tab_financas não encontrado.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: flashcards inteligentes (SM-2), gerador de cartoes e noticias no app"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
        
        # Força Deploy
        try:
            hook_url = ""
            env_file = BASE / ".env.render"
            if env_file.exists():
                for line in read(env_file).splitlines():
                    if line.startswith("RENDER_DEPLOY_HOOK_URL="):
                        hook_url = line.split("=", 1)[1].strip()
                        break
            if hook_url:
                import requests
                requests.get(hook_url, timeout=10)
                print("[OK] Deploy no Render disparado!")
        except Exception:
            pass
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V8.0 — FLASHCARDS SM-2 E NOTÍCIAS NO APP")
    print("=" * 60)

    fix_schema_flashcards()
    fix_career_flashcards_ui()
    fix_api_telegram_sm2()
    fix_informacao_news_ui()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nComo testar:")
    print("1. Espere o Render atualizar.")
    print("2. Vá na aba 'Carreira' > 'Flashcards' e gere cartões a partir do seu manual.")
    print("3. No Telegram, envie '/flashcard' para receber a pergunta.")
    print("4. Digite a sua resposta. A IA vai te avaliar e agendar a próxima revisão (se acertar, demora mais; se errar, volta amanhã).")
    print("5. Na aba 'Informação', agora tem um botão para gerar o resumo de notícias direto no app.")

if __name__ == "__main__":
    aplicar()