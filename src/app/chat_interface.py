import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.core.config import LLM_CONFIGS, ACTIVE_MODEL
from src.app.api_utils import get_api_response

MODELS = {key: cfg["model"] for key, cfg in LLM_CONFIGS.items()}

def display_chat_interface():
    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Вопрос:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Генерация ответа..."):
            response = get_api_response(prompt, st.session_state.session_id, MODELS[st.session_state.model])
            
            if response:
                st.session_state.session_id = response.get('session_id')
                st.session_state.messages.append({"role": "assistant", "content": response['answer']})
                
                with st.chat_message("assistant"):
                    st.markdown(response['answer'])
                    
            else:
                st.error("Ошибка при получении ответа из API. Пожалуйста, повторите позже.")