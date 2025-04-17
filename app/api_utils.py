import requests
import streamlit as st

def get_api_response(question, session_id, model):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        "question": question,
        "model": model
    }
    if session_id:
        data["session_id"] = session_id

    try:
        response = requests.post("http://localhost:8000/chat", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Ошибка API запроса под кодом {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Произошла ошибка: {str(e)}")
        return None

def upload_document(file):
    print("Загрузка файла...")
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post("http://localhost:8000/upload-doc", files=files)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Ошибка при загрузке файла. Ошибка: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Произошла ошибка при загрузке файла: {str(e)}")
        return None

def list_documents():
    try:
        response = requests.get("http://localhost:8000/list-docs")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Ошибка получения списка документов. Ошибка: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"Произошла ошиибка при получении списка документов: {str(e)}")
        return []

def delete_document(file_id):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {"file_id": file_id}

    try:
        response = requests.post("http://localhost:8000/delete-doc", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Ошибка при удалении документа. Ошибка: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Произошла ошибка при удалении документа: {str(e)}")
        return None