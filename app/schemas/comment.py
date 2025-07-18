from pydantic import BaseModel
from datetime import datetime

class CommentCreate(BaseModel):
    comment_text: str

class CommentOut(BaseModel):
    id: int
    post_id: int
    user_id: int
    comment_text: str
    created_at: datetime

    class Config:
        orm_mode = True
