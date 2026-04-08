from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.models.models import UserSession

def get_current_user(
    x_session_token: str = Header(..., description="Session token generated after CAPTCHA"),
    db: Session = Depends(get_db)
) -> str:
    """Dependency to retrieve the username from the database using the session token."""
    if not x_session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing session token. Please verify CAPTCHA first.",
        )
        
    user_session = db.query(UserSession).filter(UserSession.token == x_session_token).first()
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token. Identity not found.",
        )
        
    return user_session.username
