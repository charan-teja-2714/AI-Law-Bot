# AI Law Bot - Indian Legal RAG Assistant

A sophisticated RAG-based AI system for analyzing legal documents, FIRs, and providing Indian legal assistance using IPC, CrPC, and BNS frameworks.

## 🎯 Features

### Core Functionality
- **Legal Document Analysis**: Upload and analyze FIRs, legal notices, complaints, and other legal documents
- **Section Prediction**: Automatically predict applicable IPC, CrPC, and BNS sections
- **RAG-based Q&A**: Ask questions about uploaded legal documents with context-aware responses
- **Structured Legal Analysis**: Get comprehensive reports with case summaries, legal consequences, and next steps

### Advanced Features
- **Multilingual Support**: English, Hindi, Telugu, and Tamil
- **Audio/Video Processing**: Upload audio or video files for automatic transcription and analysis
- **Local Vector Storage**: FAISS-based vector database (no cloud dependency)
- **Professional UI**: Clean, minimal, law-themed interface

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI
- **LLM**: Groq API (llama-3.3-70b-versatile)
- **RAG Framework**: LangChain
- **Vector DB**: FAISS (local)
- **Embeddings**: HuggingFace sentence-transformers
- **Speech-to-Text**: OpenAI Whisper
- **Document Processing**: PyPDF2, Tesseract OCR

### Frontend Stack
- **Framework**: React
- **Styling**: Custom CSS (Professional Law Theme)
- **State Management**: React Hooks
- **API Communication**: Fetch API

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- FFmpeg (for audio/video processing)
- Tesseract OCR (for scanned documents)
- Groq API Key

### 1. Clone Repository
```bash
git clone <repository-url>
cd FIR-RAG
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create `backend/.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 5. Install System Dependencies

#### Windows:
- **Tesseract OCR**: Download from https://github.com/UB-Mannheim/tesseract/wiki
  - Install to `C:\Program Files\Tesseract-OCR\`
- **FFmpeg**: Download from https://ffmpeg.org/download.html
  - Add to PATH

#### Linux:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr ffmpeg
```

#### Mac:
```bash
brew install tesseract ffmpeg
```

## 🚀 Running the Application

### Start Backend

```bash
cd backend
venv\Scripts\activate  # or source venv/bin/activate on Linux/Mac
uvicorn app.main:app --reload --port 8000
```

Backend will run on: `http://localhost:8000`

### Start Frontend

```bash
cd frontend
npm start
```

Frontend will run on: `http://localhost:3000`

## 📖 Usage

### 1. Upload Legal Document
- Click the **📎** (attach) button
- Choose **Upload PDF** for legal documents/FIRs
- Or choose **Upload Audio/Video** for audio/video files

### 2. Ask Questions
- Select language (English, Hindi, Telugu, Tamil)
- Type your legal question
- Toggle **Structured Analysis Mode** for detailed section predictions

### 3. Analyze Document
- Click **📊 Analyze Document** button in sidebar
- View comprehensive legal analysis with:
  - Document type
  - Case summary
  - Applicable IPC/CrPC/BNS sections
  - Legal consequences
  - Similar cases
  - Recommended next steps

### 4. Language Support
- Select your preferred language from the sidebar
- Ask questions in your language
- Receive responses in the same language

## 🔧 Configuration

### Customize LLM Settings
Edit `backend/app/services/chat_service.py`:
```python
self.llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0.6  # Adjust for creativity vs accuracy
)
```

### Whisper Model Size
Edit `backend/app/services/speech_to_text.py`:
```python
speech_to_text_service = SpeechToTextService(model_size="base")
# Options: tiny, base, small, medium, large
```

### Chunking Parameters
Edit `backend/app/services/document_processor.py`:
```python
chunk_size=900,
chunk_overlap=200
```

## 📂 Project Structure

```
FIR-RAG/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── models.py          # Pydantic models
│   │   │   └── routes.py          # API endpoints
│   │   ├── services/
│   │   │   ├── chat_service.py    # Main chat logic
│   │   │   ├── faiss_store.py     # FAISS vector store
│   │   │   ├── document_processor.py
│   │   │   ├── translation_service.py
│   │   │   ├── speech_to_text.py
│   │   │   └── legal_section_predictor.py
│   │   ├── db/
│   │   │   └── database.py        # SQLite setup
│   │   └── main.py                # FastAPI app
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── LegalAnalysisView.jsx
│   │   │   ├── LanguageSelector.jsx
│   │   │   ├── MessageInput.jsx
│   │   │   └── MessageList.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.css              # Professional law theme
│   │   └── App.jsx
│   └── package.json
└── faiss_indexes/                # Local FAISS storage
```

## 🎨 UI Theme

Professional law-themed design with:
- **Colors**: Navy (#1a2332), Charcoal (#2c3e50), Light Gray (#f5f7fa)
- **Style**: Clean, minimal, corporate/judiciary
- **Typography**: Segoe UI
- **No gradients or bright colors**

## ⚠️ Important Notes

### Limitations
- This is a demo system - NOT for production legal advice
- Always consult qualified legal professionals
- Accuracy depends on document quality and LLM performance
- Whisper transcription works best with clear audio

### Data Privacy
- All data is processed locally (FAISS)
- No data sent to third parties except Groq API for LLM
- Session data stored in local SQLite

### Performance
- First run downloads embedding models (~420MB)
- Whisper model download on first use (~140MB for base model)
- FAISS indexes stored locally in `faiss_indexes/`

## 🐛 Troubleshooting

### Tesseract not found
Ensure Tesseract is installed and path is correct in:
`backend/app/services/document_processor.py`

### FFmpeg not found
Install FFmpeg and add to system PATH

### Out of memory
- Reduce Whisper model size to "tiny"
- Reduce chunk size in document processor

### Slow responses
- Use smaller embedding model
- Reduce top_k in retrieval

## 📄 License

This project is for educational and demo purposes.

## 🤝 Contributing

This is a final year project. For issues or suggestions, please create an issue.

## 📧 Contact

For questions about this project, please open an issue in the repository.
