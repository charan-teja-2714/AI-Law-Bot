# How to Execute MediSense (React + FastAPI)

## Step-by-Step Execution Guide

### Prerequisites Check

1. **Python 3.8+**
   ```bash
   python --version
   ```

2. **Node.js 16+**
   ```bash
   node --version
   npm --version
   ```

3. **Tesseract OCR**
   - Already installed at: `C:\Program Files\Tesseract-OCR\tesseract.exe`

4. **API Keys**
   - Groq API key
   - Pinecone API key

---

## STEP 1: Setup Environment Variables

Create `.env` file in the `backend` folder:

```bash
cd backend
```

Create a file named `.env` with this content:
```
GROQ_API_KEY=your_groq_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here
```

**Copy from your existing `.env` file in the root directory!**

---

## STEP 2: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- FastAPI
- Uvicorn
- All existing dependencies (langchain, pinecone, etc.)

---

## STEP 3: Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Keep this terminal open!**

Test backend: Open browser → http://localhost:8000
You should see: `{"message": "MediSense API is running"}`

API Docs: http://localhost:8000/docs

---

## STEP 4: Install Frontend Dependencies

**Open a NEW terminal** (keep backend running)

```bash
cd frontend
npm install
```

This will install React and dependencies.

---

## STEP 5: Start Frontend Server

```bash
cd frontend
npm start
```

You should see:
```
Compiled successfully!
Local:            http://localhost:3000
```

Browser will automatically open at http://localhost:3000

---

## STEP 6: Use the Application

1. **Upload PDF**
   - Click "Choose File"
   - Select a medical PDF
   - Wait for "PDF uploaded successfully!"

2. **Select Role**
   - Choose "Patient" or "Doctor" mode

3. **Ask Questions**
   - Type in the input box
   - Press "Send"
   - AI will respond

4. **Generate Doctor Questions**
   - Click "📝 Generate questions to ask the doctor"
   - Questions appear in a modal dialog

---

## Troubleshooting

### Backend won't start

**Error: "No module named 'fastapi'"**
```bash
cd backend
pip install -r requirements.txt
```

**Error: "GROQ_API_KEY not found"**
- Check `.env` file exists in `backend` folder
- Copy API keys from root `.env` file

**Error: "Pinecone connection failed"**
- Verify Pinecone API key is correct
- Check Pinecone environment name

---

### Frontend won't start

**Error: "npm: command not found"**
- Install Node.js from https://nodejs.org/

**Error: "Module not found"**
```bash
cd frontend
rm -rf node_modules
npm install
```

**Error: "Port 3000 already in use"**
```bash
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID_NUMBER> /F
```

---

### PDF Upload Fails

**Error: "Error uploading PDF"**
- Check backend is running (http://localhost:8000)
- Check browser console for errors (F12)
- Verify PDF file is valid

**Error: "Pinecone index error"**
- Check Pinecone API key
- Verify index "medisense-rag" exists in Pinecone dashboard

---

### Chat Not Working

**Error: "Please upload a PDF first"**
- Upload a PDF before asking questions

**Error: "Error sending message"**
- Check backend logs in terminal
- Verify Groq API key is valid

---

## Quick Commands Reference

### Start Everything (2 terminals)

**Terminal 1 - Backend:**
```bash
cd "C:\Users\charan27\OneDrive\Desktop\Final Year Projects\MediSense(RAG)\backend"
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd "C:\Users\charan27\OneDrive\Desktop\Final Year Projects\MediSense(RAG)\frontend"
npm start
```

---

## Testing the Migration

### Test 1: Backend Health
```bash
curl http://localhost:8000
```
Expected: `{"message": "MediSense API is running"}`

### Test 2: API Documentation
Open: http://localhost:8000/docs
You should see interactive API documentation

### Test 3: Frontend
Open: http://localhost:3000
You should see the MediSense UI

### Test 4: Full Flow
1. Upload a PDF from `docs/` folder
2. Ask: "What does this report say?"
3. Verify response is similar to Streamlit version
4. Click "Generate questions"
5. Verify questions appear in modal

---

## Stopping the Application

### Stop Backend
- Press `Ctrl+C` in backend terminal

### Stop Frontend
- Press `Ctrl+C` in frontend terminal

---

## Comparing with Old Streamlit Version

### Run Old Version (for comparison)
```bash
cd "C:\Users\charan27\OneDrive\Desktop\Final Year Projects\MediSense(RAG)"
streamlit run app.py
```

### Run New Version
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

**Test the same PDF and questions in both to verify identical responses!**

---

## Common Issues

### Issue: "Cannot connect to backend"
**Solution:**
1. Check backend is running: http://localhost:8000
2. Check CORS settings in `backend/app/main.py`
3. Verify frontend API URL in `frontend/src/services/api.js`

### Issue: "Database locked"
**Solution:**
```bash
cd backend
rm medisense.db
# Restart backend (will recreate database)
```

### Issue: "Session not found"
**Solution:**
- Refresh the page (generates new session ID)
- Upload PDF again

---

## Production Deployment (Optional)

### Backend (Docker)
```bash
cd backend
docker build -t medisense-backend .
docker run -p 8000:8000 medisense-backend
```

### Frontend (Build)
```bash
cd frontend
npm run build
# Deploy 'build' folder to Vercel/Netlify
```

---

## Need Help?

1. Check backend logs in terminal
2. Check browser console (F12 → Console tab)
3. Verify API keys in `.env`
4. Test API endpoints at http://localhost:8000/docs
5. Compare responses with Streamlit version

---

## Success Checklist

- [ ] Backend starts without errors
- [ ] Frontend opens in browser
- [ ] Can upload PDF
- [ ] Can send messages
- [ ] AI responds correctly
- [ ] Can generate doctor questions
- [ ] Questions appear in modal
- [ ] Responses match Streamlit version
