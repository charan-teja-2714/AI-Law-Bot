# 🏛️ AI Law Bot - Intelligent Legal Assistant

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![React](https://img.shields.io/badge/react-18.2.0-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688)
![License](https://img.shields.io/badge/license-MIT-orange)

> **An advanced AI-powered legal assistant for Indian law, featuring RAG-based document analysis, multilingual support, and intelligent legal section prediction.**

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#️-tech-stack)
- [Architecture](#️-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**AI Law Bot** is a final year project that leverages state-of-the-art AI technologies to provide intelligent legal assistance for Indian law. The system uses **Retrieval-Augmented Generation (RAG)** to analyze legal documents, predict applicable sections, and answer legal queries in multiple languages.

### What Makes This Unique?

- 🔍 **RAG-Powered**: Combines document retrieval with LLM generation for accurate, context-aware responses
- 🌐 **Multilingual**: Supports English, Hindi, Telugu, and Tamil
- 🎤 **Audio Input**: Record questions via voice, powered by Whisper AI
- ⚖️ **IPC to BNS Mapping**: Automatically maps outdated IPC sections to new BNS equivalents
- 📄 **OCR Support**: Extracts text from scanned PDFs using Tesseract
- 🧠 **Semantic Search**: Uses embeddings for intelligent document search (not keyword matching)
- 🔒 **Privacy-First**: All data processed locally with FAISS (no cloud lock-in)

---

## ✨ Key Features

### 🔥 Core Features

| Feature | Description |
|---------|-------------|
| **Document Analysis** | Upload FIRs, legal documents, and get automated analysis with applicable sections |
| **RAG-Based Chat** | Ask questions about uploaded documents with context-aware answers |
| **Legal Section Prediction** | Automatically identifies IPC, CrPC, BNS sections from document content |
| **Entity Extraction** | Extracts complainants, accused, witnesses, lawyers, and legal sections |
| **Multilingual Translation** | Real-time translation between English, Hindi, Telugu, and Tamil |
| **Audio/Video Processing** | Transcribe audio evidence or witness statements using Whisper AI |
| **Case Law Suggestions** | Recommends similar landmark cases based on your query |
| **Session Management** | Persistent chat history with multi-document support per session |

### 🎨 UI/UX Features

- ✅ Professional legal theme with clean, minimal design
- ✅ Real-time typing indicators
- ✅ Formatted responses with section highlighting and emoji headings
- ✅ Scrollable analysis modal for detailed legal reports
- ✅ Audio recorder with minimum duration check
- ✅ Document preview and management
- ✅ Toast notifications for user feedback
- ✅ Delete session with confirmation dialog

---

## 🛠️ Tech Stack

### Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core language |
| **FastAPI** | 0.115.0 | High-performance async API framework |
| **LangChain** | 0.3.7 | RAG orchestration and LLM integration |
| **FAISS** | Latest | Local vector database for semantic search |
| **SQLite** | 3.x | Session and message persistence |
| **Groq** | - | Ultra-fast LLM inference (Llama 3.3 70B) |
| **Whisper** | Latest | OpenAI's speech-to-text model |
| **PyPDF2** | 3.0.1 | PDF text extraction |
| **Tesseract** | 0.3.13 | OCR for scanned documents |
| **FFmpeg** | - | Audio/video format conversion |

### Frontend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.2.0 | Modern UI framework with hooks |
| **JavaScript** | ES6+ | Frontend logic |
| **CSS3** | - | Professional legal theme |
| **MediaRecorder API** | - | Browser audio recording |
| **Fetch API** | - | RESTful API communication |

### AI/ML Models

| Model | Parameters | Provider | Use Case |
|-------|------------|----------|----------|
| **Llama 3.3 70B Versatile** | 70 billion | Groq Cloud | Chat responses, translations, legal analysis |
| **all-mpnet-base-v2** | 110 million | HuggingFace | Document embeddings (768 dimensions) |
| **Whisper Base** | 74 million | OpenAI | Multilingual speech-to-text (99 languages) |

**Why These Models?**
- **Llama 3.3 70B**: Open-source, extremely fast on Groq's LPU architecture, matches GPT-4 performance
- **all-mpnet-base-v2**: Best-in-class sentence embeddings, trained on 1B+ pairs
- **Whisper Base**: State-of-the-art multilingual transcription, works offline

---

## 🏗️ Architecture

### System Architecture

```
┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
│                  │         │                  │         │                  │
│  React Frontend  │◀───────▶│  FastAPI Backend │◀───────▶│  External APIs   │
│  (Port 3000)     │  REST   │  (Port 8000)     │         │  - Groq Cloud    │
│                  │         │                  │         │  - HuggingFace   │
└──────────────────┘         └──────────────────┘         └──────────────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │  Local Storage   │
                             │  - SQLite DB     │
                             │  - FAISS Indexes │
                             │  - Temp Files    │
                             └──────────────────┘
```

### RAG Pipeline Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Document   │────▶│   Chunking   │────▶│  Embedding  │────▶│    FAISS     │
│  (PDF/Text) │     │ (900 chars)  │     │  (768 dims) │     │    Index     │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                                                                      │
                                                                      ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│   Response  │◀────│   LLM (70B)  │◀────│  Retrieval  │◀────│  User Query  │
│ (Formatted) │     │    + RAG     │     │  (Top 5)    │     │ (Embedding)  │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
```

### Database Schema

```sql
-- SQLite Database: fir.db

-- Chat Sessions
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat Messages
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,              -- 'user' or 'assistant'
    content TEXT NOT NULL,
    user_role TEXT NOT NULL,         -- Language code (en, hi, te, ta)
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
);

-- Session Documents
CREATE TABLE session_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    document_id TEXT NOT NULL UNIQUE,
    document_name TEXT NOT NULL,
    document_type TEXT NOT NULL,     -- 'pdf', 'audio', 'video'
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
);
```

---

## 🚀 Installation

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 16+** ([Download](https://nodejs.org/))
- **FFmpeg** ([Download](https://ffmpeg.org/download.html)) - Required for audio processing
- **Tesseract OCR** ([Download](https://github.com/tesseract-ocr/tesseract#installing-tesseract)) - Required for scanned PDFs
- **Git** ([Download](https://git-scm.com/downloads))

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/FIR-RAG.git
cd FIR-RAG
```

### Step 2: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For Python 3.13+ users (pyaudioop module)
pip install pyaudioop
```

### Step 3: Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Required: Groq API Key (Get free key from https://console.groq.com)
GROQ_API_KEY=your_groq_api_key_here

# Optional: For analytics and monitoring
LANGCHAIN_API_KEY=your_langchain_api_key
HF_TOKEN=your_huggingface_token
```

**Get your Groq API Key:**
1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into `.env` file

### Step 4: Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install
```

### Step 5: Configure Tesseract (Windows)

Update the Tesseract path in `backend/app/services/document_processor.py` (line 12):

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

For macOS/Linux, Tesseract is usually auto-detected. If not, update to your Tesseract path:
```bash
# Find Tesseract path
which tesseract
```

### Step 6: Install System Dependencies

#### Windows

1. **Tesseract OCR**:
   - Download installer from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install to `C:\Program Files\Tesseract-OCR\`

2. **FFmpeg**:
   - Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - Extract and add `bin` folder to system PATH

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr ffmpeg
```

#### macOS

```bash
brew install tesseract ffmpeg
```

---

## 🎮 Usage

### Starting the Application

#### Terminal 1: Start Backend Server

```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend runs at:** http://localhost:8000
**API Docs (Swagger):** http://localhost:8000/docs

#### Terminal 2: Start Frontend Server

```bash
cd frontend
npm start
```

**Frontend opens at:** http://localhost:3000

### Using the Application

#### 1️⃣ Upload a Legal Document

1. Click **"📎 Attach Document"** in the sidebar
2. Select **"Upload PDF"** for legal documents (FIRs, complaints, notices)
3. Choose your PDF file
4. Wait 3-5 seconds for processing and indexing
5. Document appears in sidebar list

**Supported formats:** PDF (text or scanned with OCR)

#### 2️⃣ Ask Questions (Text)

**General Legal Questions** (no document needed):
```
User: What is Section 420 IPC?

Bot: Section 420 IPC (now Section 318 BNS) deals with "Cheating and
     dishonestly inducing delivery of property."

     🔹 Offense Details
     - Punishment: Imprisonment up to 7 years and fine
     - Cognizable: Yes
     - Bailable: No
     - Compoundable: No
```

**Document-Specific Questions** (after uploading):
```
User: What sections are mentioned in this FIR?

Bot: Based on the uploaded FIR, the following sections apply:

     🔹 Applicable Sections
     • Section 420 IPC (now Section 318 BNS) - Cheating
     • Section 120B IPC (now Section 61 BNS) - Criminal Conspiracy
     • Section 467 IPC (now Section 336 BNS) - Forgery
```

#### 3️⃣ Ask Questions (Voice)

1. Click the **🎤 microphone** icon in the input box
2. Grant microphone permissions if prompted
3. Speak your question clearly (minimum 2 seconds)
4. Click **Stop** button
5. Transcribed text appears in the input box
6. **Verify the text** and click Submit

**Tips for better transcription:**
- Speak clearly and at moderate pace
- Minimize background noise
- Use good quality microphone
- Keep recording between 2-10 seconds

#### 4️⃣ Analyze Document

1. Ensure a document is uploaded
2. Click **"📊 Analyze Document"** button (green, in sidebar)
3. Wait 3-5 seconds for AI analysis
4. View comprehensive structured report with:
   - **Document Type**: FIR/Legal Notice/Complaint/Petition
   - **Case Summary**: 3-4 sentence overview
   - **Key Parties**: Complainant, accused, witnesses
   - **Applicable IPC Sections**: With BNS equivalents
   - **Applicable CrPC Sections**: Procedural sections
   - **Offense Details**: Cognizable, bailable, severity
   - **Legal Consequences**: Punishments and fines
   - **Similar Cases**: Landmark case suggestions
   - **Recommended Next Steps**: Action items

5. Scroll through the modal to read full analysis
6. Click outside or close button to exit

#### 5️⃣ Switch Languages

1. Click the **language dropdown** (top right of sidebar)
2. Select your preferred language:
   - **English** (en)
   - **हिंदी** (hi)
   - **తెలుగు** (te)
   - **தமிழ்** (ta)
3. All previous messages automatically translate
4. Type new questions in your selected language
5. AI responds in the same language

**Translation is powered by Llama 3.3 LLM** (not Google Translate), providing context-aware legal translations.

#### 6️⃣ Manage Sessions

- **New Chat**: Application creates a fresh session on every startup
- **View History**: All messages automatically saved
- **Delete Session**:
  1. Click 🗑️ trash icon in sidebar
  2. Confirm deletion in dialog
  3. Session and all documents removed

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Key Endpoints

#### Upload PDF Document
```http
POST /api/upload-document?session_id={session_id}
Content-Type: multipart/form-data

Request:
- file: PDF file (multipart)

Response:
{
  "success": true,
  "pdf_name": "FIR_2024.pdf",
  "message": "Document indexed successfully (45 chunks)"
}
```

#### Send Chat Message
```http
POST /api/chat
Content-Type: application/json

Request:
{
  "session_id": "abc-123",
  "message": "What is Section 420 IPC?",
  "language": "en",
  "structured_output": false
}

Response:
{
  "response": "Section 420 IPC (now Section 318 BNS)...",
  "session_id": "abc-123",
  "language": "en",
  "retrieved_chunks": 5
}
```

#### Analyze Document
```http
POST /api/analyze-document?session_id={session_id}
Content-Type: application/json

Response:
{
  "session_id": "abc-123",
  "analysis": {
    "document_type": "FIR",
    "case_summary": "...",
    "applicable_sections": [...],
    "offense_details": {...}
  }
}
```

#### Transcribe Audio
```http
POST /api/transcribe-audio
Content-Type: multipart/form-data

Request:
- file: Audio file (.webm, .mp3, .wav)

Response:
{
  "text": "What is Section 420 IPC?",
  "language": "en"
}
```

**Full API documentation:** http://localhost:8000/docs (Swagger UI)

---

## 📁 Project Structure

```
FIR-RAG/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── models.py              # Pydantic request/response models
│   │   │   └── routes.py              # 18 API endpoints
│   │   ├── services/
│   │   │   ├── chat_service.py        # Main orchestrator
│   │   │   ├── faiss_store.py         # FAISS vector store (embeddings)
│   │   │   ├── document_processor.py  # PDF extraction + legal chunking
│   │   │   ├── translation_service.py # Multilingual via LLM
│   │   │   ├── speech_to_text.py      # Whisper integration
│   │   │   └── legal_section_predictor.py  # Legal analysis
│   │   ├── db/
│   │   │   └── database.py            # SQLite connection + schema
│   │   └── main.py                    # FastAPI app initialization
│   ├── faiss_indexes/                 # FAISS vector indexes (auto-created)
│   ├── fir.db                         # SQLite database (auto-created)
│   ├── requirements.txt               # Python dependencies
│   ├── .env                           # Environment variables
│   └── venv/                          # Virtual environment
│
├── frontend/
│   ├── public/
│   │   └── index.html                 # HTML template
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx      # Main chat logic + state
│   │   │   ├── MessageList.jsx        # Message rendering with formatting
│   │   │   ├── MessageInput.jsx       # Text/audio input handling
│   │   │   ├── AudioRecorder.jsx      # Audio recording UI
│   │   │   ├── Sidebar.jsx            # Document list + controls
│   │   │   ├── DocumentList.jsx       # Document management
│   │   │   └── LegalAnalysisView.jsx  # Analysis modal
│   │   ├── services/
│   │   │   └── api.js                 # API client (fetch)
│   │   ├── App.js                     # Main app component
│   │   ├── App.css                    # Professional legal theme
│   │   └── index.js                   # React entry point
│   ├── package.json                   # Node dependencies
│   └── node_modules/                  # Installed packages
│
└── README.md                          # This file
```

---

## 🔧 Troubleshooting

### Common Backend Issues

**❌ Error: "GROQ_API_KEY not found"**
```bash
# Solution: Add API key to .env file
cd backend
echo "GROQ_API_KEY=your_actual_key_here" >> .env
```

**❌ Error: "ModuleNotFoundError: No module named 'faiss'"**
```bash
# Solution: Install FAISS
pip install faiss-cpu
```

**❌ Error: "Tesseract is not installed or cannot be found"**
```bash
# Solution 1: Install Tesseract (see Installation section)

# Solution 2: Update path in document_processor.py
pytesseract.pytesseract.tesseract_cmd = r"YOUR_TESSERACT_PATH"
```

**❌ Error: "FFmpeg not found"**
```bash
# Solution: Install FFmpeg and add to PATH
# Windows: Download from ffmpeg.org, add bin/ to PATH
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
```

**❌ Error: "No module named 'pyaudioop'" (Python 3.13+)**
```bash
# Solution: Install pyaudioop
pip install pyaudioop
```

### Common Frontend Issues

**❌ Error: "Failed to fetch" or "Network Error"**
```bash
# Solution: Ensure backend is running
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**❌ Error: "Module not found" or missing dependencies**
```bash
# Solution: Reinstall node modules
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**❌ Audio Recording Not Working**
```
Solution:
1. Check browser permissions (Settings → Privacy → Microphone)
2. Use Chrome/Edge (best MediaRecorder support)
3. Ensure HTTPS or localhost (required for getUserMedia)
4. Check console for errors (F12 Developer Tools)
```

### Performance Issues

**⚠️ Slow FAISS Search (many documents)**
```python
# Solution: Reduce top_k in query
results = faiss_store.query(
    session_id=session_id,
    query_text=query,
    top_k=3  # Instead of 5
)
```

**⚠️ Slow Whisper Transcription**
```python
# Solution 1: Use smaller model
# In speech_to_text.py line 17:
model_size="tiny"  # Instead of "base"

# Solution 2: Install CUDA Whisper (GPU)
pip install openai-whisper-cpp
```

**⚠️ Out of Memory Errors**
```python
# Solution: Reduce chunk size
# In document_processor.py line 109:
chunk_size=500,  # Instead of 900
chunk_overlap=100  # Instead of 200
```

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Reporting Issues

1. Check if the issue already exists in [Issues](https://github.com/yourusername/FIR-RAG/issues)
2. Include:
   - Error messages and stack traces
   - Steps to reproduce
   - OS and Python/Node versions
   - Screenshots if applicable

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly (backend + frontend)
5. Commit: `git commit -m "Add feature: description"`
6. Push: `git push origin feature-name`
7. Open a Pull Request with detailed description

### Development Guidelines

- Follow **PEP 8** for Python code
- Use **ESLint** for JavaScript code
- Add **docstrings** to all functions
- Write **unit tests** for new features
- Update **README** with new features

---



## ⚠️ Important Disclaimers

### Legal Notice

- 🚫 **This is a demo system for educational purposes only**
- 🚫 **NOT intended for production legal advice**
- ✅ **Always consult qualified legal professionals for actual legal matters**
- ✅ **Accuracy depends on document quality and LLM performance**
- ✅ **Verify all AI-generated legal information independently**

### Data Privacy

- 🔒 All documents processed locally with FAISS (no cloud storage)
- 🔒 Only LLM API calls sent to Groq (encrypted)
- 🔒 Session data stored in local SQLite database
- 🔒 No telemetry or user tracking

---

## 🙏 Acknowledgments

- **OpenAI** for Whisper speech recognition model
- **Meta AI** for FAISS vector search library
- **Groq** for ultra-fast LLM inference infrastructure
- **HuggingFace** for embeddings and model hosting
- **LangChain** for RAG framework and abstractions
- **FastAPI** for excellent async API framework
- **React** team for amazing frontend library

---

## 📞 Contact & Support

- **GitHub Issues:** [Report a bug](https://github.com/yourusername/FIR-RAG/issues)
- **Discussions:** [Ask questions](https://github.com/yourusername/FIR-RAG/discussions)
- **Email:** your.email@example.com

---

## 🚀 Future Roadmap

- [ ] **Voice Output**: Text-to-speech for AI responses
- [ ] **Mobile App**: React Native version
- [ ] **Image Analysis**: Extract text from evidence photos (OCR)
- [ ] **Case Law Database**: Integrate Supreme Court/High Court judgments
- [ ] **Fine-tuned Model**: Domain-specific legal LLM
- [ ] **Multi-user Auth**: Authentication and authorization
- [ ] **Analytics Dashboard**: Case management and statistics
- [ ] **Export Reports**: PDF generation for legal reports
- [ ] **Collaborative Features**: Share sessions, annotations

---

<p align="center">
  <strong>Made with ❤️ for Legal Tech Innovation</strong>
</p>

<p align="center">
  <a href="#-table-of-contents">⬆ Back to Top</a>
</p>
