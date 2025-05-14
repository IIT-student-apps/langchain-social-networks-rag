import requests
import streamlit as st


def get_all_conv():
    ids = requests.get("http://localhost:8000/get_chat/all")
    if ids:
        return ids
    else:
        return None

def get_conversation(screen_name):
    text = requests.get("http://localhost:8000/get_chat", params={"screen_name": screen_name})
    if text:
        return text
    else:
        st.error(f"Ошибка получения пользователя @{screen_name}")
        return None

def get_user_profile():
    user_info = requests.get("http://localhost:8000/self_user/profile")
    if user_info:
        return user_info.json()
    else:
        st.error(f"Ошибка при загрузке данных пользователя")
        return None

def get_token():
    user_info = requests.post("http://localhost:8000/get_token")
    if user_info:
        return user_info.json()
    else:
        st.error(f"Ошибка получения токена доступа")
        return None











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