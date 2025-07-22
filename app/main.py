# app/main.py

from fastapi import FastAPI
from app.database import async_engine, Base
from app.routes import post, comments, upload, auth
from app.services.limiter import limiter  
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


app.include_router(auth.router)
app.include_router(post.router)
app.include_router(comments.router)
app.include_router(upload.router)

