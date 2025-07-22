# app/auth/sync_user.py
from app.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def create_user_from_supabase_token(db: AsyncSession, token_data: dict):
    user_id = token_data["sub"]
    email = token_data["email"]

    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()

    if not db_user:
        new_user = User(id=user_id, email=email)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    return db_user
