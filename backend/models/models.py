from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.core.database import Base
from datetime import datetime, timezone

class Board(Base):
    __tablename__ = "boards"

    name = Column(String, primary_key=True, index=True)
    description = Column(String)

    posts = relationship("Post", back_populates="board", cascade="all, delete-orphan")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    board_name = Column(String, ForeignKey("boards.name"))
    author_name = Column(String)
    content = Column(Text)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    board = relationship("Board", back_populates="posts")
    replies = relationship("Reply", back_populates="post", cascade="all, delete-orphan")

class Reply(Base):
    __tablename__ = "replies"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    author_name = Column(String)
    content = Column(Text)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    post = relationship("Post", back_populates="replies")

class UserSession(Base):
    """Database backed session store so identities persist across server reboots."""
    __tablename__ = "user_sessions"

    token = Column(String, primary_key=True, index=True)
    username = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class PrivateMessage(Base):
    __tablename__ = "private_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_token = Column(String, index=True)
    receiver_token = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
