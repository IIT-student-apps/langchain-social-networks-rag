import streamlit as st
from api_utils import upload_document, list_documents, delete_document, get_token, get_user_profile, get_conversation

def display_sidebar():
    # Sidebar: Model Selection

    with st.sidebar.container():
        st.header("Пользователь", help="Для работы с данными ваших переписок необходимо привязать свой аккаунт")

        text_placeholder = st.empty() 
        if st.button("Привязать"):
            get_token()

        
        if st.sidebar.button("Показать пользователя"):
            user_info = get_user_profile()
            if user_info:
                text_placeholder.subheader('\t'+user_info.get('first_name')+' '+user_info.get('last_name'))
    
    with st.sidebar.expander("*Документы*"):

        st.header("Загрузить документ",help="Есть возможность загрузить выбранный вами документ")
        uploaded_file = st.file_uploader("Выбрать файл", type=["pdf", "docx", "html"])
        if uploaded_file:
            if st.button("Загрузить"):
                with st.spinner("Загрузка..."):
                    upload_response = upload_document(uploaded_file)
                    if upload_response:
                        st.success(f"Файл '{uploaded_file.name}' был успешно загружен под ID {upload_response['file_id']}.")
                        st.session_state.documents = list_documents()  # Refresh the list after upload

    # Sidebar: List Documents
        st.header("Загруженные документы")
        if st.button("Обновить список документов"):
            with st.spinner("Обновление..."):
                st.session_state.documents = list_documents()

    # Initialize document list if not present
        if "documents" not in st.session_state:
            st.session_state.documents = list_documents()

        documents = st.session_state.documents
        if documents:
            for doc in documents:
                st.text(f"{doc['filename']} (ID: {doc['id']}, Загружен: {doc['upload_timestamp']})")
        
        # Delete Document
            selected_file_id = st.selectbox("Выбрать документы для удаления", options=[doc['id'] for doc in documents], format_func=lambda x: next(doc['filename'] for doc in documents if doc['id'] == x))
            if st.button("Удалить документы"):
                with st.spinner("Удаление..."):
                    delete_response = delete_document(selected_file_id)
                    if delete_response:
                        st.success(f"Документ под ID {selected_file_id} был успешно удалён.")
                        st.session_state.documents = list_documents()  # Refresh the list after deletion
                    else:
                        st.error(f"Ошибка при удалении документа под ID {selected_file_id}.")
    
    st.sidebar.header("Варианты использования")
    st.sidebar.info("""
        
    Перед использованием привяжите свой аккаунт к сессии.
                        
    Это можно сделать по кнопке *Привязать*, после чего вам потребуется авторизация в ВКонтакте.
                    
    **Важно**: во время сессии не закрывайте вкладку ВКонтакте, так как требуется постоянный доступ к вашим данным.
    """)
    st.sidebar.markdown("""
        <div style="border: 2px solid #ff4b4b; padding: 10px; border-radius: 5px;">
                        
    Используйте :red[@name] (короткое имя) пользователя для получения вашей переписки с ним.

    *Что мы в последний раз обсуждали с :red[@name]*

    Допускается использование нескольких чатов.
                        
    *Что общего было в разговорах с :red[@name1] и :red[@name2]*      

    Дальнейшее использование данной переписки не требует обращение по :red[@name1] 
         </div>           
        """, unsafe_allow_html=True)