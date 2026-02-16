# ✅ Authentication Testing Checklist

Use this checklist to verify the authentication system is working correctly.

## 🔧 Pre-Testing Setup

- [ ] Backend server is running on http://localhost:8000
- [ ] Frontend server is running on http://localhost:3000
- [ ] Database file `fir.db` exists in backend directory
- [ ] No errors in backend terminal
- [ ] No errors in browser console (F12)

## 📝 Registration Tests

### Test 1: Successful Registration
- [ ] Open http://localhost:3000
- [ ] Click "Register" tab
- [ ] Enter username: `testuser1` (min 3 chars)
- [ ] Enter password: `password123` (min 6 chars)
- [ ] Click "Register" button
- [ ] ✅ Should redirect to chat interface
- [ ] ✅ Should see username "testuser1" in sidebar
- [ ] ✅ Should see "New Chat" button

### Test 2: Duplicate Username
- [ ] Logout from current session
- [ ] Click "Register" tab
- [ ] Enter username: `testuser1` (same as before)
- [ ] Enter password: `anypassword`
- [ ] Click "Register" button
- [ ] ✅ Should show error: "Username already exists"

### Test 3: Validation Errors
- [ ] Try username with 2 characters
- [ ] ✅ Should show HTML5 validation error
- [ ] Try password with 5 characters
- [ ] ✅ Should show HTML5 validation error

## 🔐 Login Tests

### Test 4: Successful Login
- [ ] Logout if logged in
- [ ] Click "Login" tab
- [ ] Enter username: `testuser1`
- [ ] Enter password: `password123`
- [ ] Click "Login" button
- [ ] ✅ Should redirect to chat interface
- [ ] ✅ Should see username in sidebar

### Test 5: Wrong Password
- [ ] Logout if logged in
- [ ] Click "Login" tab
- [ ] Enter username: `testuser1`
- [ ] Enter password: `wrongpassword`
- [ ] Click "Login" button
- [ ] ✅ Should show error: "Invalid username or password"

### Test 6: Non-existent User
- [ ] Logout if logged in
- [ ] Click "Login" tab
- [ ] Enter username: `nonexistent`
- [ ] Enter password: `anypassword`
- [ ] Click "Login" button
- [ ] ✅ Should show error: "Invalid username or password"

## 💾 Session Persistence Tests

### Test 7: Auto-Login on Refresh
- [ ] Login as `testuser1`
- [ ] Refresh the page (F5)
- [ ] ✅ Should stay logged in (no login screen)
- [ ] ✅ Should see same username in sidebar

### Test 8: Auto-Login After Browser Close
- [ ] Login as `testuser1`
- [ ] Close browser completely
- [ ] Reopen browser
- [ ] Navigate to http://localhost:3000
- [ ] ✅ Should auto-login (no login screen)

### Test 9: Logout Clears Session
- [ ] Login as `testuser1`
- [ ] Click "🚪 Logout" button in sidebar
- [ ] ✅ Should redirect to login screen
- [ ] Refresh the page
- [ ] ✅ Should still show login screen (not auto-login)

## 🔒 User Isolation Tests

### Test 10: User A Cannot See User B's Data
- [ ] Register new user: `userA` / `password123`
- [ ] Upload a document (any PDF)
- [ ] Create a chat message: "Hello from User A"
- [ ] Note the session ID in URL or sidebar
- [ ] Logout
- [ ] Register new user: `userB` / `password123`
- [ ] ✅ Should NOT see User A's documents
- [ ] ✅ Should NOT see User A's messages
- [ ] ✅ Should NOT see User A's sessions
- [ ] ✅ Should start with empty chat

### Test 11: User Can Access Own Data After Re-login
- [ ] Login as `userA`
- [ ] Upload document "test1.pdf"
- [ ] Send message "Test message 1"
- [ ] Logout
- [ ] Login as `userA` again
- [ ] ✅ Should see "test1.pdf" in documents
- [ ] ✅ Should see "Test message 1" in chat history

## 🚀 Functionality Tests (Authenticated)

### Test 12: Upload Document
- [ ] Login as any user
- [ ] Click "📎 Attach Document"
- [ ] Select "Upload PDF"
- [ ] Choose a PDF file
- [ ] ✅ Should upload successfully
- [ ] ✅ Should appear in documents list
- [ ] ✅ Should show success toast

### Test 13: Send Chat Message
- [ ] Login as any user
- [ ] Type message: "What is Section 420 IPC?"
- [ ] Click send button
- [ ] ✅ Should send successfully
- [ ] ✅ Should receive AI response
- [ ] ✅ Should save to chat history

### Test 14: Create New Session
- [ ] Login as any user
- [ ] Click "New Chat" button
- [ ] ✅ Should create new session
- [ ] ✅ Should clear current chat
- [ ] ✅ Should appear in sessions list

### Test 15: Delete Session
- [ ] Login as any user
- [ ] Create 2-3 sessions
- [ ] Hover over a session in sidebar
- [ ] Click 🗑️ delete button
- [ ] ✅ Should delete session
- [ ] ✅ Should remove from list
- [ ] ✅ Should switch to another session if current

## 🌐 API Tests (Optional)

### Test 16: Protected Endpoint Without Token
```bash
curl http://localhost:8000/api/sessions
```
- [ ] ✅ Should return 401 Unauthorized

### Test 17: Protected Endpoint With Valid Token
```bash
# Get token from localStorage in browser console
# localStorage.getItem('session_token')
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/sessions?session_token=YOUR_TOKEN
```
- [ ] ✅ Should return user's sessions

### Test 18: Verify Session Endpoint
```bash
curl http://localhost:8000/api/verify-session?session_token=YOUR_TOKEN
```
- [ ] ✅ Should return user info if valid
- [ ] ✅ Should return 401 if invalid

## 🐛 Edge Cases

### Test 19: Expired Session (Manual)
- [ ] Login as any user
- [ ] In `auth_service.py`, change expiration to 1 second
- [ ] Restart backend
- [ ] Wait 2 seconds
- [ ] Try to send a message
- [ ] ✅ Should return 401 Unauthorized
- [ ] ✅ Should redirect to login (if frontend handles it)

### Test 20: Multiple Devices
- [ ] Login as `testuser1` in Chrome
- [ ] Login as `testuser1` in Firefox (or incognito)
- [ ] Upload document in Chrome
- [ ] ✅ Should NOT appear in Firefox (different session)
- [ ] Refresh Firefox
- [ ] ✅ Still should NOT appear (user isolation works)

### Test 21: SQL Injection Prevention
- [ ] Try username: `admin' OR '1'='1`
- [ ] Try password: `anything`
- [ ] Click Login
- [ ] ✅ Should fail with "Invalid username or password"
- [ ] ✅ Should NOT bypass authentication

## 📊 Database Verification

### Test 22: Check Users Table
```bash
cd backend
sqlite3 fir.db
SELECT * FROM users;
```
- [ ] ✅ Should see all registered users
- [ ] ✅ Passwords should be hashed (not plain text)
- [ ] ✅ Each user has unique ID

### Test 23: Check Sessions Table
```bash
sqlite3 fir.db
SELECT session_id, user_id FROM chat_sessions;
```
- [ ] ✅ Each session has a user_id
- [ ] ✅ user_id matches users.id

### Test 24: Check User Isolation in DB
```bash
sqlite3 fir.db
SELECT cs.session_id, u.username 
FROM chat_sessions cs 
JOIN users u ON cs.user_id = u.id;
```
- [ ] ✅ Each session is linked to correct user

## 🎯 Final Verification

### Test 25: Complete User Journey
- [ ] Register new user `finaltest`
- [ ] Upload 2 documents
- [ ] Send 3 chat messages
- [ ] Create 2 sessions
- [ ] Analyze a document
- [ ] Switch between sessions
- [ ] Logout
- [ ] Login again
- [ ] ✅ All data should be preserved
- [ ] ✅ All functionality should work

## 📝 Test Results

**Date Tested:** _______________

**Tester Name:** _______________

**Total Tests:** 25

**Passed:** _____ / 25

**Failed:** _____ / 25

**Notes:**
_______________________________________
_______________________________________
_______________________________________

## ✅ Sign-off

- [ ] All critical tests passed (Tests 1-15)
- [ ] User isolation verified (Tests 10-11)
- [ ] Session management works (Tests 7-9)
- [ ] Database structure correct (Tests 22-24)
- [ ] Ready for production/demo

**Approved by:** _______________

**Date:** _______________
