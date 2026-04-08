from fastapi import APIRouter, HTTPException, status
import uuid
import random
from typing import Dict
from .schemas import CaptchaAttempt, SessionResponse, CaptchaResponse
from backend.core.security import generate_anonymous_name, generate_session_token
from backend.core.state import CAPTCHA_STORE, SESSION_STORE

router = APIRouter()

def create_captcha() -> tuple[str, str, str]:
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    question = f"What is {num1} + {num2}?"
    answer = str(num1 + num2)
    challenge_id = str(uuid.uuid4())
    return challenge_id, question, answer

@router.get("/captcha", response_model=CaptchaResponse)
def get_captcha():
    """Generates a simple CAPTCHA challenge."""
    challenge_id, question, answer = create_captcha()
    CAPTCHA_STORE[challenge_id] = answer
    return CaptchaResponse(challenge_id=challenge_id, question=question)

@router.post("/verify-captcha", response_model=SessionResponse)
def verify_captcha(attempt: CaptchaAttempt):
    """Verifies CAPTCHA and returns a new session token & username on success."""
    if attempt.challenge_id not in CAPTCHA_STORE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired CAPTCHA challenge.")
    
    correct_answer = CAPTCHA_STORE.pop(attempt.challenge_id)
    
    if attempt.solution.strip() != correct_answer:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect CAPTCHA solution.")
    
    # Success! Generate identity
    token = generate_session_token()
    username = generate_anonymous_name()
    
    # Store session (temporarily in memory)
    SESSION_STORE[token] = username
    
    return SessionResponse(token=token, username=username)

@router.get("/me", response_model=SessionResponse)
def get_current_user(token: str):
    """Restores session identity using token."""
    if token not in SESSION_STORE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    return SessionResponse(token=token, username=SESSION_STORE[token])
