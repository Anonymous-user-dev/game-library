from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, Depends

from database import get_db
from models import Developer
from auth_utils import (
    verify_password,
    hash_password,
    create_access_token,
    verify_token,
)

from schemas.developer import DeveloperCreate, DeveloperResponse
from schemas.auth import Token

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def register_user(self, data: DeveloperCreate) -> DeveloperResponse:

        result = await self.db.execute(
            select(Developer).where(Developer.email == data.email)
        )
        existing_user = result.scalars().first()

        if existing_user:
            raise HTTPException(status_code=409, detail="Email already exists")

        new_user = Developer(
            email=data.email,
            username=data.username,
            age=data.age,
            hashed_password=hash_password(data.password),
            is_active=True,
        )

        self.db.add(new_user)

        try:
            await self.db.commit()
            await self.db.refresh(new_user)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        return DeveloperResponse(
            id=new_user.id,
            username=new_user.username,
            age=new_user.age,
            games=[]
        )

    async def login(self, data) -> Token:
        result = await self.db.execute(
            select(Developer).where(Developer.username == data.username)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({
            "sub": str(user.id),
            "token_version": user.token_version
        })

        return Token(
            access_token=token,
            token_type="bearer"
        )


    async def get_user_by_token(self, token: str) -> Developer:
    
        payload = verify_token(token)

        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_id = payload.get("sub")
        token_version = payload.get("token_version")

        if not user_id or token_version is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        
        result = await self.db.execute(
            select(Developer).where(Developer.id == int(user_id))
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")


        if user.token_version != token_version:
            raise HTTPException(status_code=401, detail="Token expired")

        return user