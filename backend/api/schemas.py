from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CaptchaAttempt(BaseModel):
    challenge_id: str
    solution: str

class SessionResponse(BaseModel):
    token: str
    username: str

class CaptchaResponse(BaseModel):
    challenge_id: str
    question: str

class BoardBase(BaseModel):
    name: str
    description: str

class BoardResponse(BoardBase):
    pass
    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    content: str
    # image handling will be added in phase 3

class PostResponse(BaseModel):
    id: int
    board_name: str
    author_name: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
