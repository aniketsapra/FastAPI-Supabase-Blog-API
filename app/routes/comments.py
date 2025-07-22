from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.comment import Comment
from app.models.post import Post
from app.auth.dependencies import get_current_user, require_admin
from app.models.users import User
from app.schemas.comment import CommentCreate, CommentOut
from app.services.limiter import limiter
from uuid import UUID


router = APIRouter(tags=["Comments"])

@router.post("/comments", response_model=CommentOut)
@limiter.limit("5/minute")
async def add_comment(
    request: Request,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Post).where(Post.id == comment_data.post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(
        post_id=comment_data.post_id,
        user_id=current_user.id,
        comment_text=comment_data.comment_text
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


@router.get("/posts/{post_id}/comments", response_model=list[CommentOut], dependencies=[Depends(require_admin)])
@limiter.limit("5/minute")
async def get_comments(
    request: Request,
    post_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    result = await db.execute(
        select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.desc())
    )
    return result.scalars().all()
