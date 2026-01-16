# Streamlit vs React+FastAPI Comparison

## Side-by-Side Feature Comparison

| Feature | Streamlit (Old) | React + FastAPI (New) |
|---------|----------------|----------------------|
| **UI Framework** | Streamlit (Python) | React (JavaScript) |
| **Backend** | Embedded in Streamlit | FastAPI (separate) |
| **State Management** | st.session_state | React state + Backend sessions |
| **Chat History** | JSON files | SQLite database |
| **API** | None | RESTful HTTP API |
| **Deployment** | Single Python app | Frontend + Backend separate |
| **Scalability** | Single instance | Horizontal scaling |
| **Mobile Support** | Limited | Full responsive |
| **Real-time Updates** | Page rerun | React state updates |
| **Session Persistence** | File-based | Database-based |

## Code Comparison

### PDF Upload

**Streamlit:**
```python
uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_pdf and st.session_state.pinecone_index is None:
    with st.spinner("Indexing medical report..."):
        load_collection(uploaded_pdf)
```

**React + FastAPI:**
```javascript
// Frontend (React)
const handlePDFUpload = async (file) => {
  setLoading(true);
  await api.uploadPDF(file, sessionId);
  setPdfUploaded(true);
  setLoading(false);
};

// Backend (FastAPI)
@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile, session_id: str):
    result = await chat_service.process_pdf(file, session_id)
    return {"success": True, "pdf_name": result["pdf_name"]}
```

### Chat Message

**Streamlit:**
```python
user_input = st.chat_input("Ask something...")

if user_input:
    chat_history.add_user_message(user_input)
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.chat_message("assistant"):
        answer = generate_pdf_response(user_input, role=st.session_state.role)
        st.markdown(answer)
    
    chat_history.add_ai_message(answer)
```

**React + FastAPI:**
```javascript
// Frontend (React)
const handleSendMessage = async (message) => {
  setMessages(prev => [...prev, { role: 'user', content: message }]);
  
  const response = await api.sendMessage(sessionId, message, role);
  setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
};

// Backend (FastAPI)
@router.post("/chat")
async def chat(request: ChatRequest):
    response = await chat_service.generate_response(
        request.session_id, request.message, request.role
    )
    # Save to database
    save_to_db(request.session_id, request.message, response)
    return {"response": response}
```

### Doctor Questions

**Streamlit:**
```python
if st.button("📝 Generate questions"):
    with st.spinner("Preparing questions..."):
        questions = generate_doctor_questions(context, llm)
    
    st.markdown("### 🩺 Questions to ask your doctor")
    st.markdown(questions)
```

**React + FastAPI:**
```javascript
// Frontend (React)
const handleGenerateQuestions = async () => {
  const response = await api.generateQuestions(sessionId);
  setQuestions(response.questions);  // Opens modal
};

// Backend (FastAPI)
@router.post("/generate-questions")
async def generate_questions(request: QuestionRequest):
    questions = await chat_service.generate_doctor_questions(request.session_id)
    return {"questions": questions}
```

## What Changed

### ✅ Changed (UI Only)
- Streamlit components → React components
- st.session_state → React useState + Backend sessions
- st.chat_message → Custom MessageList component
- st.file_uploader → Custom PDFUpload component
- st.button → HTML button with onClick
- st.spinner → Loading state in React
- JSON file storage → SQLite database

### ❌ NOT Changed (AI Logic Preserved)
- PDF processing (PyPDF2, Tesseract)
- OCR pipeline
- Medical-aware chunking
- Sentence-transformers embeddings
- Pinecone vector operations
- BM25 sparse encoding
- Hybrid retrieval (dense + sparse)
- Query rewriting
- Groq LLM calls
- Safety prompts (no diagnosis/treatment)
- Question generation logic

## Migration Effort

### Low Effort (Copy-Paste)
- `utils/pdf.py` → `backend/app/services/pdf.py`
- `utils/question_recommender.py` → `backend/app/services/question_recommender.py`

### Medium Effort (New Code)
- FastAPI routes (200 lines)
- SQLite database setup (50 lines)
- Chat service wrapper (100 lines)

### Medium Effort (React UI)
- 6 React components (400 lines total)
- API client (50 lines)
- Basic styling (50 lines)

**Total New Code: ~850 lines**
**Reused Code: ~500 lines (100% preserved)**

## Benefits of Migration

### 1. Better User Experience
- **Streamlit**: Page reloads on every interaction
- **React**: Smooth, instant UI updates

### 2. API-First Architecture
- **Streamlit**: No API, monolithic
- **React+FastAPI**: RESTful API, can serve mobile apps, integrations

### 3. Scalability
- **Streamlit**: Single instance, limited concurrency
- **React+FastAPI**: Frontend on CDN, backend scales horizontally

### 4. Development Workflow
- **Streamlit**: Frontend and backend tightly coupled
- **React+FastAPI**: Independent development, testing, deployment

### 5. Database
- **Streamlit**: JSON files, no queries
- **React+FastAPI**: SQLite with indexes, easy to query

### 6. Deployment
- **Streamlit**: Single server, single port
- **React+FastAPI**: Frontend (CDN) + Backend (containers)

## Drawbacks (Trade-offs)

| Aspect | Streamlit | React+FastAPI |
|--------|-----------|---------------|
| **Setup Complexity** | Simple (1 file) | More complex (2 apps) |
| **Learning Curve** | Python only | Python + JavaScript |
| **Deployment** | Single command | Two deployments |
| **Development Speed** | Very fast prototyping | Slower initial setup |
| **Dependencies** | Fewer | More (Node.js + Python) |

## When to Use Each

### Use Streamlit When:
- Rapid prototyping
- Internal tools
- Data science demos
- Python-only team
- Simple UI requirements

### Use React+FastAPI When:
- Production application
- Public-facing product
- Need mobile app later
- Multiple clients (web, mobile, API)
- Team has frontend developers
- Need scalability
- Want modern UX

## Conclusion

The migration preserves **100% of AI functionality** while providing:
- Modern, responsive UI
- RESTful API for extensibility
- Better scalability
- Proper database persistence
- Separation of concerns

**Core principle: Change the UI, keep the AI logic intact.**
