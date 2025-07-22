from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class CommentCreate(BaseModel):
    post_id: UUID
    comment_text: str

class CommentOut(BaseModel):
    id: UUID
    post_id: UUID
    user_id: UUID
    comment_text: str
    created_at: datetime

    class Config:
        orm_mode = True