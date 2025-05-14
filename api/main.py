from fastapi import FastAPI, File, UploadFile, HTTPException
from api.pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest, UserInfo, UserToken
from api.langchain_utils import get_rag_chain
from api.db_utils import insert_application_logs, get_chat_history, get_all_documents, insert_document_record, delete_document_record
from api.chroma_utils import index_document_to_chroma, delete_doc_from_chroma
import os
import uuid
import logging
import shutil

from api.vk.vkapi import get_self_vk_profile, get_vk_chat, get_vk_profile, get_all_vk_chat

from api.vk.tokken_grabber import token_updater

import api.vk.tokken_grabber as vkapi

from api.conversation import parse_vk_messages, conversation_to_prompt

import asyncio

app = FastAPI()


@app.post("/get_token", response_model=UserToken)
async def get_token():
    if vkapi.state.running:
        return UserToken(
            status="already_running",
            token=vkapi.state.token,
            message="Фоновая задача уже запущена"
        )
    
    try:
        vkapi.state.running = True
        vkapi.state.task = asyncio.create_task(token_updater())
        #while not vkapi.state.token and vkapi.state.running:pass
        return UserToken(
            status="started",
            message="Фоновая задача запущена",
            token=vkapi.state.token
        )
    except Exception as e:
        vkapi.state.running = False
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка запуска фоновой задачи: {str(e)}"
        )

@app.get("/self_user/profile", response_model=UserInfo)
async def get_token_status():
    #while not vkapi.state.token and vkapi.state.running:pass
    response = get_self_vk_profile(vkapi.state.token)
    return UserInfo(first_name=response['first_name'], last_name=response['last_name'], user_id=response['id'])
    # return UserToken(
    #     status="running" if vkapi.state.running else "stopped",
    #     token=vkapi.state.token
    # )

@app.post("/token/stop", response_model=UserToken)
async def stop_token_updater():
    if not vkapi.state.running:
        return UserToken(
            status="not_running",
            message="Фоновая задача не запущена"
        )
    
    vkapi.state.running = False
    if vkapi.state.task:
        vkapi.state.task.cancel()
    if vkapi.state.browser:
        await vkapi.state.browser.close()
    
    return UserToken(
        status="stopped",
        message="Фоновая задача остановлена"
    )

@app.on_event("shutdown")
async def shutdown_event():
    if vkapi.state.running:
        await stop_token_updater()



@app.get("/get_chat/all", response_model=list)
def get_all_chat():
    response = get_all_vk_chat(vkapi.state.token)
    if response:
        return response

@app.get("/get_chat", response_model=str)
def get_chat(screen_name: str):
    response = get_vk_chat(vkapi.state.token, get_id(screen_name).user_id)
    if not response:
        return
    conv = parse_vk_messages(response, vkapi.state.token)
    conv_text = conversation_to_prompt(conv)
    #print(conv_text)
    return conv_text

@app.get("/user/profile", response_model=UserInfo)
def get_id(screen_name: str):
    response = get_vk_profile(vkapi.state.token, screen_name)
    return UserInfo(first_name=response['first_name'], last_name=response['last_name'], user_id=response['id'])







# КОВАЛЁВ ЭДИШН
@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    session_id = query_input.session_id or str(uuid.uuid4())
    logging.info(f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}")

    chat_history = get_chat_history(session_id)
    print(query_input.model.value)
    rag_chain = get_rag_chain(query_input.model.value)
    answer = rag_chain.invoke({
        "input": query_input.question,
        "chat_history": chat_history
    })['answer']

    insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
    logging.info(f"Session ID: {session_id}, AI Response: {answer}")
    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)

@app.post("/upload-doc")
def upload_and_index_document(file: UploadFile = File(...)):
    allowed_extensions = ['.pdf', '.docx', '.html']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}")

    temp_file_path = f"temp_{file.filename}"

    try:
        # Save the uploaded file to a temporary file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_id = insert_document_record(file.filename)
        success = index_document_to_chroma(temp_file_path, file_id)

        if success:
            return {"message": f"File {file.filename} has been successfully uploaded and indexed.", "file_id": file_id}
        else:
            delete_document_record(file_id)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/list-docs", response_model=list[DocumentInfo])
def list_documents():
    return get_all_documents()

@app.post("/delete-doc")
def delete_document(request: DeleteFileRequest):
    chroma_delete_success = delete_doc_from_chroma(request.file_id)

    if chroma_delete_success:
        db_delete_success = delete_document_record(request.file_id)
        if db_delete_success:
            return {"message": f"Successfully deleted document with file_id {request.file_id} from the system."}
        else:
            return {"error": f"Deleted from Chroma but failed to delete document with file_id {request.file_id} from the database."}
    else:
        return {"error": f"Failed to delete document with file_id {request.file_id} from Chroma."}

