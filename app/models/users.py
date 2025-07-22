from sqlalchemy import Column, String, UUID
import uuid
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, unique=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="user")

    posts = relationship("Post", back_populates="author", cascade="all, delete")
