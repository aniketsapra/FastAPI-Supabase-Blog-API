# app/routes/post.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db
from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse, PostOut, PostDetailOut
from app.auth.dependencies import get_current_user, require_admin  # already implemented
from app.models.users import User
from fastapi import Query
from slowapi import Limiter
from fastapi import Request
from app.services.limiter import limiter 

router = APIRouter(tags=["Posts"])

@router.post("/post", response_model=PostResponse, dependencies=[Depends(require_admin)])
@limiter.limit("2/minute")
def create_post(request:Request, post_data: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        image_url=post_data.image_url,
        author_id=current_user.id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/posts", response_model=list[PostOut])
@limiter.limit("5/minute")
def get_posts(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit
    return db.query(Post).order_by(Post.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/posts/{post_id}", response_model=PostDetailOut)
@limiter.limit("5/minute")
def get_post(request: Request, post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/posts/{post_id}", response_model=PostOut)
@limiter.limit("2/minute")
def update_post(
    request: Request,
    post_id: int,
    updated_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")

    for key, value in updated_data.dict().items():
        setattr(post, key, value)
    db.commit()
    db.refresh(post)
    return post


@router.delete("/posts/{post_id}")
@limiter.limit("1/minute")
def delete_post(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}
