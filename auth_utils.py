from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
import bcrypt
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from config import settings
from models import Developer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/Auth/login")

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
        return None

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    verify = verify_token(token)
    if verify is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    user_id = int(verify.get("sub"))
    result = await db.execute(select(Developer).where(user_id == Developer.id).options(selectinload(Developer.games)))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return user