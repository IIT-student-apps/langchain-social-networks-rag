import streamlit as st
from api_utils import get_api_response

MODELS={"yandexGPT":"denisavetisyan/saiga_yandexgpt_8b_gguf_q5_k_m:latest", "gpt-4o":"gpt-4o",\
         "gpt-4o-mini":"gpt-4o-mini", "llama3":"llama3:latest"}

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