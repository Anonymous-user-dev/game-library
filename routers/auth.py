from sqlalchemy import select
from sqlalchemy.orm import selectinload

from auth_utils import verify_password, hash_password, create_access_token, get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import Developer
from schemas import DeveloperCreate, DeveloperResponse, Token
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/Auth",
    tags=["Auth"]
)

@router.post("/register", response_model=DeveloperResponse)
async def register(create_developer: DeveloperCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Developer).where(Developer.email == create_developer.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already registered.")
    create_developer = Developer(
        email=create_developer.email,
        username=create_developer.username,
        age=create_developer.age,
        hashed_password=hash_password(create_developer.password),
        is_active=True
    )
    db.add(create_developer)
    await db.commit()

    result = await db.execute(select(Developer).where(Developer.email == create_developer.email).options(selectinload(Developer.games)))
    return result.scalars().first()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Developer).where(Developer.username == form_data.username))
    developer_exists = result.scalars().first()
    if not developer_exists:
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    if not verify_password(form_data.password, developer_exists.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    token = create_access_token({"sub": str(developer_exists.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=DeveloperResponse)
async def me(current_user: Developer = Depends(get_current_user)):
    return current_user

