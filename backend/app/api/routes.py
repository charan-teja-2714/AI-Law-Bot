from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from app.api.models import (
    ChatRequest, ChatResponse, QuestionRequest, QuestionResponse,
    UploadResponse, HistoryResponse, MessageHistory,
    LegalAnalysisResponse, AudioVideoUploadResponse,
    TranslateRequest, TranslateResponse
)
from app.services.chat_service import chat_service
from app.services.translation_service import translation_service
from app.db.database import get_db
from datetime import datetime

router = APIRouter()


@router.post("/upload-document", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...), session_id: str = None, session_token: str = None):
    """
    Upload legal document (PDF)
    """
    try:
        from app.auth.auth_service import auth_service
        import uuid
        from datetime import datetime
        
        # Verify session
        session = auth_service.get_session(session_token)
        if not session:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Verify session belongs to user
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM chat_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if not row or row["user_id"] != session["user_id"]:
                raise HTTPException(status_code=403, detail="Access denied")
        
        document_id = str(uuid.uuid4())
        result = await chat_service.process_document(file, session_id, document_id)
        
        # Save to database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO session_documents (session_id, document_id, document_name, document_type, uploaded_at) VALUES (?, ?, ?, ?, ?)",
                (session_id, document_id, file.filename, "pdf", datetime.now().isoformat())
            )
            conn.commit()
        
        return UploadResponse(
            success=True,
            pdf_name=result["doc_name"],
            message=f"Document indexed successfully ({result['chunks_created']} chunks)"
        )
    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"ERROR in upload_document: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-audio-video", response_model=AudioVideoUploadResponse)
async def upload_audio_video(file: UploadFile = File(...), session_id: str = None):
    """
    Upload audio or video file for transcription
    """
    try:
        import uuid
        from datetime import datetime
        document_id = str(uuid.uuid4())
        
        result = await chat_service.process_audio_video(file, session_id, document_id)
        
        # Save to database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO session_documents (session_id, document_id, document_name, document_type, uploaded_at) VALUES (?, ?, ?, ?, ?)",
                (session_id, document_id, file.filename, result["file_type"], datetime.now().isoformat())
            )
            conn.commit()
        
        return AudioVideoUploadResponse(
            success=True,
            filename=result["doc_name"],
            transcription=result["transcription"],
            language=result["language"],
            file_type=result["file_type"],
            message="Audio/Video transcribed and indexed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe-audio")
async def transcribe_audio(file: UploadFile = File(...), language: str = None):
    """
    Transcribe audio to text (for voice input)
    language: optional ISO-639-1 code (en, hi, te, ta, etc.) — None = auto-detect
    """
    try:
        from app.services.speech_to_text import speech_to_text_service
        print(f"[TRANSCRIBE] Processing file: {file.filename}, language hint: {language}")
        result = await speech_to_text_service.process_file(file, language=language)
        print(f"[TRANSCRIBE] Result: {result}")
        response = {
            "text": result.get("text", ""),
            "language": result.get("language", "en")
        }
        print(f"[TRANSCRIBE] Returning: {response}")
        return response
    except Exception as e:
        print(f"[TRANSCRIBE] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with AI Law Bot
    Supports multilingual queries and structured output
    """
    try:
        from app.auth.auth_service import auth_service
        
        # Verify session
        session = auth_service.get_session(request.session_token)
        if not session:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Verify session belongs to user and fetch recent chat history
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM chat_sessions WHERE session_id = ?", (request.session_id,))
            row = cursor.fetchone()
            if not row or row["user_id"] != session["user_id"]:
                raise HTTPException(status_code=403, detail="Access denied")

            # Fetch last 6 messages (3 exchanges) for conversation history
            cursor.execute(
                "SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT 6",
                (request.session_id,)
            )
            history_rows = cursor.fetchall()
            chat_history = [{"role": r["role"], "content": r["content"]} for r in reversed(history_rows)]

        response_data = await chat_service.generate_response(
            session_id=request.session_id,
            message=request.message,
            user_language=request.language or "en",
            structured_output=request.structured_output or False,
            chat_history=chat_history
        )

        # Save to database
        with get_db() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().isoformat()
            
            # Update last activity
            cursor.execute(
                "UPDATE chat_sessions SET last_activity = ? WHERE session_id = ?",
                (current_time, request.session_id)
            )

            # Save user message
            cursor.execute(
                "INSERT INTO chat_messages (session_id, role, content, user_role, timestamp) VALUES (?, ?, ?, ?, ?)",
                (request.session_id, "user", request.message, request.language or "en", current_time)
            )

            # Save assistant response
            response_content = response_data.get("response", "")
            if response_data.get("type") == "structured":
                response_content = str(response_data.get("analysis"))

            cursor.execute(
                "INSERT INTO chat_messages (session_id, role, content, user_role, timestamp) VALUES (?, ?, ?, ?, ?)",
                (request.session_id, "assistant", response_content, request.language or "en", current_time)
            )

            conn.commit()

        # Return appropriate response
        if response_data.get("type") == "structured":
            return ChatResponse(
                response="",
                session_id=request.session_id,
                structured_analysis=response_data.get("analysis"),
                language=response_data.get("language")
            )
        else:
            return ChatResponse(
                response=response_data.get("response", ""),
                session_id=request.session_id,
                language=response_data.get("language"),
                similar_cases=response_data.get("similar_cases")
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-document")
async def analyze_document(session_id: str, request: dict = Body(default=None)):
    """
    Perform structured legal analysis on uploaded document(s)
    Returns IPC, CrPC, BNS sections and legal predictions
    """
    try:
        document_ids = None
        if request and 'document_ids' in request:
            document_ids = request['document_ids']

        print(f"[ANALYZE] Session: {session_id}, Document IDs: {document_ids}")
        analysis = await chat_service.analyze_document(session_id, document_ids)

        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])

        return {
            "session_id": session_id,
            "analysis": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[ANALYZE] Error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{session_id}")
async def get_session_documents(session_id: str, search: str = None):
    """
    Get all documents for a session with optional name filter
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            if search:
                cursor.execute(
                    "SELECT document_id, document_name, document_type, uploaded_at FROM session_documents WHERE session_id = ? AND document_name LIKE ? ORDER BY uploaded_at DESC",
                    (session_id, f"%{search}%")
                )
            else:
                cursor.execute(
                    "SELECT document_id, document_name, document_type, uploaded_at FROM session_documents WHERE session_id = ? ORDER BY uploaded_at DESC",
                    (session_id,)
                )
            
            rows = cursor.fetchall()
            documents = [
                {
                    "document_id": row["document_id"],
                    "document_name": row["document_name"],
                    "document_type": row["document_type"],
                    "uploaded_at": row["uploaded_at"]
                }
                for row in rows
            ]
            
            return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract-entities")
async def extract_entities(session_id: str, request: dict = Body(default=None)):
    """
    Extract legal entities from documents with advanced processing
    """
    try:
        from app.services.faiss_store import faiss_store
        from app.services.chat_service import chat_service
        
        document_ids = None
        if request and 'document_ids' in request:
            document_ids = request['document_ids']
        
        print(f"[EXTRACT] Session: {session_id}, Docs: {document_ids}")
        
        # Determine processing mode
        processing_mode = "single_document" if document_ids and len(document_ids) == 1 else "multi_document"
        
        # Get document content
        results = faiss_store.query(
            session_id=session_id,
            query_text="FIR sections IPC CrPC BNS charges offense crime complainant accused witness",
            top_k=30,
            document_ids=document_ids
        )
        
        print(f"[EXTRACT] Retrieved {len(results) if results else 0} chunks")
        
        if not results:
            return {"entities": {"people": {}, "legal_sections": {}}}
        
        context = "\n\n".join([r["text"] for r in results])
        print(f"[EXTRACT] Context length: {len(context)}")
        
        # Use LLM with advanced prompt
        from langchain_core.prompts import PromptTemplate
        prompt = PromptTemplate(
            template="""You are a Legal Document Analysis Expert. Extract entities with MAXIMUM ACCURACY.

=== DOCUMENT CONTENT ===
{context}

=== EXTRACTION RULES ===

1. PEOPLE EXTRACTION:
   - Find FULL NAMES (not just "Accused", "PW-1")
   - If you see "Accused No.3 Shiva Murthy" → extract "Shiva Murthy"
   - If you see "PW-1 Ramesh Kumar" → extract "Ramesh Kumar"
   - Include designations: "Inspector Kavita Sharma" → extract "Inspector Kavita Sharma"
   - Look for: Complainant, Accused, Witness, Lawyer (Adv./Advocate), Police Officer, Judge

2. LEGAL SECTIONS EXTRACTION:
   - Extract COMPLETE section references
   - Format: "Section [NUMBER] [ACT]"
   - Examples: "Section 420 IPC", "Section 318 BNS", "Section 164(1) CrPC"
   - IMPORTANT: If IPC section found, also mention BNS equivalent
     * IPC 302 → also extract "Section 103 BNS"
     * IPC 420 → also extract "Section 318 BNS"
   - Common acts: IPC, CrPC, BNS, Prevention of Corruption Act, IT Act

3. ACCURACY RULES:
   - Extract ONLY what is EXPLICITLY written
   - Do NOT invent names or sections
   - If uncertain, skip it
   - Prefer full names over labels

=== OUTPUT FORMAT (STRICT JSON) ===

{{
  "people": {{
    "complainants": ["Full Name 1", "Full Name 2"],
    "accused": ["Full Name 1", "Full Name 2"],
    "witnesses": ["Full Name or ID like PW-1"],
    "lawyers": ["Adv. Full Name"],
    "officers": ["Designation Full Name"]
  }},
  "legal_sections": {{
    "ipc": ["Section 420 IPC", "Section 302 IPC"],
    "crpc": ["Section 164(1) CrPC"],
    "bns": ["Section XXX BNS"],
    "other": ["Section 5(2) Prevention of Corruption Act"]
  }}
}}

=== IMPORTANT ===
- Return ONLY valid JSON
- Use empty arrays [] if nothing found
- Extract from the ENTIRE document provided
- Be thorough and accurate

JSON:""",
            input_variables=["context"]
        )
        
        response = (prompt | chat_service.llm).invoke({"context": context})
        print(f"[EXTRACT] Full LLM response: {response.content}")
        
        import json
        import re
        try:
            content = response.content.strip()
            if content.startswith('```'):
                content = re.sub(r'^```(?:json)?\s*', '', content)
                content = re.sub(r'\s*```$', '', content)
            
            entities = json.loads(content.strip())
            
            # Simplify structure for frontend
            simplified = {
                "people": {
                    "complainants": [p.get("name", p) if isinstance(p, dict) else p for p in entities.get("people", {}).get("complainants", [])],
                    "accused": [p.get("name", p) if isinstance(p, dict) else p for p in entities.get("people", {}).get("accused", [])],
                    "witnesses": [p.get("name", p) if isinstance(p, dict) else p for p in entities.get("people", {}).get("witnesses", [])],
                    "lawyers": [p.get("name", p) if isinstance(p, dict) else p for p in entities.get("people", {}).get("lawyers", [])],
                    "officers": [p.get("name", p) if isinstance(p, dict) else p for p in entities.get("people", {}).get("officers", [])]
                },
                "legal_sections": entities.get("legal_sections", {})
            }
            
            print(f"[EXTRACT] Parsed entities: {simplified}")
            return {"entities": simplified}
        except Exception as e:
            print(f"[EXTRACT] JSON parse error: {e}")
            return {
                "entities": {
                    "people": {"complainants": [], "accused": [], "witnesses": [], "lawyers": [], "officers": []},
                    "legal_sections": {"ipc": [], "crpc": [], "bns": [], "other": []}
                }
            }
    except Exception as e:
        print(f"[EXTRACT] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{session_id}/{document_id}")
async def delete_document(session_id: str, document_id: str):
    """
    Delete a specific document from session
    """
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM session_documents WHERE session_id = ? AND document_id = ?",
                (session_id, document_id)
            )
            conn.commit()
        
        # Delete FAISS index
        from app.services.faiss_store import faiss_store
        try:
            faiss_store.delete_index(session_id, document_id)
        except:
            pass
        
        return {"deleted": True, "document_id": document_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str, session_token: str):
    """
    Get chat history for a session
    """
    try:
        from app.auth.auth_service import auth_service
        
        # Verify session
        session = auth_service.get_session(session_token)
        if not session:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Verify session belongs to user
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM chat_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if not row or row["user_id"] != session["user_id"]:
                raise HTTPException(status_code=403, detail="Access denied")
            
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


@router.get("/sessions")
async def get_all_sessions(session_token: str):
    """
    Get all chat sessions for logged-in user
    """
    try:
        from app.auth.auth_service import auth_service
        
        # Verify session
        session = auth_service.get_session(session_token)
        if not session:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    cs.session_id,
                    cs.created_at,
                    cs.last_activity,
                    COUNT(cm.id) as message_count
                FROM chat_sessions cs
                LEFT JOIN chat_messages cm ON cs.session_id = cm.session_id
                WHERE cs.user_id = ?
                GROUP BY cs.session_id
                ORDER BY cs.last_activity DESC
            """, (session["user_id"],))
            rows = cursor.fetchall()

            sessions = []
            for row in rows:
                # Get first message as preview
                cursor.execute(
                    "SELECT content FROM chat_messages WHERE session_id = ? AND role = 'user' ORDER BY timestamp LIMIT 1",
                    (row["session_id"],)
                )
                first_msg = cursor.fetchone()
                preview = first_msg["content"][:100] if first_msg else "New conversation"

                sessions.append({
                    "session_id": row["session_id"],
                    "created_at": row["created_at"],
                    "last_activity": row["last_activity"],
                    "message_count": row["message_count"] or 0,
                    "preview": preview
                })

            return {"sessions": sessions}
    except Exception as e:
        import traceback
        print(f"Error in get_all_sessions: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/new")
async def create_new_session(request: dict = Body(...)):
    """
    Create a new chat session for logged-in user
    """
    try:
        from app.auth.auth_service import auth_service
        import uuid
        from datetime import datetime
        
        session_token = request.get('session_token')
        if not session_token:
            raise HTTPException(status_code=400, detail="session_token required")
        
        # Verify session
        session = auth_service.get_session(session_token)
        if not session:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        session_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_sessions (session_id, user_id, created_at, last_activity) VALUES (?, ?, ?, ?)",
                (session_id, session["user_id"], current_time, current_time)
            )
            conn.commit()

        return {"session_id": session_id, "created": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, session_token: str):
    """
    Delete a chat session and all its messages
    """
    try:
        from app.auth.auth_service import auth_service
        
        # Verify session
        session = auth_service.get_session(session_token)
        if not session:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Verify session belongs to user
            cursor.execute("SELECT user_id FROM chat_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if not row or row["user_id"] != session["user_id"]:
                raise HTTPException(status_code=403, detail="Access denied")

            # Delete messages
            cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))

            # Delete session
            cursor.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))

            conn.commit()

        # Also delete FAISS index if exists
        from app.services.faiss_store import faiss_store
        try:
            faiss_store.delete_index(session_id)
        except:
            pass

        return {"deleted": True, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """
    Translate text to target language
    """
    try:
        if request.target_language == "en":
            # If target is English, detect source language and translate
            translation_result = translation_service.process_user_input(request.text)
            translated_text = translation_result["english_text"]
        else:
            # Translate from English to target language
            translated_text = translation_service.translate_from_english(
                request.text,
                request.target_language
            )

        return TranslateResponse(
            translated_text=translated_text,
            target_language=request.target_language
        )
    except Exception as e:
        import traceback
        print(f"[TRANSLATE] Error: {str(e)}")
        print(f"[TRANSLATE] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Law Bot API",
        "version": "2.0.0"
    }


@router.get("/debug/check-dependencies")
async def check_dependencies():
    """Check if all dependencies are working"""
    results = {}

    # Check Tesseract
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        results["tesseract"] = {"status": "OK", "version": str(version)}
    except Exception as e:
        results["tesseract"] = {"status": "ERROR", "error": str(e)}

    # Check PDF processing
    try:
        from PyPDF2 import PdfReader
        results["pypdf2"] = {"status": "OK"}
    except Exception as e:
        results["pypdf2"] = {"status": "ERROR", "error": str(e)}

    # Check FAISS
    try:
        import faiss
        results["faiss"] = {"status": "OK"}
    except Exception as e:
        results["faiss"] = {"status": "ERROR", "error": str(e)}

    # Check LangChain
    try:
        from langchain_groq import ChatGroq
        results["langchain"] = {"status": "OK"}
    except Exception as e:
        results["langchain"] = {"status": "ERROR", "error": str(e)}

    return results


# Authentication endpoints
@router.post("/register")
async def register(username: str = Body(...), email: str = Body(...), password: str = Body(...)):
    """Register new user"""
    try:
        from app.auth.auth_service import auth_service
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check if username exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Username already exists")
            
            # Check if email exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email already exists")
            
            # Hash password and create user
            password_hash = auth_service.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            
            # Get user_id
            user_id = cursor.lastrowid
            
            # Create session
            session_token = auth_service.create_session(user_id, username)
            
            return {
                "success": True,
                "session_token": session_token,
                "username": username
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(login_id: str = Body(...), password: str = Body(...)):
    """Login user with username or email"""
    try:
        from app.auth.auth_service import auth_service
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get user by username or email
            cursor.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ? OR email = ?",
                (login_id, login_id)
            )
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Verify password
            if not auth_service.verify_password(password, user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Create session
            session_token = auth_service.create_session(user["id"], user["username"])
            
            return {
                "success": True,
                "session_token": session_token,
                "username": user["username"]
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(session_token: str = Body(...)):
    """Logout user"""
    try:
        from app.auth.auth_service import auth_service
        auth_service.delete_session(session_token)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify-session")
async def verify_session(session_token: str):
    """Verify if session is valid"""
    try:
        from app.auth.auth_service import auth_service
        session = auth_service.get_session(session_token)
        
        if not session:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        return {
            "valid": True,
            "username": session["username"],
            "user_id": session["user_id"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
