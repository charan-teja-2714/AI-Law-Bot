import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict

class AuthService:
    """Simple session-based authentication"""
    
    def __init__(self):
        self.active_sessions = {}  # session_token -> {user_id, username, expires_at}
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.hash_password(plain_password) == hashed_password
    
    def create_session(self, user_id: int, username: str) -> str:
        """Create new session and return token"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=7)
        
        self.active_sessions[session_token] = {
            "user_id": user_id,
            "username": username,
            "expires_at": expires_at
        }
        
        return session_token
    
    def get_session(self, session_token: str) -> Optional[Dict]:
        """Get session if valid"""
        session = self.active_sessions.get(session_token)
        
        if not session:
            return None
        
        # Check if expired
        if datetime.now() > session["expires_at"]:
            del self.active_sessions[session_token]
            return None
        
        return session
    
    def delete_session(self, session_token: str):
        """Logout - delete session"""
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]

# Global instance
auth_service = AuthService()
