import streamlit as st
from api_utils import get_api_response, get_conversation, get_all_conv

import re



# MODELS={"yandexGPT":"denisavetisyan/saiga_yandexgpt_8b_gguf_q5_k_m:latest", "gpt-4o":"gpt-4o",\
#          "gpt-4o-mini":"gpt-4o-mini", "llama3":"llama3:latest"}

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

            pattern = r'@\w+'
            for screen_name in re.findall(pattern, prompt, re.IGNORECASE):
                if screen_name == "@all": # Лучше не использовать, а то долго будет
                    for conv_id in get_all_conv():
                        conv += get_conversation('id'+conv_id)
                else:
                    conv = get_conversation(screen_name[1:])
                    if not conv:
                        return
                pattern = re.escape(screen_name)
                prompt = re.sub(pattern, conv, prompt, flags=re.IGNORECASE)
                 
                print(prompt)
            response = get_api_response(prompt, st.session_state.session_id, "denisavetisyan/saiga_yandexgpt_8b_gguf_q5_k_m:latest")
            
            if response:
                st.session_state.session_id = response.get('session_id')
                st.session_state.messages.append({"role": "assistant", "content": response['answer']})
                
                with st.chat_message("assistant"):
                    st.markdown(response['answer'])
                    
            else:
                st.error("Ошибка при получении ответа из API. Пожалуйста, повторите позже.")