"""
criar_projeto_samurai.py — V8.2 (Controle de Orçamento e Alertas)

ENTREGAS:
1. DB: Cria a tabela 'budgets' para guardar os limites mensais.
2. UI (15_Financas.py): Adiciona a configuração de teto de gastos e barras de progresso.
3. API (api_samurai.py): A rota de receber foto no Telegram agora checa o orçamento e avisa se estourou.

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
# 1. SCHEMA (Tabela de Orçamento)
# ============================================================
def fix_schema_budgets() -> None:
    p = BASE / "core" / "schema.py"
    txt = read(p)
    
    if "CREATE TABLE IF NOT EXISTS budgets" in txt:
        print("[SKIP] schema.py — tabela budgets já existe.")
        return
    
    marker = '"""CREATE TABLE IF NOT EXISTS expenses (id SERIAL PRIMARY KEY, expense_date TEXT NOT NULL, description TEXT NOT NULL, amount REAL NOT NULL, category TEXT, notes TEXT);""",'
    nova_linha = marker + '\n        """CREATE TABLE IF NOT EXISTS budgets (category TEXT PRIMARY KEY, limit_amount REAL NOT NULL);""",'
    
    if marker in txt:
        txt = txt.replace(marker, nova_linha, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] schema.py — marcador de expenses não encontrado.")

# ============================================================
# 2. UI FINANÇAS (Configuração de Orçamento e Progresso)
# ============================================================
def fix_financas_budget_ui() -> None:
    p = BASE / "ui" / "pages" / "15_Financas.py"
    txt = read(p)

    if "Configurar Orçamento" in txt:
        print("[SKIP] 15_Financas.py — orçamento já implementado.")
        return

    old_chart = '''# --- GRÁFICO DE GASTOS ---
st.subheader("🍕 Para onde o dinheiro está indo?")'''

    new_ui = '''# --- CONFIGURAÇÃO DE ORÇAMENTO ---
with st.expander("⚙️ Configurar Orçamento Mensal (Teto de Gastos)"):
    st.write("Defina o limite para cada categoria. O Mentor vai te avisar se você estourar.")
    with st.form("form_budget"):
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Categoria", ["Alimentação", "Transporte", "Lazer", "Saúde", "Outros"])
        val = c2.number_input("Limite Mensal (R$)", min_value=0.0, step=100.0)
        if st.form_submit_button("Salvar Limite"):
            execute("INSERT INTO budgets (category, limit_amount) VALUES (?, ?) ON CONFLICT(category) DO UPDATE SET limit_amount=excluded.limit_amount", (cat, val))
            st.success(f"Limite de R$ {val:.2f} salvo para {cat}.")
            st.rerun()

st.divider()

# --- BARRAS DE PROGRESSO DO ORÇAMENTO ---
st.subheader("📊 Orçamento em Tempo Real")
budgets = query_all("SELECT * FROM budgets")
if budgets:
    for b in budgets:
        # Pega o total gasto nesta categoria no mês atual
        gasto_cat = sum([g['amount'] for g in gastos_mes if g['category'] == b['category']])
        perc = (gasto_cat / b['limit_amount']) * 100 if b['limit_amount'] > 0 else 0
        
        cor = "#4CAF50" if perc < 70 else ("#F9A825" if perc < 90 else "#F44336")
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; font-size: 0.9rem;">
            <span><b>{b['category']}</b></span>
            <span>R$ {gasto_cat:.2f} / R$ {b['limit_amount']:.2f} ({perc:.0f}%)</span>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(perc / 100, 1.0))
        if perc >= 90:
            st.caption(f"⚠️ Cuidado! Você já usou {perc:.0f}% do seu limite em {b['category']}.")

st.divider()

# --- GRÁFICO DE GASTOS ---
st.subheader("🍕 Para onde o dinheiro está indo?")'''

    if old_chart in txt:
        txt = txt.replace(old_chart, new_ui, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] 15_Financas.py — bloco de gráfico não encontrado.")

# ============================================================
# 3. API (Alerta de Orçamento no Telegram)
# ============================================================
def fix_api_budget_alert() -> None:
    p = BASE / "api_samurai.py"
    txt = read(p)

    if "Orçamento estourado" in txt:
        print("[SKIP] api_samurai.py — alerta de orçamento já existe.")
        return

    old_telegram_photo = '''                        msg = f"✅ Gasto registrado: *{data.get('description')}*\\n"
                        msg += f"Valor: R$ {data.get('amount'):.2f}\\n"
                        msg += f"Categoria: {data.get('category')}"
                        reply(msg)'''

    new_telegram_photo = '''                        msg = f"✅ Gasto registrado: *{data.get('description')}*\\n"
                        msg += f"Valor: R$ {data.get('amount'):.2f}\\n"
                        msg += f"Categoria: {data.get('category')}\\n"
                        
                        # Checagem de Orçamento
                        try:
                            cat = data.get('category', 'Outros')
                            budget = query_one("SELECT limit_amount FROM budgets WHERE category = ?", (cat,))
                            if budget:
                                # Soma os gastos do mês atual nesta categoria
                                mes_atual = date.today().strftime("%Y-%m")
                                gastos_cat = query_all("SELECT amount FROM expenses WHERE category = ? AND expense_date LIKE ?", (cat, f"{mes_atual}%"))
                                total_gasto = sum(float(g['amount']) for g in gastos_cat) if gastos_cat else 0.0
                                
                                perc = (total_gasto / float(budget['limit_amount'])) * 100
                                if perc >= 100:
                                    msg += f"\\n🚨 **ORÇAMENTO ESTOURADO!** Você já gastou {perc:.0f}% do teto de {cat}."
                                elif perc >= 80:
                                    msg += f"\\n⚠️ **Atenção:** Você já usou {perc:.0f}% do seu orçamento de {cat}."
                        except Exception as e:
                            print(f"Erro ao checar orçamento: {e}")
                            
                        reply(msg)'''

    if old_telegram_photo in txt:
        txt = txt.replace(old_telegram_photo, new_telegram_photo, 1)
        write_validated(p, txt)
    else:
        print("[AVISO] api_samurai.py — bloco de resposta de foto não encontrado.")

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: controle de orcamento mensal e alertas proativos no telegram"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
        
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
    print("V8.2 — CONTROLE DE ORÇAMENTO E ALERTAS")
    print("=" * 60)

    fix_schema_budgets()
    fix_financas_budget_ui()
    fix_api_budget_alert()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\nO que testar agora:")
    print("1. Espere o Render e o Streamlit atualizarem (1-2 min).")
    print("2. Vá na aba '💸 Finanças' e clique em '⚙️ Configurar Orçamento Mensal'.")
    print("3. Defina um teto baixo para 'Lazer' (ex: R$ 50) só para testar.")
    print("4. Vá no Telegram e envie uma foto de comprovante com categoria 'Lazer' e valor '60'.")
    print("5. Veja a mágica acontecer: o bot vai te avisar na hora que você estourou o orçamento!")

if __name__ == "__main__":
    aplicar()