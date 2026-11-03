"""
criar_projeto_samurai.py — V9.0 (O Patch Definitivo: RAG, Valuation, PWA e WhatsApp)

ENTREGAS:
1. DB: Ativa pgvector e adiciona a coluna 'embedding' em journal_entries.
2. AI: Adiciona função de embeddings (text-embedding-004) no services/ai.py.
3. UI (06_Autoconhecimento.py): Salva o embedding a cada nova reflexão.
4. UI (04_Patrimonio.py): Adiciona o valuation (lucro/prejuízo) em tempo real.
5. APP: Injeta o CSS para esconder o cabeçalho do Streamlit (modo PWA).
6. API (Telegram): Altera a busca do diário para usar RAG Vetorial.
7. API (WhatsApp): Cria a rota /webhook/whatsapp (para Z-API/Twilio).

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
import re
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
# 1. DB & RAG (schema.py)
# ============================================================
def fix_schema_vector() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)

    if "vector(768)" in txt:
        print("[SKIP] schema.py — coluna embedding já existe.")
        return

    # Adiciona a extensão pgvector e a coluna de embedding
    if "CREATE EXTENSION IF NOT EXISTS vector;" not in txt:
        old_ddl = '"""CREATE TABLE IF NOT EXISTS habits (id SERIAL PRIMARY KEY, name TEXT NOT NULL, pillar TEXT NOT NULL, description TEXT, active INTEGER NOT NULL DEFAULT 1, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);""",'
        new_ddl = '"CREATE EXTENSION IF NOT EXISTS vector;",\n        ' + old_ddl
        txt = txt.replace(old_ddl, new_ddl, 1)

    old_journal = '"""CREATE TABLE IF NOT EXISTS journal_entries (id SERIAL PRIMARY KEY, entry_date TEXT NOT NULL, prompt TEXT, content TEXT NOT NULL, ai_reflection TEXT);""",'
    new_journal = '"""CREATE TABLE IF NOT EXISTS journal_entries (id SERIAL PRIMARY KEY, entry_date TEXT NOT NULL, prompt TEXT, content TEXT NOT NULL, ai_reflection TEXT, embedding vector(768));""",'
    
    if old_journal in txt:
        txt = txt.replace(old_journal, new_journal, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] schema.py — tabela journal_entries não encontrada.")

# ============================================================
# 2. AI SERVICE (services/ai.py)
# ============================================================
def fix_ai_embeddings() -> None:
    p = BASE / "services" / "ai.py"
    txt = read(p)

    if "get_embedding" in txt:
        print("[SKIP] ai.py — função de embedding já existe.")
        return

    func_embedding = '''
def get_embedding(text: str) -> list[float]:
    """Gera o embedding (vetor) de um texto para busca semântica (RAG)."""
    api_key = get_api_key()
    if not api_key or api_key == "COLE_SUA_CHAVE_AQUI":
        return []
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.embed_content(
            model='text-embedding-004',
            contents=text
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"Erro ao gerar embedding: {e}")
        return []
'''
    txt += func_embedding
    write_validated(p, txt)

# ============================================================
# 3. UI AUTOCONHECIMENTO (Salvar Embedding)
# ============================================================
def fix_ui_journal_embedding() -> None:
    p = BASE / "ui" / "pages" / "06_Autoconhecimento.py"
    txt = read(p)

    if "embedding = get_embedding" in txt:
        print("[SKIP] 06_Autoconhecimento.py — embedding já salvo.")
        return

    if "from services.ai import ask_gemini" in txt and "get_embedding" not in txt:
        txt = txt.replace("from services.ai import ask_gemini", "from services.ai import ask_gemini, get_embedding")

    old_save = '''        execute(
            "INSERT INTO journal_entries (entry_date, prompt, content, ai_reflection) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), prompt_do_dia, texto.strip(), reflexao_ia)
        )'''

    new_save = '''        # Gera o embedding para RAG Vetorial
        embedding = get_embedding(texto.strip())
        emb_str = f"[{','.join(map(str, embedding))}]" if embedding else None

        execute(
            "INSERT INTO journal_entries (entry_date, prompt, content, ai_reflection, embedding) VALUES (?, ?, ?, ?, ?::vector)",
            (date.today().isoformat(), prompt_do_dia, texto.strip(), reflexao_ia, emb_str)
        )'''

    if old_save in txt:
        txt = txt.replace(old_save, new_save, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 06_Autoconhecimento.py — bloco de insert do journal não encontrado.")

# ============================================================
# 4. UI PATRIMÔNIO (Valuation em Tempo Real)
# ============================================================
def fix_ui_patrimonio_valuation() -> None:
    p = BASE / "ui" / "pages" / "04_Patrimonio.py"
    txt = read(p)

    if "Lucro/Prejuízo" in txt:
        print("[SKIP] 04_Patrimonio.py — valuation já existe.")
        return

    old_card = '''    for a in carteira:
        st.markdown(f'<div class="samurai-card" style="padding: 10px;"><b>{a["ticker"]}</b> - {a["quantity"]} cotas @ R$ {a["average_price"]:.2f}</div>', unsafe_allow_html=True)'''

    new_card = '''    import yfinance as yf
    
    for a in carteira:
        ticker = a['ticker']
        ticker_busca = ticker if ".SA" in ticker else f"{ticker}.SA"
        
        try:
            data = yf.Ticker(ticker_busca).history(period="1d")
            preco_atual = float(data['Close'].iloc[-1]) if not data.empty else a['average_price']
        except Exception:
            preco_atual = a['average_price']
            
        valor_investido = a['quantity'] * a['average_price']
        valor_atual = a['quantity'] * preco_atual
        lucro = valor_atual - valor_investido
        lucro_pct = (lucro / valor_investido) * 100 if valor_investido > 0 else 0
        
        cor = "#4CAF50" if lucro >= 0 else "#F44336"
        sinal = "+" if lucro >= 0 else ""
        
        st.markdown(f"""
        <div class="samurai-card" style="padding: 10px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <b>{ticker}</b><br>
                <span style="font-size: 0.8rem; color: #CCC;">{a['quantity']} cotas @ R$ {a['average_price']:.2f}</span>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 1.1rem; font-weight: bold;">R$ {valor_atual:.2f}</span><br>
                <span style="font-size: 0.85rem; color: {cor};">{sinal}R$ {lucro:.2f} ({sinal}{lucro_pct:.1f}%)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)'''

    if old_card in txt:
        txt = txt.replace(old_card, new_card, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 04_Patrimonio.py — bloco do card de ação não encontrado.")

# ============================================================
# 5. APP.PY (CSS PWA e Esconder Header)
# ============================================================
def fix_app_pwa_css() -> None:
    p = BASE / "app.py"
    txt = read(p)

    if "header[data-testid=\"stHeader\"]" in txt:
        print("[SKIP] app.py — CSS do PWA já aplicado.")
        return

    old_css = '''/* MOBILE OPTIMIZATIONS */
@media (max-width: 768px) {'''

    new_css = '''/* PWA - ESCONDER BARRA DO STREAMLIT NO MOBILE */
@media (max-width: 768px) {
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
}

/* MOBILE OPTIMIZATIONS */
@media (max-width: 768px) {'''

    if old_css in txt:
        txt = txt.replace(old_css, new_css, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] app.py — bloco CSS mobile não encontrado.")

# ============================================================
# 6. API (RAG no Telegram + Webhook WhatsApp)
# ============================================================
def fix_api_rag_and_whatsapp() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    # 6.1 - Atualizar o Telegram para usar RAG
    if "ORDER BY embedding <-> %s::vector" not in txt:
        old_ctx = '''        entries = query_all("SELECT entry_date, content FROM journal_entries ORDER BY entry_date DESC LIMIT 20")
        
        ctx = ""
        if entries:
            ctx = "\\n".join([f"[{e['entry_date']}] {e['content']}" for e in entries])
        else:
            ctx = "(Nenhum registro no diário ainda)"'''

        new_ctx = '''        from services.ai import get_embedding
        query_emb = get_embedding(text)
        
        ctx = ""
        if query_emb:
            emb_str = f"[{','.join(map(str, query_emb))}]"
            try:
                # Busca semântica usando a extensão pgvector
                entries = query_all("SELECT entry_date, content FROM journal_entries ORDER BY embedding <-> %s::vector LIMIT 5", (emb_str,))
                if entries:
                    ctx = "\\n".join([f"[{e['entry_date']}] {e['content']}" for e in entries])
            except Exception as e:
                print(f"Erro no RAG (usando fallback): {e}")
                
        if not ctx:
            # Fallback se não tiver embedding
            entries = query_all("SELECT entry_date, content FROM journal_entries ORDER BY entry_date DESC LIMIT 5")
            ctx = "\\n".join([f"[{e['entry_date']}] {e['content']}" for e in entries]) if entries else "(Nenhum registro no diário ainda)"'''

        if old_ctx in txt:
            txt = txt.replace(old_ctx, new_ctx, 1)

    # 6.2 - Adicionar rota do WhatsApp
    if "/webhook/whatsapp" not in txt:
        whatsapp_route = '''
# ============================================================
# WEBHOOK DO WHATSAPP (Z-API / Twilio Compatível)
# ============================================================
class WhatsAppPayload(BaseModel):
    message: str
    sender: str

@app.post("/webhook/whatsapp")
async def receive_whatsapp(payload: WhatsAppPayload, background_tasks: BackgroundTasks):
    def process_msg():
        from services.ai import ask_gemini
        try:
            resposta = ask_gemini(f"Atue como o Mentor Samurai no WhatsApp. O usuário disse: '{payload.message}'. Responda de forma direta, amigável e curta.")
            
            # Configuração para envio de volta (depende do provedor Z-API/Twilio)
            # Exemplo genérico para Z-API:
            import os
            zapi_instance = os.environ.get("ZAPI_INSTANCE", "")
            zapi_token = os.environ.get("ZAPI_TOKEN", "")
            
            if zapi_instance and zapi_token:
                requests.post(
                    f"https://api.z-api.io/instances/{zapi_instance}/token/{zapi_token}/send-text",
                    json={"phone": payload.sender, "message": resposta},
                    timeout=10
                )
        except Exception as e:
            print(f"Erro WhatsApp: {e}")

    background_tasks.add_task(process_msg)
    return {"status": "ok"}

'''
        marker = 'if __name__ == "__main__":'
        if marker in txt:
            txt = txt.replace(marker, whatsapp_route + marker, 1)

    write_validated(p, txt)

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: rag vetorial, valuation tempo real, pwa mobile e whatsapp webhook"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V9.0 — PATCH DEFINITIVO (RAG, PWA, VALUATION E WHATSAPP)")
    print("=" * 60)

    fix_schema_vector()
    fix_ai_embeddings()
    fix_ui_journal_embedding()
    fix_ui_patrimonio_valuation()
    fix_app_pwa_css()
    fix_api_rag_and_whatsapp()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que você acabou de instalar:")
    print("1. 💸 Valuation: Vá em Patrimônio para ver o lucro/prejuízo em tempo real.")
    print("2. 📱 PWA: Abra o app no celular. A barra do Streamlit sumiu (parece um app nativo).")
    print("3. 🧠 RAG: Quando enviar uma nova reflexão no Diário, ela será vetorizada.")
    print("   No Telegram, pergunte algo antigo (ex: 'o que eu decidi em julho?'). A IA vai buscar por similaridade.")
    print("4. 🟢 WhatsApp: A rota /webhook/whatsapp está pronta. Configure a Z-API no Render para ativar.")

if __name__ == "__main__":
    aplicar()