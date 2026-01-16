# MediSense Migration Guide: Streamlit → React + FastAPI

## Architecture Overview

```
Frontend (React) ←→ Backend (FastAPI) ←→ [Pinecone, Groq LLM]
                          ↓
                     SQLite (Chat History)
```

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Copy existing service files
cp ../utils/pdf.py app/services/
cp ../utils/question_recommender.py app/services/

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run React app
npm start
```

The app will open at http://localhost:3000

## How Existing Logic is Reused

### PDF Processing (UNCHANGED)
- `app/services/pdf.py` - Copied from `utils/pdf.py`
- Functions reused:
  - `process_pdf()` - PDF text extraction + OCR
  - `chunk_text()` - Medical-aware chunking
  - `create_pinecone_index()` - Vector indexing
  - `generate_pdf_response()` - RAG answer generation

### Question Generation (UNCHANGED)
- `app/services/question_recommender.py` - Copied from `utils/question_recommender.py`
- Function reused:
  - `generate_doctor_questions()` - Safe question generation

### Chat Service (NEW - Wrapper Only)
- `app/services/chat_service.py` - Thin wrapper that:
  - Manages session state (replaces Streamlit session_state)
  - Calls existing functions without modification
  - Handles file upload conversion

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/upload-pdf` | POST | Upload and index PDF |
| `/api/chat` | POST | Send message, get AI response |
| `/api/generate-questions` | POST | Generate doctor questions |
| `/api/history/{session_id}` | GET | Retrieve chat history |

## Database Schema

**chat_sessions**
- session_id (unique identifier)
- created_at, last_activity (timestamps)

**chat_messages**
- session_id (foreign key)
- role (user/assistant)
- content (message text)
- user_role (patient/doctor mode)
- pdf_name (optional tracking)
- timestamp

## Safety Preservation

All safety rules from original system are preserved:
- ✅ No diagnosis
- ✅ No treatment suggestions
- ✅ Patient-friendly language
- ✅ Role-based explanations
- ✅ Questions only (no answers)

## Testing the Migration

1. Start backend: `uvicorn app.main:app --reload`
2. Start frontend: `npm start`
3. Upload a PDF
4. Ask questions
5. Generate doctor questions
6. Verify responses match Streamlit version

## Key Differences

| Aspect | Streamlit | React + FastAPI |
|--------|-----------|-----------------|
| UI | Python-based | JavaScript-based |
| State | st.session_state | React useState + Backend sessions |
| History | JSON files | SQLite database |
| Deployment | Single app | Separate frontend/backend |
| Scalability | Limited | Horizontal scaling possible |

## Migration Benefits

1. **Separation of Concerns**: UI and logic are decoupled
2. **Better UX**: Modern React UI with smooth interactions
3. **API-First**: Backend can serve multiple clients
4. **Database**: Proper persistence with SQLite
5. **Scalability**: Can deploy frontend and backend separately

## Important Notes

- All AI logic remains EXACTLY the same
- Pinecone, embeddings, chunking, retrieval - UNCHANGED
- Only UI layer replaced
- Backend is a thin API wrapper around existing code
