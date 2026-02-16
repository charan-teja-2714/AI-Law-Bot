from fastapi import Request, HTTPException
from app.auth.auth_service import auth_service

async def verify_session_middleware(request: Request):
    """Middleware to verify session token"""
    # Skip auth for public endpoints
    public_paths = ["/api/register", "/api/login", "/api/health", "/docs", "/openapi.json"]
    if any(request.url.path.startswith(path) for path in public_paths):
        return None
    
    # Get session token from header or query
    session_token = request.headers.get("Authorization") or request.query_params.get("session_token")
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Session token required")
    
    # Remove "Bearer " prefix if present
    if session_token.startswith("Bearer "):
        session_token = session_token[7:]
    
    # Verify session
    session = auth_service.get_session(session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    # Attach user info to request state
    request.state.user_id = session["user_id"]
    request.state.username = session["username"]
    
    return session
