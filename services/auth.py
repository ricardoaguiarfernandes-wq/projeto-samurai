import streamlit as st
import hashlib
import time

def check_password():
    """Retorna True se o usuário digitou a senha correta."""
    
    def password_entered():
        """Verifica se a senha digitada está correta comparando os hashes."""
        try:
            # Pega a senha configurada nos Secrets (Nuvem) ou variável de ambiente
            senha_correta = st.secrets.get("app_password", "samurai123") # fallback local para testes
            
            # Cria o hash SHA-256 da senha digitada e da senha correta
            input_hash = hashlib.sha256(st.session_state["password"].encode()).hexdigest()
            correct_hash = hashlib.sha256(senha_correta.encode()).hexdigest()
            
            if input_hash == correct_hash:
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Não guarda a senha na memória
            else:
                st.session_state["password_correct"] = False
                time.sleep(1) # Pequena pausa para evitar ataques de força bruta
        except Exception as e:
            st.error(f"Erro ao ler a senha: {e}")
            st.session_state["password_correct"] = False

    # Se já estiver autenticado, libera o acesso
    if st.session_state.get("password_correct", False):
        return True

    # Desenha a tela de login
    st.markdown("<h1 style='text-align: center; margin-top: 100px;'>⚔️ Projeto Samurai</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #CCC;'>Acesso Restrito</p>", unsafe_allow_html=True)
    
    st.text_input(
        "Senha Mestra", 
        type="password", 
        on_change=password_entered, 
        key="password",
        placeholder="Digite sua senha...",
        help="A senha local padrão é: samurai123"
    )
    
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Senha incorreta. Tente novamente. (Dica: use 'samurai123' no PC)")
    return False
