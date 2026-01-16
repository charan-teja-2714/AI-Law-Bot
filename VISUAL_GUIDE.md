# 🎯 VISUAL EXECUTION GUIDE

## Step-by-Step with Screenshots

### STEP 1: First Time Setup (Do Once)

```
📁 Your Project Folder
└── MediSense(RAG)/
    ├── .env                    ← You have this
    └── backend/
        └── .env                ← Copy here!
```

**Action:**
```bash
copy .env backend\.env
```

---

### STEP 2: Install Dependencies (Do Once)

**Backend:**
```
┌─────────────────────────────────────┐
│ Terminal 1                          │
├─────────────────────────────────────┤
│ > cd backend                        │
│ > pip install -r requirements.txt   │
│                                     │
│ Installing...                       │
│ ✓ fastapi                           │
│ ✓ uvicorn                           │
│ ✓ langchain                         │
│ ✓ pinecone-client                   │
│ ...                                 │
└─────────────────────────────────────┘
```

**Frontend:**
```
┌─────────────────────────────────────┐
│ Terminal 2                          │
├─────────────────────────────────────┤
│ > cd frontend                       │
│ > npm install                       │
│                                     │
│ Installing...                       │
│ ✓ react                             │
│ ✓ react-dom                         │
│ ✓ react-scripts                     │
│ ...                                 │
└─────────────────────────────────────┘
```

---

### STEP 3: Start Backend

**Option A: Double-click `start_backend.bat`**

**Option B: Manual command:**
```
┌─────────────────────────────────────┐
│ Terminal 1 - Backend                │
├─────────────────────────────────────┤
│ > cd backend                        │
│ > uvicorn app.main:app --reload     │
│                                     │
│ INFO: Uvicorn running on            │
│       http://0.0.0.0:8000           │
│ INFO: Application startup complete. │
│                                     │
│ ✅ Backend is running!              │
└─────────────────────────────────────┘
```

**Test:** Open http://localhost:8000
```
┌─────────────────────────────────────┐
│ Browser                             │
├─────────────────────────────────────┤
│ http://localhost:8000               │
│                                     │
│ {"message": "MediSense API is       │
│  running"}                          │
│                                     │
│ ✅ Backend working!                 │
└─────────────────────────────────────┘
```

---

### STEP 4: Start Frontend

**Option A: Double-click `start_frontend.bat`**

**Option B: Manual command:**
```
┌─────────────────────────────────────┐
│ Terminal 2 - Frontend               │
├─────────────────────────────────────┤
│ > cd frontend                       │
│ > npm start                         │
│                                     │
│ Compiled successfully!              │
│                                     │
│ Local:   http://localhost:3000      │
│ Network: http://192.168.1.x:3000    │
│                                     │
│ ✅ Frontend is running!             │
└─────────────────────────────────────┘
```

**Browser opens automatically:**
```
┌─────────────────────────────────────┐
│ Browser - http://localhost:3000     │
├─────────────────────────────────────┤
│                                     │
│     🩺 MediSense AI                 │
│                                     │
│  Understand your medical reports    │
│  in simple, human language          │
│                                     │
│  📂 Upload Medical Report           │
│  [Choose File] No file chosen       │
│                                     │
│  ⚙️ Explanation Mode:               │
│  [Patient ▼]                        │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Chat messages appear here   │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  [Ask something...] [Send]          │
│                                     │
│ ✅ UI is ready!                     │
└─────────────────────────────────────┘
```

---

### STEP 5: Upload PDF

```
┌─────────────────────────────────────┐
│ 1. Click "Choose File"              │
│                                     │
│ 2. Select PDF from docs/ folder     │
│    (e.g., p1.pdf)                   │
│                                     │
│ 3. Wait for upload...               │
│    ⏳ Indexing medical report...    │
│                                     │
│ 4. Success!                         │
│    ✅ PDF uploaded successfully!    │
└─────────────────────────────────────┘
```

---

### STEP 6: Chat with AI

```
┌─────────────────────────────────────┐
│ Type: "What does this report say?"  │
│                                     │
│ ┌─────────────────────────────┐     │
│ │ 🧑 You:                     │     │
│ │ What does this report say?  │     │
│ │                             │     │
│ │ 🩺 AI:                      │     │
│ │ Your report shows...        │     │
│ │ [detailed explanation]      │     │
│ └─────────────────────────────┘     │
│                                     │
│ [Ask something...] [Send]           │
└─────────────────────────────────────┘
```

---

### STEP 7: Generate Questions

```
┌─────────────────────────────────────┐
│ Click: "📝 Generate questions"      │
│                                     │
│ ⏳ Preparing questions...           │
│                                     │
│ ┌───────────────────────────────┐   │
│ │ 🩺 Questions to Ask Your     │   │
│ │    Doctor                     │   │
│ │                               │   │
│ │ - Is this value normal for    │   │
│ │   my age?                     │   │
│ │                               │   │
│ │ - Should I follow up with     │   │
│ │   additional tests?           │   │
│ │                               │   │
│ │ - Are there lifestyle changes │   │
│ │   I should consider?          │   │
│ │                               │   │
│ │        [Close]                │   │
│ └───────────────────────────────┘   │
└─────────────────────────────────────┘
```

---

## 🎯 Both Terminals Running

```
┌──────────────────────┐  ┌──────────────────────┐
│ Terminal 1           │  │ Terminal 2           │
│ BACKEND              │  │ FRONTEND             │
├──────────────────────┤  ├──────────────────────┤
│ > uvicorn app.main   │  │ > npm start          │
│                      │  │                      │
│ ✅ Running on        │  │ ✅ Running on        │
│    :8000             │  │    :3000             │
│                      │  │                      │
│ Keep this open! →    │  │ ← Keep this open!    │
└──────────────────────┘  └──────────────────────┘
```

---

## 🔍 Verification Checklist

```
✅ Backend Terminal:
   └─ Shows "Application startup complete"

✅ Frontend Terminal:
   └─ Shows "Compiled successfully"

✅ Browser (localhost:8000):
   └─ Shows {"message": "MediSense API is running"}

✅ Browser (localhost:3000):
   └─ Shows MediSense UI

✅ Can upload PDF:
   └─ Success message appears

✅ Can send message:
   └─ AI responds

✅ Can generate questions:
   └─ Modal popup appears
```

---

## 🛑 How to Stop

```
Terminal 1 (Backend):     Terminal 2 (Frontend):
Press Ctrl+C              Press Ctrl+C

┌──────────────────┐      ┌──────────────────┐
│ ^C               │      │ ^C               │
│ Shutting down... │      │ Shutting down... │
│ ✓ Stopped        │      │ ✓ Stopped        │
└──────────────────┘      └──────────────────┘
```

---

## 🚨 Common Errors & Fixes

### Error: "Port 8000 already in use"
```
❌ Error: Address already in use

✅ Fix:
   1. Find process: netstat -ano | findstr :8000
   2. Kill it: taskkill /PID <number> /F
   3. Restart backend
```

### Error: "Module not found"
```
❌ Error: No module named 'fastapi'

✅ Fix:
   cd backend
   pip install -r requirements.txt
```

### Error: "npm command not found"
```
❌ Error: 'npm' is not recognized

✅ Fix:
   Install Node.js from https://nodejs.org/
```

### Error: "Cannot connect to backend"
```
❌ Error: Failed to fetch

✅ Fix:
   1. Check backend is running (Terminal 1)
   2. Visit http://localhost:8000
   3. If not working, restart backend
```

---

## 🎉 Success Screen

```
┌─────────────────────────────────────────────┐
│                                             │
│          🩺 MediSense AI                    │
│                                             │
│  ✅ Backend: Running                        │
│  ✅ Frontend: Running                       │
│  ✅ PDF: Uploaded                           │
│  ✅ AI: Responding                          │
│  ✅ Questions: Generated                    │
│                                             │
│         🎉 ALL SYSTEMS GO! 🎉               │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📚 Next Steps

1. ✅ Test with different PDFs
2. ✅ Try Patient vs Doctor mode
3. ✅ Compare with Streamlit version
4. ✅ Check API docs at /docs
5. ✅ Review chat history in database

---

## 🆘 Still Having Issues?

1. Read `HOW_TO_EXECUTE.md` for detailed troubleshooting
2. Check terminal logs for error messages
3. Verify `.env` file has correct API keys
4. Test API at http://localhost:8000/docs
5. Check browser console (F12) for errors
