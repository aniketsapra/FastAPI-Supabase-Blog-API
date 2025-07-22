from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.post import Post
from app.schemas.post import PostCreate, PostResponse, PostOut, PostDetailOut
from app.auth.dependencies import get_current_user, require_admin
from app.models.users import User
from app.services.limiter import limiter
from uuid import UUID
from sqlalchemy.orm import selectinload
from typing import List

router = APIRouter(tags=["Posts"])

@router.post("/post", response_model=PostResponse)
@limiter.limit("2/minute")
async def create_post(
    request: Request,
    post_data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_admin)
):
    new_post = Post(
        title=post_data.title,
        content=post_data.content,
        image_url=post_data.image_url,
        author_id=current_user.id
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post

@router.get("/posts/{post_id}", response_model=PostDetailOut)
@limiter.limit("5/minute")
async def get_post(request: Request, post_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.comments))  
        .where(Post.id == post_id)
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.get("/posts", response_model=List[PostDetailOut])
@limiter.limit("5/minute")
async def get_all_posts(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Post).options(selectinload(Post.comments), selectinload(Post.author))
    )
    posts = result.scalars().all()
    return posts


@router.put("/posts/{post_id}", response_model=PostOut)
@limiter.limit("2/minute")
async def update_post(
    request: Request,
    post_id: UUID,
    updated_data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _ = Depends(require_admin)
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")

    for key, value in updated_data.dict().items():
        setattr(post, key, value)
    await db.commit()
    await db.refresh(post)
    return post


@router.delete("/posts/{post_id}")
@limiter.limit("1/minute")
async def delete_post(
    request: Request,
    post_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    await db.delete(post)
    await db.commit()
    return {"message": "Post deleted successfully"}
