import os
import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.models.users import User
from app.services.limiter import limiter
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

@router.post("/register", response_model=Token)
@limiter.limit("2/minute")
async def register(
    request: Request,
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    # 1. Create user in Supabase
    res = requests.post(
        f"{SUPABASE_URL}/auth/v1/admin/users",
        headers=headers,
        json={
            "email": data.email,
            "password": data.password,
            "email_confirm": True
        }
    )

    try:
        res_data = res.json()
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid JSON response from Supabase")

    if res.status_code not in (200, 201):
        message = res_data.get("msg") or res_data.get("message") or res_data.get("error_description") or "Unknown Supabase error"
        raise HTTPException(status_code=res.status_code, detail=message)

    # 2. Extract Supabase user ID
    supabase_user = res_data
    user_id = supabase_user.get("id")
    if not user_id:
        raise HTTPException(status_code=500, detail=f"No user ID found in response: {res_data}")

    # 3. Save to your local DB
    new_user = User(
        id=user_id,
        email=data.email,
        role=data.role  # role from UserCreate (default "user")
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 4. Return access token (you may want to implement a real token generation here)
    return {
        "access_token": "registered_successfully",  # Placeholder
        "token_type": "bearer"
    }


@router.post("/login", response_model=Token)
@limiter.limit("3/minute")
async def login(request: Request, data: UserLogin):
    # Supabase login to get JWT token
    res = requests.post(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        headers=headers,
        json={
            "email": data.email,
            "password": data.password
        }
    )

    try:
        res_data = res.json()
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid response from Supabase")

    if res.status_code != 200:
        message = res_data.get("msg") or res_data.get("message") or res_data.get("error") or "Login failed"
        raise HTTPException(status_code=401, detail=message)

    return {"access_token": res_data["access_token"]}
