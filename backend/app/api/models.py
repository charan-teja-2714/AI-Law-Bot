from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: Optional[str] = "en"  # en, hi, te, ta
    structured_output: Optional[bool] = False
    session_token: str


class ChatResponse(BaseModel):
    response: str
    session_id: str
    language: Optional[str] = "en"
    structured_analysis: Optional[Dict[str, Any]] = None
    similar_cases: Optional[str] = None


class QuestionRequest(BaseModel):
    session_id: str


class QuestionResponse(BaseModel):
    questions: str


class UploadResponse(BaseModel):
    success: bool
    pdf_name: str
    message: str


class AudioVideoUploadResponse(BaseModel):
    success: bool
    filename: str
    transcription: str
    language: str
    file_type: str  # "audio" or "video"
    message: str


class LegalAnalysisResponse(BaseModel):
    session_id: str
    analysis: Dict[str, Any]


class MessageHistory(BaseModel):
    role: str
    content: str
    user_role: str
    timestamp: str


class HistoryResponse(BaseModel):
    session_id: str
    messages: List[MessageHistory]


class TranslateRequest(BaseModel):
    text: str
    target_language: str  # en, hi, te, ta


class TranslateResponse(BaseModel):
    translated_text: str
    target_language: str
