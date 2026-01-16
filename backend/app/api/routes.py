from fastapi import APIRouter, UploadFile, File, HTTPException
from app.api.models import ChatRequest, ChatResponse, QuestionRequest, QuestionResponse, UploadResponse, HistoryResponse, MessageHistory
from app.services.chat_service import ChatService
from app.db.database import get_db
from datetime import datetime

router = APIRouter()
chat_service = ChatService()

@router.post("/upload-pdf", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...), session_id: str = None):
    try:
        result = await chat_service.process_pdf(file, session_id)
        return UploadResponse(
            success=True,
            pdf_name=result["pdf_name"],
            message="PDF indexed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await chat_service.generate_response(
            session_id=request.session_id,
            message=request.message,
            role=request.role
        )
        
        # Save to database
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Ensure session exists
            cursor.execute(
                "INSERT OR IGNORE INTO chat_sessions (session_id) VALUES (?)",
                (request.session_id,)
            )
            
            # Save user message
            cursor.execute(
                "INSERT INTO chat_messages (session_id, role, content, user_role) VALUES (?, ?, ?, ?)",
                (request.session_id, "user", request.message, request.role)
            )
            
            # Save assistant response
            cursor.execute(
                "INSERT INTO chat_messages (session_id, role, content, user_role) VALUES (?, ?, ?, ?)",
                (request.session_id, "assistant", response, request.role)
            )
            
            conn.commit()
        
        return ChatResponse(response=response, session_id=request.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-questions", response_model=QuestionResponse)
async def generate_questions(request: QuestionRequest):
    try:
        questions = await chat_service.generate_doctor_questions(request.session_id)
        return QuestionResponse(questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, user_role, timestamp FROM chat_messages WHERE session_id = ? ORDER BY timestamp",
                (session_id,)
            )
            rows = cursor.fetchall()
            
            messages = [
                MessageHistory(
                    role=row["role"],
                    content=row["content"],
                    user_role=row["user_role"],
                    timestamp=row["timestamp"]
                )
                for row in rows
            ]
            
            return HistoryResponse(session_id=session_id, messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
