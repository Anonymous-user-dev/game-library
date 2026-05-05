from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import bcrypt

from jose import jwt, JWTError
import re

from config import settings
from models import PasswordHistory

def validate_password_strength(value: str):
    if len(value) < 12:
        raise ValueError("Password must be at least 12 characters!")
    if not re.search(r"[A-Z]", value):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", value):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", value):
        raise ValueError("Password must contain at least one number")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
        raise ValueError("Password must contain at least one special character")
    return value


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

def verify_password(plain_password, hashed_password) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict) -> str:
    token = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token.update({"exp": expire})
    return jwt.encode(token, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        print("JWT Error: ", e)
        return None

async def check_password_history(user_id: int, new_password: str, db: AsyncSession) -> bool:
    result = await db.execute(
        select(PasswordHistory)
        .where(PasswordHistory.developer_id == user_id)
        .order_by(PasswordHistory.created_at.desc())
        .limit(5)
    )
    old_passwords = result.scalars().all()

    for old in old_passwords:
        if verify_password(new_password, old.hashed_password):
            raise HTTPException(status_code=400, detail="Cannot reuse one of your last 5 passwords.")
    return True
