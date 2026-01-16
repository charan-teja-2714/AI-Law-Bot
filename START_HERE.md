# 🚀 QUICK START - MediSense (React + FastAPI)

## ⚡ Fastest Way to Run

### Option 1: Using Batch Scripts (Easiest)

1. **Double-click** `start_backend.bat`
   - Wait for "Application startup complete"
   - Keep this window open

2. **Double-click** `start_frontend.bat`
   - Browser will open automatically at http://localhost:3000

3. **Done!** Start using the app

---

### Option 2: Manual Commands

**Terminal 1 (Backend):**
```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

---

## 📋 First Time Setup (One-time only)

### 1. Copy Environment Variables

Copy your `.env` file to the `backend` folder:
```bash
copy .env backend\.env
```

Or manually create `backend\.env` with:
```
GROQ_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
PINECONE_ENVIRONMENT=your_env_here
```

### 2. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
```

---

## ✅ Verify It's Working

1. **Backend**: Open http://localhost:8000
   - Should see: `{"message": "MediSense API is running"}`

2. **Frontend**: Open http://localhost:3000
   - Should see: MediSense AI interface

3. **API Docs**: Open http://localhost:8000/docs
   - Should see: Interactive API documentation

---

## 🎯 How to Use

1. **Upload PDF**
   - Click "Choose File"
   - Select a medical report PDF
   - Wait for success message

2. **Select Mode**
   - Choose "Patient" (simple) or "Doctor" (technical)

3. **Ask Questions**
   - Type your question
   - Click "Send"
   - AI responds

4. **Generate Questions**
   - Click "📝 Generate questions to ask the doctor"
   - Questions appear in popup

---

## 🛑 How to Stop

- Press `Ctrl+C` in both terminal windows
- Or close the terminal windows

---

## 🔧 Troubleshooting

### Backend won't start?
```bash
cd backend
pip install -r requirements.txt
```

### Frontend won't start?
```bash
cd frontend
npm install
```

### Can't upload PDF?
- Make sure backend is running (http://localhost:8000)
- Check `.env` file has correct API keys

### Questions not generating?
- Upload a PDF first
- Check Groq API key is valid

---

## 📊 Compare with Old Version

### Run Streamlit (old):
```bash
streamlit run app.py
```

### Run React+FastAPI (new):
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

**Test same PDF in both to verify identical AI responses!**

---

## 🎓 What Changed?

### Same (AI Logic):
✅ PDF processing
✅ OCR
✅ Chunking
✅ Embeddings
✅ Pinecone
✅ Groq LLM
✅ Safety rules

### Different (UI Only):
🆕 React instead of Streamlit
🆕 FastAPI backend
🆕 SQLite database
🆕 REST API

---

## 📁 Project Structure

```
MediSense(RAG)/
├── start_backend.bat       ← Double-click to start backend
├── start_frontend.bat      ← Double-click to start frontend
├── backend/                ← FastAPI backend
│   ├── app/
│   │   ├── api/           ← REST endpoints
│   │   ├── services/      ← AI logic (reused)
│   │   └── main.py
│   └── .env               ← API keys (copy from root)
├── frontend/               ← React UI
│   ├── src/
│   │   ├── components/    ← React components
│   │   └── services/      ← API client
│   └── package.json
└── docs/                   ← Test PDFs
```

---

## 🎉 Success!

If you see:
- ✅ Backend running at http://localhost:8000
- ✅ Frontend running at http://localhost:3000
- ✅ Can upload PDF
- ✅ Can chat with AI
- ✅ Can generate questions

**You're all set!** 🚀

---

## 📞 Need Help?

1. Check `HOW_TO_EXECUTE.md` for detailed troubleshooting
2. Check backend terminal for error messages
3. Check browser console (F12) for frontend errors
4. Verify `.env` file has correct API keys
