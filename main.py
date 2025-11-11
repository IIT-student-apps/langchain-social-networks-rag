# api/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import logging
import shutil
import os

from langchain_utils import get_rag_chain
from db_utils import (
    insert_application_logs, get_chat_history,
    insert_document_record, delete_document_record, get_all_documents
)
from chroma_utils import index_document_to_chroma, delete_doc_from_chroma

app = FastAPI(title="VK Social RAG API")

class QueryInput(BaseModel):
    question: str
    session_id: Optional[str] = None
    model: str = "qwen3:4b"

class QueryResponse(BaseModel):
    answer: str
    session_id: str

@app.post("/chat", response_model=QueryResponse)
def chat(query: QueryInput):
    session_id = query.session_id or str(uuid.uuid4())
    logging.info(f"Session {session_id} | Question: {query.question}")

    chain = get_rag_chain()
    chat_history = get_chat_history(session_id)

    result = chain.invoke({
        "input": query.question,
        "chat_history": chat_history
    })

    answer = result["answer"]
    insert_application_logs(session_id, query.question, answer, query.model)

    return QueryResponse(answer=answer, session_id=session_id)

@app.post("/upload-doc")
async def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.docx', '.html')):
        raise HTTPException(400, "Only .pdf, .docx, .html allowed")

    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        file_id = insert_document_record(file.filename)
        success = index_document_to_chroma(temp_path, file_id)
        if not success:
            delete_document_record(file_id)
            raise HTTPException(500, "Failed to index")
        return {"message": "Uploaded", "file_id": file_id}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/list-docs")
def list_docs():
    return get_all_documents()

@app.post("/delete-doc")
def delete_doc(request: dict):
    file_id = request.get("file_id")
    if not delete_doc_from_chroma(file_id):
        return {"error": "Chroma delete failed"}
    delete_document_record(file_id)
    return {"message": "Deleted"}