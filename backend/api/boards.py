from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.core.database import get_db
from backend.models.models import Board, Post
from backend.api.schemas import BoardResponse, PostCreate, PostResponse
from backend.api.dependencies import get_current_user

router = APIRouter()

DEFAULT_BOARDS = [
    {"name": "anime", "description": "Discuss anime, manga, and related culture."},
    {"name": "academics", "description": "Study tips, notes, and academic discussions."},
    {"name": "technology", "description": "Tech news, programming, and gadgets."},
    {"name": "movies", "description": "Cinema, tv shows, and pop corn talks."},
    {"name": "games", "description": "Video games, board games, tabletop."},
    {"name": "exams", "description": "Exam preparation and results discussions."},
    {"name": "placements", "description": "Internships, job prep, and interview experiences."},
    {"name": "travel", "description": "Share travel stories and planned trips."},
    {"name": "hostel", "description": "Hostel life, mess food, and late night talks."},
    {"name": "dayscholar", "description": "Commute, bus routes, and day scholar life."}
]

def init_boards(db: Session):
    """Initializes the default boards if they do not exist."""
    for b_data in DEFAULT_BOARDS:
        board = db.query(Board).filter(Board.name == b_data["name"]).first()
        if not board:
            new_board = Board(name=b_data["name"], description=b_data["description"])
            db.add(new_board)
    db.commit()

@router.get("/boards", response_model=List[BoardResponse])
def get_boards(db: Session = Depends(get_db)):
    """Retrieve all available boards."""
    boards = db.query(Board).all()
    # Auto-initialize if empty (useful for first run)
    if not boards:
        init_boards(db)
        boards = db.query(Board).all()
    return boards

@router.get("/boards/{board_name}/posts", response_model=List[PostResponse])
def get_board_posts(board_name: str, db: Session = Depends(get_db)):
    """Retrieve all posts for a specific board."""
    board = db.query(Board).filter(Board.name == board_name).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    # Return posts ordered by newest first
    posts = db.query(Post).filter(Post.board_name == board_name).order_by(Post.created_at.desc()).all()
    return posts

@router.post("/boards/{board_name}/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_board_post(
    board_name: str,
    post_in: PostCreate,
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new post in a specific board. Requires session token."""
    board = db.query(Board).filter(Board.name == board_name).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    new_post = Post(
        board_name=board_name,
        author_name=username,
        content=post_in.content
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
