from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from backend.core.database import Base
from datetime import datetime, timezone

class Board(Base):
    __tablename__ = "boards"

    name = Column(String, primary_key=True, index=True)
    description = Column(String)

    posts = relationship("Post", back_populates="board")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    board_name = Column(String, ForeignKey("boards.name"))
    author_name = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    board = relationship("Board", back_populates="posts")
    
# Image posting will be added later in Phase 3
