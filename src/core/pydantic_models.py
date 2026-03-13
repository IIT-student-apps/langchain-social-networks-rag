from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.core.config import ACTIVE_MODEL, LLM_CONFIGS

class ModelName(str, Enum):
    GROQ_QWEN = "groq_qwen"
    GROQ_MOONSHOT = "groq_moonshotai"
    LOCAL_QWEN = "local_qwen3:8b"

class QueryInput(BaseModel):
    question: str
    session_id: str = Field(default=None)
    model: ModelName = Field(default=ModelName(ACTIVE_MODEL))

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
