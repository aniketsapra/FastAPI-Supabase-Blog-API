# app/main.py

from fastapi import FastAPI
from app.database import Base, engine
from app.models import users
from app.auth import routes as auth_routes
from app.routes import post, comments, upload
from app.services.limiter import limiter  
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

app = FastAPI()

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

Base.metadata.create_all(bind=engine)

app.include_router(auth_routes.router)
app.include_router(post.router)
app.include_router(comments.router)
app.include_router(upload.router)
