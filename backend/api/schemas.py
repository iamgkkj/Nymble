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
    options: List[str]

class BoardBase(BaseModel):
    name: str
    description: str

class BoardResponse(BoardBase):
    class Config:
        from_attributes = True

class ReplyCreate(BaseModel):
    content: str

class ReplyResponse(BaseModel):
    id: int
    post_id: int
    author_name: str
    content: str
    image_url: Optional[str] = None
    is_whisper: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class PostResponse(BaseModel):
    id: int
    board_name: str
    author_name: str
    content: str
    image_url: Optional[str] = None
    is_whisper: bool = False
    created_at: datetime
    replies: List[ReplyResponse] = []

    class Config:
        from_attributes = True
