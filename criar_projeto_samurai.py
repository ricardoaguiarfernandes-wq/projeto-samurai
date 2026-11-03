"""
criar_projeto_samurai.py — V9.1 (Grimórios de Filosofia e Presença)

ENTREGAS:
1. ASSETS: Cria os arquivos de texto 'grimorio_proibido.txt' e 'grimorio_presenca.txt'.
2. UI (12_Filosofia.py): Adiciona 2 novas abas e a lógica de paginação (Leitura Diária).
3. IA: Cria o botão "Gerar Aula Prática com IA" focado no capítulo do dia.

REGRA DE OURO: 'gemini-3.5-flash-lite' permanece INTOCÁVEL.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ASSETS_DIR = BASE / "assets"

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
# 1. CRIAR OS ARQUIVOS DE TEXTO (ASSETS)
# ============================================================
def create_text_files() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Texto do Grimório Proibido (Início)
    proibido_path = ASSETS_DIR / "grimorio_proibido.txt"
    if not proibido_path.exists():
        conteudo_proibido = """GRIMÓRIO PROIBIDO
FACA QUALQUER MULHER TE DESEJAR COM UMA FRASE

PRÓLOGO - A CARTA AO INICIADO

Se este livro chegou nas suas mãos, não foi por acaso. Eu não sei quem te indicou. Não sei o que te fez parar na capa. Não sei o que aconteceu na sua vida antes desta página. Mas sei de uma coisa: alguma parte de você já desconfiava que estava jogando o jogo errado. Você tentou ser bom. Tentou ser educado. Tentou ser engraçado. Tentou ser interessante. Tentou ser o cara legal, o cara firme, o cara confiante, o cara misterioso. Tentou copiar conselhos da internet, frases prontas, gurus de Instagram, vídeos do YouTube com milhões de visualizações. Algumas coisas funcionaram. A maioria não.

E o pior: quando funcionou, você não soube por quê. Quando falhou, você também não soube por quê. É como se existisse um jogo invisível sendo jogado ao seu redor, com regras que ninguém te explicou, e você ficasse ali no meio do tabuleiro, fazendo movimentos no escuro, esperando dar sorte. Eu já estive aí. Cada homem que vale alguma coisa já esteve.

E é por isso que este livro existe.

Antes de continuar, preciso te dizer uma coisa que talvez te incomode. Este livro não é sobre conquistar mulheres. Calma. Antes que você feche, me escuta. Este livro é sobre entender o desejo. Sobre entender a mente feminina. Sobre entender o jogo social que acontece toda vez que dois seres humanos se olham, se aproximam, se medem, se desejam, se rejeitam, se enfeitiçam. E sobre entender, no fim das contas, você mesmo. Porque a verdade que ninguém te contou é simples: o homem que conquista mulheres de verdade não é o homem que aprendeu técnicas. É o homem que aprendeu a enxergar. A mulher. O mundo. A si próprio.

Conquistar é consequência. Enxergar é o trabalho.

Eu chamo o leitor deste livro de Iniciado. Não por arrogância. Não por brincadeira mística. Mas porque é o que você é, neste momento, na primeira página. Iniciado é o homem que percebeu que existe alguma coisa que ele ainda não sabe. Que existe um nível de compreensão que ele ainda não acessou. Que existe uma versão dele esperando para ser construída, e ele finalmente decidiu fazer a travessia. Não é elogio. É descrição. Você está aqui porque alguma coisa em você sabe que existe mais.

CAPÍTULO I - A GRANDE MENTIRA

Antes de qualquer coisa, eu preciso te tirar uma ilusão da cabeça. Não tem outro jeito. Se a ilusão ficar, nada do que vem depois neste livro vai funcionar. Vai ser como tentar construir uma casa em cima de areia. Bonito por uns dias, ruína em semanas. A ilusão é esta: Você acredita que sedução é alguma coisa que você faz. Uma técnica. Uma frase. Uma postura. Um truque. Um movimento. Um gesto certo no momento certo. Você acredita que existe, em algum lugar, uma linha mágica. Uma sequência de palavras. Um jeito específico de chegar. E que, se você descobrir essa fórmula, vai conseguir conquistar a mulher que você quer.

Eu já acreditei nisso também. A maioria dos homens acredita. Tem indústria inteira ganhando dinheiro com essa crença. Mas é mentira. E enquanto você acreditar nela, vai continuar fracassando com mulheres importantes. Vai continuar tendo resultado raso com mulheres rasas. Vai continuar achando que faltou "encontrar o estilo certo de cantada".

Olha. Eu quero que você pense, agora, em algum homem que você conhece que tem facilidade absurda com mulheres. Não o do filme. Não o do Instagram. Um cara real. Um amigo. Um conhecido. Aquele primo. Aquele colega de trabalho. Aquele cara que você cresceu vendo. Pensa nele. Ele é o mais bonito do seu círculo? Provavelmente não. Ele tem o corpo mais trabalhado? Provavelmente não. Ele tem o maior salário? O carro mais caro? A roupa mais cara? Provavelmente não. Ele decora frases prontas? Treina abordagem na frente do espelho? Lê livros de pickup? Quase certamente não.

E ainda assim, mulheres se aproximam dele. Conversam mais demoradamente. Riem mais do que precisariam rir. Dão atenção que outros caras pagariam para receber. Por quê?

Essa pergunta é o primeiro portal. Se você não responder ela com honestidade, o livro não funciona. A resposta não é carisma. Carisma é palavra-coringa que ninguém sabe explicar. A resposta também não é "ele é seguro de si". Isso é vago demais. Existe segurança falsa, segurança performada, segurança decorada. Mulher reconhece essas em três segundos. A resposta verdadeira é esta:

Esse homem não está fazendo nada. Esse homem está sendo. E ser, para o cérebro feminino, é mil vezes mais magnético do que fazer.

Eu quero que você grave isso na medula. Sedução não é o que você faz na frente dela. Sedução é o que você é antes de chegar perto dela. Releia essa frase. Devagar. Sedução não é o que você faz na frente dela. Sedução é o que você é antes de chegar perto dela. Essa frase, sozinha, vale o preço deste livro. Se você sair daqui só com ela, e ela for plantada de verdade, sua vida com mulheres já vai começar a mudar.

(Nota: Para adicionar o resto do livro, basta abrir o arquivo `assets/grimorio_proibido.txt` na sua pasta e colar o restante do texto do PDF. O app dividirá automaticamente por capítulos)."""
        proibido_path.write_text(conteudo_proibido, encoding="utf-8")
        print("[OK] assets/grimorio_proibido.txt criado.")

    # Texto do Grimório da Presença (Início)
    presenca_path = ASSETS_DIR / "grimorio_presenca.txt"
    if not presenca_path.exists():
        conteudo_presenca = """GRIMÓRIO DA PRESENÇA
O dossiê da linguagem não verbal masculina

CAPÍTULO 1 - O JULGAMENTO DE MEIO SEGUNDO

Eu tenho duas gravações que mudaram a minha vida. E vão mudar a sua. Nas duas, sou eu, na mesma rua, na mesma semana, abordando duas mulheres parecidas com quase as mesmas palavras. Na primeira, ela sorri por educação, olha o relógio e vai embora em trinta segundos. Na segunda, ela ri, o corpo dela vira inteiro na minha direção, e no fim ela digita o número dela no meu celular.

Passei uma madrugada alternando entre os dois vídeos, procurando a frase mágica que eu teria dito num e não no outro. Não existia. As palavras eram praticamente idênticas. Então eu tirei o som.

E no mudo, os dois vídeos se tornaram duas cenas completamente diferentes. No primeiro, um homem de ombros comprimidos, peso trocando de perna, mãos inquietas, queixo levemente baixo — um homem pedindo desculpas por existir. No segundo, um homem parado, aberto, sem pressa — um homem confortável no próprio corpo. Ela não escolheu entre duas frases. Escolheu entre dois homens.

Naquela madrugada nasceu a pergunta que me consumiu pelos cinco anos seguintes — anos em que gravei e analisei mais de quinhentas horas das minhas próprias interações, virei estudioso obsessivo de tudo que a ciência da comunicação já produziu, e depois treinei centenas de pessoas pelo Brasil: Se não são as palavras... o que é? Este livro é a resposta. E ela começa aqui.

O mecanismo
O cérebro humano forma uma impressão de outra pessoa em menos de um segundo — antes da primeira frase terminar, frequentemente antes de começar. Pesquisadores de psicologia social mediram isso repetidas vezes: mostraram rostos e trechos mudos de segundos a voluntários, e as avaliações feitas nesse piscar de olhos previam com precisão assustadora as avaliações feitas após longa convivência. Não é julgamento raso que depois se corrige. É a veredito — o resto da interação, na maioria dos casos, apenas o confirma.

Por que o cérebro faz isso? Porque foi construído num mundo em que decidir devagar se um estranho era ameaça custava a vida. O julgamento instantâneo não é grosseria — é o software de fábrica de todos nós. Você faz o mesmo, o tempo todo, sem perceber.

A consequência é a lei fundamental deste livro: você não se comunica quando decide falar. Você se comunica desde que se torna visível. Sua caminhada fala. Sua postura fala. Seu rosto em repouso fala. Seu silêncio fala. As palavras — que a escola, os pais e a vida inteira te disseram serem "a comunicação" — chegam por último, num tribunal onde a sentença já está quase assinada.

CAPÍTULO 2 - AS DUAS PERGUNTAS

Toda vez que você aparece na frente de um ser humano, o cérebro dele te faz duas perguntas. Ele não escolhe fazê-las — elas rodam sozinhas, herdadas de um passado em que errar a resposta custava a vida:

Pergunta 1: "Eu posso confiar nessa pessoa?" — É amigo ou ameaça? Ela está do meu lado?
Pergunta 2: "Essa pessoa é capaz?" — Ela tem força, competência, valor? Ela importa?

A ciência da percepção social chama as respostas de calor e força (ou competência) — e décadas de pesquisa convergem num achado brutal: esses dois eixos explicam a esmagadora maioria de toda impressão que formamos de qualquer pessoa. Todo julgamento humano sobre você é, no fundo, um par de notas: quanto calor, quanta força.

Os quatro destinos
Calor alto + força baixa = o Fofo. Confiável, querido... e dispensável. É o "gente boa" que todo mundo gosta e ninguém respeita, promove ou deseja. Ouve "você é um amor" no trabalho e "você é como um irmão pra mim" no amor — as duas frases são o mesmo diagnóstico: confio em você, mas você não tem peso. A maioria das pessoas boas do mundo mora aqui, sem entender por que bondade não vira resultado.

Força alta + calor baixo = o Intimidante. Respeitado, admirado de longe... e evitado. É o competente que não é chamado pro almoço, o chefe de quem se esconde o problema, a pessoa "difícil de conversar". Ouve "você é meio fechado, né?" a vida inteira e acha que o problema são os outros.

Calor baixo + força baixa = o Invisível. Nem ameaça, nem valor: o cérebro alheio faz a coisa mais econômica que existe — apaga. É a pessoa que ninguém nota que chegou nem que saiu.

Calor alto + força alta = o Magnético. O raro. A pessoa perto de quem os outros se sentem, ao mesmo tempo, seguros e elevados. É o único quadrante em que confiança e desejo, afeto e respeito, coexistem. Carisma, essa palavra mística, tem definição técnica e é só isso: calor e força transmitidos simultaneamente.

(Nota: Para adicionar o resto do livro, basta abrir o arquivo `assets/grimorio_presenca.txt` na sua pasta e colar o restante do texto. O app dividirá automaticamente por capítulos)."""
        presenca_path.write_text(conteudo_presenca, encoding="utf-8")
        print("[OK] assets/grimorio_presenca.txt criado.")

# ============================================================
# 2. ATUALIZAR A PÁGINA DE FILOSOFIA
# ============================================================
def update_filosofia_page() -> None:
    p = BASE / "ui" / "pages" / "12_Filosofia.py"
    txt = read(p)

    if "Grimório Proibido" in txt:
        print("[SKIP] 12_Filosofia.py — Grimórios já integrados.")
        return

    new_content = '''import streamlit as st
import sys
import re
from pathlib import Path
from datetime import date

_p = Path(__file__).resolve().parents[2]
if str(_p) not in sys.path:
    sys.path.insert(0, str(_p))

from core.database import execute, query_one
from services.ai import ask_gemini

BASE_DIR = Path(__file__).resolve().parents[2]
ASSETS_DIR = BASE_DIR / "assets"

st.title("🏛️ Filosofia & Sabedoria")

tab_video, tab_debate, tab_gp, tab_gpres = st.tabs([
    "🎬 Aula em Vídeo", 
    "🧠 Debate Socrático", 
    "🕵️ Grimório Proibido", 
    "👑 Grimório da Presença"
])

with tab_video:
    st.header("Assistir Aula (COF ou outros)")
    video_link = st.text_input("Cole o link do vídeo (YouTube):", placeholder="https://www.youtube.com/watch?v=...")
    if video_link:
        try:
            st.video(video_link)
            if st.button("🧠 Resumir Aula com IA", use_container_width=True):
                with st.spinner("Preparando resumo..."):
                    prompt = f"Atue como professor de filosofia. Crie um resumo dos principais conceitos e 3 perguntas de reflexão sobre a aula contida no link: {video_link}"
                    st.markdown(f"""<div class="samurai-card" style="border-left-color: #F9A825;"><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)
        except:
            st.error("Link de vídeo inválido.")

with tab_debate:
    st.header("Desafio Intelectual do Dia")
    PROMPTS = ["O que é a verdadeira ignorância: não saber, ou saber e não aplicar?", "O que a sua rotina diz sobre a sua visão de mundo?", "Como a ordem no ambiente físico reflete a ordem da mente?"]
    prompt_hoje = PROMPTS[date.today().toordinal() % len(PROMPTS)]
    st.markdown(f"""<div class="samurai-card"><div class="titulo">Reflexão</div><div class="valor" style="font-size:1.2rem;">{prompt_hoje}</div></div>""", unsafe_allow_html=True)
    
    with st.form("form_fil"):
        refl = st.text_area("Sua resposta:")
        if st.form_submit_button("Debater com Mentor", use_container_width=True) and refl:
            with st.spinner("Analisando..."):
                prompt = f"Atue como mentor COF. Tema: '{prompt_hoje}'. Usuário disse: '{refl}'. Aponte uma falha lógica e faça 1 pergunta socrática."
                st.markdown(f"""<div class="samurai-card" style="border-left-color: #2196F3;"><div style="white-space: pre-wrap;">{ask_gemini(prompt)}</div></div>""", unsafe_allow_html=True)

def show_book_tab(filename, book_name):
    filepath = ASSETS_DIR / filename
    if not filepath.exists():
        st.error(f"Arquivo {filename} não encontrado na pasta assets. Rode o script de melhoria novamente.")
        return

    text = filepath.read_text(encoding="utf-8")
    # Divide o texto por "CAPÍTULO" ou "PARTE" ou marcadores de início
    chapters = re.split(r'(?i)\\n\\s*(?:CAPÍTULO|PARTE|PRÓLOGO|C A P Í T U L O)\\s+[IVXLCDM\\d]+', text)
    chapters = [c.strip() for c in chapters if len(c.strip()) > 100]
    
    if not chapters:
        st.info("Nenhum capítulo formatado encontrado no texto.")
        return

    state_key = f"idx_{filename}"
    if state_key not in st.session_state:
        st.session_state[state_key] = 0

    idx = st.session_state[state_key]
    if idx >= len(chapters):
        idx = 0
        st.session_state[state_key] = 0

    st.subheader(f"📖 {book_name} — Módulo {idx+1} de {len(chapters)}")
    
    # Área de Leitura
    with st.expander("Ler o texto base deste módulo", expanded=True):
        # Exibe uma versão truncada para não travar a tela, o texto completo fica no contexto da IA
        display_text = chapters[idx][:3000] + "\\n\\n[...]*(O texto continua, use a IA para aprofundar)*" if len(chapters[idx]) > 3000 else chapters[idx]
        st.markdown(f"<div style='white-space: pre-wrap; line-height: 1.6;'>{display_text}</div>", unsafe_allow_html=True)

    # Navegação
    col1, col2 = st.columns(2)
    if col1.button("⬅️ Módulo Anterior", key=f"prev_{filename}", use_container_width=True):
        st.session_state[state_key] = max(0, idx - 1)
        st.rerun()
    if col2.button("Próximo Módulo ➡️", key=f"next_{filename}", use_container_width=True):
        st.session_state[state_key] = min(len(chapters) - 1, idx + 1)
        st.rerun()

    st.divider()
    
    # Aula com IA
    st.write("#### 🎓 Aula do Mentor")
    if st.button("🧠 Gerar Aula Prática com IA", key=f"ia_{filename}", use_container_width=True):
        with st.spinner("O Mentor está preparando sua aula diária..."):
            prompt = f"""Atue como o mestre e mentor Felipe Alves, ensinando os conceitos dos seus livros.
O usuário está estudando o livro '{book_name}'.
Aqui está o trecho do módulo de hoje:
{chapters[idx][:6000]}

Sua missão:
1. Crie 3 tópicos de reflexão sobre o texto (explicando o conceito de forma clara).
2. Crie 1 exercício prático para o usuário aplicar HOJE na vida real (ex: "Hoje, observe a postura das pessoas no elevador", "Ao conversar com alguém, faça a pausa de 2 segundos antes de responder").
3. Dê uma frase de impacto final, estilo Samurai.
Seja direto, empolgante e prático.
"""
            resposta = ask_gemini(prompt)
            st.markdown(f'<div class="samurai-card" style="border-left-color: #F9A825;"><div class="titulo">Aula: {book_name}</div><div style="white-space: pre-wrap;">{resposta}</div></div>', unsafe_allow_html=True)

with tab_gp:
    show_book_tab("grimorio_proibido.txt", "Grimório Proibido")

with tab_gpres:
    show_book_tab("grimorio_presenca.txt", "Grimório da Presença")
'''
    write_validated(p, new_content)

def sync_git() -> None:
    print("\n" + "=" * 60)
    print("SINCRONIZANDO COM O GITHUB")
    print("=" * 60)

    _git_run_safe(["add", "-A"])
    _git_run_safe(["commit", "-m", "feat: adiciona abas dos grimorios com leitura diaria e aulas com IA"])
    
    r = _git_run_safe(["push", "origin", "main"])
    if r.returncode == 0:
        print("[OK] Push concluído com sucesso!")
    else:
        print(f"[ERRO] Push falhou:\n{r.stderr}")

def aplicar() -> None:
    print("=" * 60)
    print("V9.1 — GRIMÓRIOS DE FILOSOFIA")
    print("=" * 60)

    create_text_files()
    update_filosofia_page()
    sync_git()

    print("\n" + "=" * 60)
    print("✅ CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print("\n⚠️ PASSO IMPORTANTE:")
    print("1. O script criou os arquivos na pasta 'assets/' com o início dos livros.")
    print("2. Vá até a pasta 'assets', abra 'grimorio_proibido.txt' e 'grimorio_presenca.txt'.")
    print("3. Cole o restante do texto dos seus PDFs nesses arquivos.")
    print("4. O app do Streamlit vai dividir o texto automaticamente em capítulos e você poderá ler 1 por dia!")

if __name__ == "__main__":
    aplicar()