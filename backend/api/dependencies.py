from fastapi import Header, HTTPException, status
from backend.core.state import SESSION_STORE

def get_current_user(x_session_token: str = Header(..., description="Session token generated after CAPTCHA")) -> str:
    """Dependency to retrieve the username from the session token."""
    if not x_session_token or x_session_token not in SESSION_STORE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing session token. Please verify CAPTCHA first.",
        )
    return SESSION_STORE[x_session_token]
