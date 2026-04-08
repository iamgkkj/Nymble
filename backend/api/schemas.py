from pydantic import BaseModel

class CaptchaAttempt(BaseModel):
    challenge_id: str
    solution: str

class SessionResponse(BaseModel):
    token: str
    username: str

class CaptchaResponse(BaseModel):
    challenge_id: str
    question: str
