# app/schemas/post.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PostCreate(BaseModel):
    title: str
    content: str
    image_url: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    image_url: str
    created_at: datetime
    author_id: int

    class Config:
        orm_mode = True

# app/schemas.py

class PostCreate(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None

class PostOut(PostCreate):
    id: int
    author_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CommentOut(BaseModel):
    id: int
    comment_text: str
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class PostDetailOut(PostOut):
    comments: list[CommentOut] = []
