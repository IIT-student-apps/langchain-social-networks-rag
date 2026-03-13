import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.core.config import LLM_CONFIGS, ACTIVE_MODEL
from src.app.api_utils import upload_document, list_documents, delete_document

def display_sidebar():
    # Sidebar: Model Selection
    model_options = list(LLM_CONFIGS.keys())
    default_index = model_options.index(ACTIVE_MODEL) if ACTIVE_MODEL in model_options else 0
    st.sidebar.selectbox("Модель", options=model_options, index=default_index, key="model")
    

    # Sidebar: Upload Document
    st.sidebar.header("Загрузить документ")
    uploaded_file = st.sidebar.file_uploader("Выбрать файл", type=["pdf", "docx", "html"])
    if uploaded_file is not None:
        if st.sidebar.button("Загрузить"):
            with st.spinner("Загрузка..."):
                upload_response = upload_document(uploaded_file)
                if upload_response:
                    st.sidebar.success(f"Файл '{uploaded_file.name}' был успешно загружен под ID {upload_response['file_id']}.")
                    st.session_state.documents = list_documents()  # Refresh the list after upload

    # Sidebar: List Documents
    st.sidebar.header("Загруженные документы")
    if st.sidebar.button("Обновить список документов"):
        with st.spinner("Обновление..."):
            st.session_state.documents = list_documents()

    # Initialize document list if not present
    if "documents" not in st.session_state:
        st.session_state.documents = list_documents()

    documents = st.session_state.documents
    if documents:
        for doc in documents:
            st.sidebar.text(f"{doc['filename']} (ID: {doc['id']}, Загружен: {doc['upload_timestamp']})")
        
        # Delete Document
        selected_file_id = st.sidebar.selectbox("Выбрать документы для удаления", options=[doc['id'] for doc in documents], format_func=lambda x: next(doc['filename'] for doc in documents if doc['id'] == x))
        if st.sidebar.button("Удалить документы"):
            with st.spinner("Удаление..."):
                delete_response = delete_document(selected_file_id)
                if delete_response:
                    st.sidebar.success(f"Документ под ID {selected_file_id} был успешно удалён.")
                    st.session_state.documents = list_documents()  # Refresh the list after deletion
                else:
                    st.sidebar.error(f"Ошибка при удалении документа под ID {selected_file_id}.")