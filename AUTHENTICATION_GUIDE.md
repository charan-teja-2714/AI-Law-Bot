# 🔐 Authentication Quick Start Guide

## Overview
The AI Law Bot now includes a complete authentication system with user registration, login, and session management. Each user has their own isolated data (sessions, documents, messages).

## 🚀 Quick Setup (First Time)

### 1. Backend Setup
```bash
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies (if not already done)
npm install

# Start frontend server
npm start
```

### 3. First Use
1. Open http://localhost:3000
2. You'll see the login/register screen
3. Click "Register" tab
4. Enter username (min 3 characters) and password (min 6 characters)
5. Click "Register" button
6. You'll be automatically logged in!

## 📖 User Guide

### Registration
- Username must be at least 3 characters
- Password must be at least 6 characters
- Username must be unique
- Account is created permanently (never deleted)

### Login
- Enter your username and password
- Session lasts for 7 days
- You can login from multiple devices
- Browser remembers your session (auto-login on refresh)

### Using the App
- Upload documents (only you can see them)
- Create chat sessions (only you can access them)
- All your data is isolated from other users
- Your username is displayed in the sidebar

### Logout
- Click the "🚪 Logout" button in the sidebar
- You'll be redirected to the login screen
- Your session will be invalidated
- Your data remains saved for next login

## 🔒 Security Features

### Password Security
- Passwords are hashed using SHA256
- Plain text passwords are never stored
- Passwords cannot be recovered (only reset by admin)

### Session Security
- 32-byte secure random tokens
- Tokens expire after 7 days
- Server-side validation on every request
- Tokens stored in browser localStorage

### Data Isolation
- Each user has their own database records
- Users cannot access other users' data
- API enforces ownership checks
- FAISS indexes are session-specific

## 🛠️ Troubleshooting

### "Username already exists"
- Choose a different username
- Usernames are case-sensitive

### "Invalid username or password"
- Check your credentials
- Username and password are case-sensitive
- Ensure no extra spaces

### "Invalid or expired session"
- Your session expired (7 days)
- Click logout and login again
- Clear browser localStorage if issues persist

### Auto-login not working
- Check browser localStorage for 'session_token'
- Session may have expired
- Backend server must be running

### Can't see my old data
- Ensure you're logged in with the correct account
- Old sessions created before authentication won't have user_id
- Run migration script if needed: `python backend/migrate_db.py`

## 🔧 Advanced Configuration

### Change Session Expiration
Edit `backend/app/auth/auth_service.py` line 23:
```python
expires_at = datetime.now() + timedelta(days=7)  # Change 7 to desired days
```

### View All Users (Database)
```bash
cd backend
sqlite3 fir.db
SELECT * FROM users;
.exit
```

### Manually Create User (Database)
```bash
cd backend
sqlite3 fir.db
INSERT INTO users (username, password_hash) VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918');
-- Password is 'admin' (SHA256 hash)
.exit
```

### Reset User Password (Database)
```bash
cd backend
sqlite3 fir.db
UPDATE users SET password_hash = '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918' WHERE username = 'john';
-- Password is now 'admin'
.exit
```

## 📊 Database Structure

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Chat Sessions Table (Updated)
```sql
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL UNIQUE,
    user_id INTEGER,  -- NEW: Links to users.id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## 🎯 API Endpoints

### Public Endpoints (No Auth Required)
- `POST /api/register` - Create new account
- `POST /api/login` - Login and get session token
- `GET /api/health` - Health check

### Protected Endpoints (Auth Required)
- `POST /api/logout` - Logout
- `GET /api/verify-session` - Check session validity
- `POST /api/chat` - Send message
- `POST /api/upload-document` - Upload document
- `GET /api/sessions` - Get all user sessions
- `DELETE /api/sessions/{id}` - Delete session
- All other endpoints require authentication

## 💡 Tips

1. **Remember Your Password**: There's no password reset feature
2. **Use Strong Passwords**: Minimum 6 characters recommended
3. **Multiple Devices**: You can login from multiple devices simultaneously
4. **Session Expiry**: Sessions last 7 days, then you need to login again
5. **Data Privacy**: Your data is isolated and secure

## 🆘 Support

If you encounter issues:
1. Check backend logs in terminal
2. Check browser console (F12) for errors
3. Verify backend is running on port 8000
4. Verify frontend is running on port 3000
5. Clear browser cache and localStorage
6. Restart both servers

## 🎉 Success!

You now have a fully functional authentication system! Each user can:
- ✅ Register and login securely
- ✅ Upload and analyze legal documents
- ✅ Chat with AI assistant
- ✅ Manage multiple sessions
- ✅ Access only their own data
- ✅ Stay logged in for 7 days

Enjoy using the AI Law Bot! ⚖️
