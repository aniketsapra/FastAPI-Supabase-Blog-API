# app/schemas/post.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class PostCreate(BaseModel):
    title: str
    content: str
    image_url: str

class PostResponse(BaseModel):
    id: UUID
    title: str
    content: str
    image_url: str
    created_at: datetime
    author_id: UUID

    class Config:
        orm_mode = True

# app/schemas.py

class PostCreate(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None

class PostOut(PostCreate):
    id: UUID
    author_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class CommentOut(BaseModel):
    id: UUID
    comment_text: str
    user_id: UUID
    created_at: datetime

    class Config:
        orm_mode = True

class PostDetailOut(PostOut):
    comments: list[CommentOut] = []
