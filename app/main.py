from fastapi import FastAPI
from app.database import Base, engine
from app.models import users  # Ensure models are imported
from app.auth import routes as auth_routes
from app.routes import post, comments, upload  # <- if you’ve created routes/posts.py

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)

app.include_router(post.router)

app.include_router(comments.router)

app.include_router(upload.router)