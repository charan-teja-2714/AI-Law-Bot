# MediSense Architecture Documentation

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                                 │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │              React Frontend (Port 3000)                     │    │
│  │                                                             │    │
│  │  Components:                                                │    │
│  │  ├─ ChatInterface.jsx      (Main container)                │    │
│  │  ├─ MessageList.jsx        (Display messages)              │    │
│  │  ├─ MessageInput.jsx       (User input)                    │    │
│  │  ├─ PDFUpload.jsx          (File upload)                   │    │
│  │  ├─ RoleToggle.jsx         (Patient/Doctor switch)         │    │
│  │  └─ QuestionsDialog.jsx    (Modal for questions)           │    │
│  │                                                             │    │
│  │  Services:                                                  │    │
│  │  └─ api.js                 (HTTP client)                   │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                          HTTP REST API
                          (JSON over HTTP)
                                  │
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                       │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                    API Layer                                │    │
│  │  routes.py:                                                 │    │
│  │  ├─ POST /api/upload-pdf                                    │    │
│  │  ├─ POST /api/chat                                          │    │
│  │  ├─ POST /api/generate-questions                            │    │
│  │  └─ GET  /api/history/{session_id}                          │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                  │                                   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                  Service Layer                              │    │
│  │  chat_service.py:                                           │    │
│  │  ├─ Session management                                      │    │
│  │  ├─ PDF processing orchestration                            │    │
│  │  └─ Response generation                                     │    │
│  │                                                             │    │
│  │  pdf.py (REUSED - UNCHANGED):                               │    │
│  │  ├─ process_pdf()          (Extract text + OCR)            │    │
│  │  ├─ chunk_text()           (Medical-aware chunking)         │    │
│  │  ├─ create_pinecone_index() (Vector indexing)              │    │
│  │  ├─ retrieve_with_rerank() (Hybrid retrieval)              │    │
│  │  └─ generate_pdf_response() (RAG generation)               │    │
│  │                                                             │    │
│  │  question_recommender.py (REUSED - UNCHANGED):              │    │
│  │  └─ generate_doctor_questions() (Safe questions)           │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                  │                                   │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                  Database Layer                             │    │
│  │  database.py:                                               │    │
│  │  ├─ SQLite connection management                            │    │
│  │  ├─ Chat history persistence                                │    │
│  │  └─ Session tracking                                        │    │
│  └────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                    │                │                │
        ┌───────────┴────────┬───────┴────────┬──────┴──────────┐
        │                    │                │                  │
┌───────▼────────┐  ┌────────▼────────┐  ┌───▼──────────┐  ┌──▼────────┐
│   SQLite DB    │  │   Pinecone      │  │  Groq LLM    │  │ Tesseract │
│                │  │   Vector DB     │  │  (llama-3.3) │  │    OCR    │
│ • Sessions     │  │                 │  │              │  │           │
│ • Messages     │  │ • Dense vectors │  │ • Generation │  │ • Scanned │
│ • Timestamps   │  │ • BM25 sparse   │  │ • Safety     │  │   PDFs    │
│                │  │ • Metadata      │  │   rules      │  │           │
└────────────────┘  └─────────────────┘  └──────────────┘  └───────────┘
```

## Data Flow

### 1. PDF Upload Flow
```
User uploads PDF
    ↓
React: PDFUpload.jsx
    ↓
API: POST /api/upload-pdf
    ↓
Backend: chat_service.process_pdf()
    ↓
Service: pdf.process_pdf() [REUSED]
    ├─ Extract text (PyPDF2)
    └─ OCR fallback (Tesseract)
    ↓
Service: pdf.chunk_text() [REUSED]
    └─ Medical-aware chunking
    ↓
Service: pdf.create_pinecone_index() [REUSED]
    ├─ Generate embeddings (sentence-transformers)
    ├─ Generate BM25 sparse vectors
    └─ Upsert to Pinecone
    ↓
Store session state in memory
    ↓
Return success to frontend
```

### 2. Chat Flow
```
User sends message
    ↓
React: MessageInput.jsx
    ↓
API: POST /api/chat
    ↓
Backend: chat_service.generate_response()
    ↓
Service: pdf.generate_pdf_response() [REUSED]
    ├─ Rewrite query (LLM)
    ├─ Retrieve with rerank (Pinecone + BM25)
    ├─ Generate response (Groq LLM)
    └─ Apply safety rules
    ↓
Save to SQLite:
    ├─ User message
    └─ Assistant response
    ↓
Return response to frontend
    ↓
React: Display in MessageList.jsx
```

### 3. Question Generation Flow
```
User clicks "Generate questions"
    ↓
React: ChatInterface.jsx
    ↓
API: POST /api/generate-questions
    ↓
Backend: chat_service.generate_doctor_questions()
    ├─ Query Pinecone for context
    └─ Call question_recommender.generate_doctor_questions() [REUSED]
    ↓
Return questions
    ↓
React: Display in QuestionsDialog.jsx (modal)
```

## Component Responsibilities

### Frontend (React)
- **UI Rendering**: Display chat, forms, buttons
- **User Input**: Capture messages, file uploads
- **State Management**: Local UI state (messages, loading)
- **API Communication**: HTTP requests to backend

### Backend (FastAPI)
- **API Endpoints**: RESTful interface
- **Session Management**: Track user sessions
- **Business Logic**: Orchestrate AI services
- **Data Persistence**: Save chat history

### Services (Reused Logic)
- **PDF Processing**: Text extraction, OCR
- **Chunking**: Medical-aware text splitting
- **Vector Operations**: Embeddings, indexing
- **Retrieval**: Hybrid search (dense + sparse)
- **Generation**: LLM-based responses
- **Safety**: No diagnosis, no treatment

### External Services
- **Pinecone**: Vector storage and search
- **Groq**: LLM inference
- **Tesseract**: OCR for scanned PDFs

## Security Considerations

1. **No Sensitive Data Storage**: PDFs not stored permanently
2. **Session Isolation**: Each session has separate state
3. **API Validation**: Pydantic models validate all inputs
4. **CORS**: Restricted to localhost:3000
5. **Safety Rules**: Enforced in prompts (no diagnosis/treatment)

## Scalability Path

### Current (Single Server)
- Frontend: localhost:3000
- Backend: localhost:8000
- Database: SQLite file

### Production (Scalable)
- Frontend: CDN (Vercel, Netlify)
- Backend: Multiple instances (Docker + Load Balancer)
- Database: PostgreSQL (replace SQLite)
- Cache: Redis (session state)
- Queue: Celery (async PDF processing)

## Key Design Decisions

1. **Why SQLite?**
   - Lightweight for chat history
   - No setup required
   - Easy migration to PostgreSQL later

2. **Why in-memory sessions?**
   - Fast access to Pinecone index
   - Stateful backend simplifies logic
   - Can move to Redis for multi-instance

3. **Why copy existing code?**
   - Zero risk of breaking AI logic
   - Proven, tested functionality
   - Easy to maintain

4. **Why FastAPI?**
   - Modern Python async framework
   - Auto-generated API docs
   - Type safety with Pydantic
   - Easy integration with existing code
