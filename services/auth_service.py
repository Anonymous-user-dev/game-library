from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from fastapi import HTTPException, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Developer
from auth_utils import verify_password, hash_password, create_access_token, verify_token
from schemas.developer import DeveloperResponse, DeveloperCreate
from schemas.auth import Token

def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)

class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_current_user(self, token: str):
        payload = verify_token(token)

        if not payload:
            raise HTTPException(status_code=401, detail="Invalid Credentials")

        user_id = int(payload.get("sub"))
        token_version = payload.get("token_version")

        result = await self.db.execute(select(Developer).where(Developer.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid Credentials")

        if user.token_version != token_version:
            raise HTTPException(status_code=401, detail="Token is no longer valid")

        return user


    async def register_user(self, data: DeveloperCreate) -> DeveloperResponse:

        result = await self.db.execute(
            select(Developer).where(Developer.email == data.email)
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=409, detail="Conflict")
        new_developer = Developer(
            email=data.email,
            username=data.username,
            age=data.age,
            hashed_password=hash_password(data.password),
            is_active=True
        )
        self.db.add(new_developer)
        try:
            await self.db.commit()
            await self.db.refresh(new_developer)
        except SQLAlchemyError:
            await self.db.rollback()
            raise
        return DeveloperResponse(
            id=new_developer.id,
            username=new_developer.username,
            age=new_developer.age,
            games=[]
        )

    async def login(self, data: OAuth2PasswordRequestForm):
        result = await self.db.execute(select(Developer).where(Developer.username == data.username))
        developer_exists = result.scalars().first()
        if not developer_exists:
            raise HTTPException(status_code=401, detail="Invalid Credentials")
        if not verify_password(data.password, developer_exists.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid Credentials")
        token = create_access_token({"sub": str(developer_exists.id),
                                     "token_version": developer_exists.token_version
                                     })
        return {"access_token": token, "token_type": "bearer"}

