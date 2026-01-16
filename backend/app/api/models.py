from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    session_id: str
    message: str
    role: str  # "patient" or "doctor"

class ChatResponse(BaseModel):
    response: str
    session_id: str

class QuestionRequest(BaseModel):
    session_id: str

class QuestionResponse(BaseModel):
    questions: str

class UploadResponse(BaseModel):
    success: bool
    pdf_name: str
    message: str

class MessageHistory(BaseModel):
    role: str
    content: str
    user_role: str
    timestamp: str

class HistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageHistory]
