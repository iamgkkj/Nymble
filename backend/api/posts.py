from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from backend.core.database import get_db
from backend.models.models import Post, Reply
from backend.api.schemas import PostResponse, ReplyResponse
from backend.api.dependencies import get_current_user
from backend.core.upload import save_upload_file

router = APIRouter()

@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a specific post along with its replies."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.post("/posts/{post_id}/replies", response_model=ReplyResponse, status_code=status.HTTP_201_CREATED)
def create_reply(
    post_id: int,
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    username: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reply to a specific post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    image_url = None
    if image and image.filename:
        image_url = save_upload_file(image)
        
    from backend.core.moderation import moderate_content
    try:
        content = moderate_content(content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    new_reply = Reply(
        post_id=post_id,
        author_name=username,
        content=content,
        image_url=image_url
    )
    
    db.add(new_reply)
    db.commit()
    db.refresh(new_reply)
    return new_reply
