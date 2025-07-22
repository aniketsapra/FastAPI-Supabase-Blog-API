# app/auth/dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.auth.supabase_auth import verify_supabase_token
from app.auth.sync_user import create_user_from_supabase_token

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
):
    token = credentials.credentials
    token_data = verify_supabase_token(token)
    user = await create_user_from_supabase_token(db, token_data)
    return user

async def get_current_user_role(user = Depends(get_current_user)):
    return getattr(user, "role", "authenticated")

async def require_admin(role: str = Depends(get_current_user_role)):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
