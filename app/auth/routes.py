from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.user import UserCreate, UserLogin, Token
from app.crud import user as crud_user
from app.auth.jwt import create_access_token
from slowapi import Limiter
from fastapi import Request
from app.services.limiter import limiter 

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=Token)
@limiter.limit("1/minute")
def register(request: Request, data: UserCreate, db: Session = Depends(get_db)):
    existing_user = crud_user.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud_user.create_user(db, data.email, data.password, data.role)
    token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token}

@router.post("/login", response_model=Token)
@limiter.limit("1/minute")
def login(request: Request, data: UserLogin, db: Session = Depends(get_db)):
    user = crud_user.get_user_by_email(db, data.email)
    if not user or not crud_user.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token}
