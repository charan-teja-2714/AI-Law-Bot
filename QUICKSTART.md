# Quick Start Guide

## Prerequisites
- Python 3.8+
- Node.js 16+
- Tesseract OCR installed
- Pinecone API key
- Groq API key

## Environment Setup

Create `.env` file in backend directory:
```
GROQ_API_KEY=your_groq_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_pinecone_env
```

## Start Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: http://localhost:8000

## Start Frontend

```bash
cd frontend
npm install
npm start
```

Frontend will run at: http://localhost:3000

## Usage Flow

1. Open http://localhost:3000
2. Upload a medical PDF report
3. Select role (Patient or Doctor)
4. Ask questions about the report
5. Click "Generate questions" for doctor consultation prep

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation (FastAPI auto-generates this)

## Troubleshooting

**Backend won't start:**
- Check .env file exists with correct keys
- Verify Tesseract is installed
- Check Python dependencies installed

**Frontend won't start:**
- Run `npm install` first
- Check Node.js version (16+)
- Clear npm cache: `npm cache clean --force`

**PDF upload fails:**
- Check file is valid PDF
- Verify Pinecone connection
- Check backend logs for errors

**Questions not generating:**
- Ensure PDF is uploaded first
- Check Groq API key is valid
- Verify backend session has PDF indexed
