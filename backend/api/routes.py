from fastapi import APIRouter, HTTPException, status, Header, Depends
from sqlalchemy.orm import Session
import uuid
import random

from backend.api.schemas import CaptchaAttempt, SessionResponse, CaptchaResponse
from backend.core.security import generate_anonymous_name, generate_session_token
from backend.core.state import CAPTCHA_STORE
from backend.core.database import get_db
from backend.models.models import UserSession

router = APIRouter()

EMOJIS = {"cat": "🐱", "dog": "🐶", "mouse": "🐭", "fox": "🦊", "bear": "🐻", "panda": "🐼", "lion": "🦁", "frog": "🐸"}

def create_captcha() -> tuple[str, str, str, list]:
    names = random.sample(list(EMOJIS.keys()), 4)
    target_name = random.choice(names)
    options = [EMOJIS[n] for n in names]
    random.shuffle(options)
    question = f"Prove you're human: Select the {target_name}"
    answer = EMOJIS[target_name]
    challenge_id = str(uuid.uuid4())
    return challenge_id, question, answer, options

@router.get("/captcha", response_model=CaptchaResponse)
def get_captcha():
    """Generates an emoji CAPTCHA challenge."""
    challenge_id, question, answer, options = create_captcha()
    CAPTCHA_STORE[challenge_id] = answer
    return CaptchaResponse(challenge_id=challenge_id, question=question, options=options)

@router.post("/verify-captcha", response_model=SessionResponse)
def verify_captcha(attempt: CaptchaAttempt, db: Session = Depends(get_db)):
    """Verifies CAPTCHA and returns a new persistent session token & username on success."""
    if attempt.challenge_id not in CAPTCHA_STORE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired CAPTCHA challenge.")
    
    correct_answer = CAPTCHA_STORE.pop(attempt.challenge_id)
    
    if attempt.solution.strip() != correct_answer:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect CAPTCHA solution.")
    
    # Success! Generate identity
    token = generate_session_token()
    username = generate_anonymous_name()
    
    # Store persistent session in database
    new_session = UserSession(token=token, username=username)
    db.add(new_session)
    db.commit()
    
    return SessionResponse(token=token, username=username)

@router.get("/me", response_model=SessionResponse)
def get_current_user_route(
    x_session_token: str = Header(..., description="Session token generated after CAPTCHA"),
    db: Session = Depends(get_db)
):
    """Restores session identity using token header."""
    user_session = db.query(UserSession).filter(UserSession.token == x_session_token).first()
    if not user_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    return SessionResponse(token=user_session.token, username=user_session.username)
