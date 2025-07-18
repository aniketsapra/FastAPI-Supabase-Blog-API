# app/routes/comments.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.auth.dependencies import get_current_user
from app.models.users import User
from app.schemas.comment import CommentCreate, CommentOut

router = APIRouter(prefix="/posts", tags=["Comments"])

@router.post("/{post_id}/comment", response_model=CommentOut)
def add_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        comment_text=comment_data.comment_text
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/{post_id}/comments", response_model=list[CommentOut])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.desc()).all()
