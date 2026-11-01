import json
import streamlit as st
from pathlib import Path
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

def get_api_key() -> str:
    # Tenta pegar dos Secrets do Streamlit Cloud (Nuvem)
    try:
        if "gemini_api_key" in st.secrets:
            return st.secrets["gemini_api_key"]
    except Exception:
        pass
        
    # Fallback local (config.json)
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("gemini_api_key", "")
        except Exception:
            pass
    return ""

def _extrair_texto(response) -> str:
    """Função auxiliar para extrair texto com segurança."""
    if response and hasattr(response, "text"):
        return response.text
    return "⚠️ A IA não retornou texto (resposta vazia)."

def ask_gemini(prompt: str) -> str:
    api_key = get_api_key()
    if not api_key or api_key == "COLE_SUA_CHAVE_AQUI":
        return "⚠️ API Key não configurada."
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt
        )
        return _extrair_texto(response)
    except Exception as e:
        return f"⚠️ Erro na IA: {str(e)}"

def ask_gemini_vision(image_bytes: bytes, prompt: str) -> str:
    api_key = get_api_key()
    if not api_key or api_key == "COLE_SUA_CHAVE_AQUI":
        return "⚠️ API Key não configurada."
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                prompt
            ]
        )
        return _extrair_texto(response)
    except Exception as e:
        return f"⚠️ Erro na IA (Visão): {str(e)}"
