# 🚀 Authentication Quick Reference Card

## 📋 Quick Commands

### Start Servers
```bash
# Backend
cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm start
```

### Database Migration (First Time Only)
```bash
cd backend
python migrate_db.py
```

### View Users
```bash
cd backend
sqlite3 fir.db "SELECT * FROM users;"
```

### Reset Password (Manual)
```bash
cd backend
sqlite3 fir.db "UPDATE users SET password_hash = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918' WHERE username = 'john';"
# Password is now 'admin'
```

## 🔑 Key Files

### Backend
- `app/auth/auth_service.py` - Auth logic
- `app/api/routes.py` - API endpoints
- `app/db/database.py` - Database schema

### Frontend
- `src/components/Auth.jsx` - Login/register UI
- `src/App.jsx` - Auth state management
- `src/services/api.js` - API client with tokens

## 📡 API Endpoints

### Public
```
POST /api/register        - Create account
POST /api/login           - Get session token
GET  /api/health          - Health check
```

### Protected (Requires session_token)
```
POST   /api/logout                    - Invalidate session
GET    /api/verify-session            - Check token
POST   /api/chat                      - Send message
POST   /api/upload-document           - Upload PDF
GET    /api/sessions                  - Get user sessions
POST   /api/sessions/new              - Create session
DELETE /api/sessions/{id}             - Delete session
GET    /api/history/{id}              - Get chat history
GET    /api/documents/{id}            - Get documents
POST   /api/analyze-document          - Analyze document
POST   /api/extract-entities          - Extract entities
DELETE /api/documents/{sid}/{did}     - Delete document
```

## 🔒 Security

### Password Hashing
```python
import hashlib
hash = hashlib.sha256(password.encode()).hexdigest()
```

### Session Token
```python
import secrets
token = secrets.token_urlsafe(32)  # 32-byte random
```

### Token Validation
```python
from app.auth.auth_service import auth_service
session = auth_service.get_session(token)
if not session:
    raise HTTPException(status_code=401)
```

## 💾 Database Schema

### users
```sql
id              INTEGER PRIMARY KEY
username        TEXT UNIQUE NOT NULL
password_hash   TEXT NOT NULL
created_at      TIMESTAMP
```

### chat_sessions
```sql
id              INTEGER PRIMARY KEY
session_id      TEXT UNIQUE NOT NULL
user_id         INTEGER (FK -> users.id)
created_at      TIMESTAMP
last_activity   TIMESTAMP
```

## 🎨 Frontend Usage

### Get Session Token
```javascript
const token = localStorage.getItem('session_token');
```

### API Call with Token
```javascript
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    session_id: 'xxx',
    message: 'Hello',
    session_token: token
  })
});
```

### Check Auth State
```javascript
const isAuthenticated = !!localStorage.getItem('session_token');
```

## 🐛 Common Issues

### "Unauthorized" Error
```javascript
// Solution: Check token exists
console.log(localStorage.getItem('session_token'));

// Solution: Verify session
fetch('http://localhost:8000/api/verify-session?session_token=' + token)
```

### "Username already exists"
```javascript
// Solution: Use different username
// Usernames are case-sensitive
```

### Auto-login not working
```javascript
// Solution: Clear localStorage
localStorage.clear();
// Then login again
```

### Session expired
```python
# Solution: Change expiration in auth_service.py
expires_at = datetime.now() + timedelta(days=30)  # 30 days
```

## 📊 Testing Queries

### Count Users
```sql
SELECT COUNT(*) FROM users;
```

### List Sessions by User
```sql
SELECT u.username, COUNT(cs.id) as session_count
FROM users u
LEFT JOIN chat_sessions cs ON u.id = cs.user_id
GROUP BY u.username;
```

### Find Orphaned Sessions
```sql
SELECT * FROM chat_sessions WHERE user_id IS NULL;
```

### User Activity
```sql
SELECT u.username, cs.session_id, cs.last_activity
FROM users u
JOIN chat_sessions cs ON u.id = cs.user_id
ORDER BY cs.last_activity DESC;
```

## 🔧 Configuration

### Session Expiration
```python
# File: backend/app/auth/auth_service.py
# Line: 23
expires_at = datetime.now() + timedelta(days=7)
```

### CORS Origins
```python
# File: backend/app/main.py
# Line: 9
allow_origins=["http://localhost:3000"]
```

### Password Min Length
```javascript
// File: frontend/src/components/Auth.jsx
// Line: 75
minLength={6}
```

## 📝 Code Snippets

### Create User (Backend)
```python
from app.auth.auth_service import auth_service
from app.db.database import get_db

password_hash = auth_service.hash_password("password123")
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        ("john", password_hash)
    )
    conn.commit()
```

### Verify User Owns Session (Backend)
```python
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id FROM chat_sessions WHERE session_id = ?",
        (session_id,)
    )
    row = cursor.fetchone()
    if not row or row["user_id"] != current_user_id:
        raise HTTPException(status_code=403, detail="Access denied")
```

### Logout (Frontend)
```javascript
const handleLogout = async () => {
  const token = localStorage.getItem('session_token');
  await fetch('http://localhost:8000/api/logout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_token: token })
  });
  localStorage.removeItem('session_token');
  localStorage.removeItem('username');
  window.location.href = '/';
};
```

## 🎯 Testing Checklist

- [ ] Register new user
- [ ] Login with correct credentials
- [ ] Login with wrong credentials (should fail)
- [ ] Auto-login after refresh
- [ ] Logout and verify session cleared
- [ ] User A cannot see User B's data
- [ ] Upload document (authenticated)
- [ ] Send chat message (authenticated)
- [ ] Create new session (authenticated)
- [ ] Delete session (authenticated)

## 📚 Documentation Files

- `AUTHENTICATION_IMPLEMENTATION.md` - Technical details
- `AUTHENTICATION_GUIDE.md` - User guide
- `TESTING_CHECKLIST.md` - 25 test cases
- `AUTHENTICATION_SUMMARY.md` - Complete overview
- `AUTHENTICATION_QUICK_REFERENCE.md` - This file

## 🆘 Emergency Commands

### Reset All Sessions
```python
# In Python console
from app.auth.auth_service import auth_service
auth_service.active_sessions.clear()
```

### Delete All Users (DANGER!)
```bash
cd backend
sqlite3 fir.db "DELETE FROM users;"
```

### Backup Database
```bash
cd backend
copy fir.db fir_backup.db
```

### Restore Database
```bash
cd backend
copy fir_backup.db fir.db
```

## ✅ Status Indicators

### Backend Running
```
✅ http://localhost:8000/api/health returns 200
```

### Frontend Running
```
✅ http://localhost:3000 shows login screen
```

### Database OK
```
✅ fir.db exists in backend directory
✅ users table has records
```

### Authentication Working
```
✅ Can register new user
✅ Can login with credentials
✅ Can access protected endpoints
✅ Can logout successfully
```

---

**Quick Reference Version:** 1.0.0
**Last Updated:** December 2024
**Project:** AI Law Bot Authentication System
