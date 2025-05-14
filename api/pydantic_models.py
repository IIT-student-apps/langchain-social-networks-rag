from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

from typing import Optional

class ModelName(str, Enum):
    YANDEX = "denisavetisyan/saiga_yandexgpt_8b_gguf_q5_k_m:latest"
    # GPT4_O = "gpt-4o"
    # GPT4_O_MINI = "gpt-4o-mini"
    #LLAMA32= "llama3.2"

class QueryInput(BaseModel):
    question: str
    session_id: str = Field(default=None)
    model: ModelName = Field(default=ModelName.YANDEX)

class QueryResponse(BaseModel):
    answer: str
    session_id: str
    model: ModelName

class DocumentInfo(BaseModel):
    id: int
    filename: str
    upload_timestamp: datetime

class DeleteFileRequest(BaseModel):
    file_id: int
    

class UserInfo(BaseModel):
    first_name: str
    last_name: str
    user_id: int

class UserToken(BaseModel):
    status: str
    token: Optional[str] = None
    message: Optional[str] = None