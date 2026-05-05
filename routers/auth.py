from sqlalchemy import select, delete


from auth_utils import verify_password, hash_password, check_password_history
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies.auth import get_current_user, oauth2_scheme
from database import get_db
from dependencies.redis import get_redis
from config import settings
from models import Developer, PasswordHistory
from schemas.developer import DeveloperCreate, DeveloperResponse
from schemas.auth import Token, ChangePasswordRequest
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from dependencies.auth import verify_blacklisted_token
from services.auth_service import AuthService, get_auth_service, blacklist_token


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", response_model=DeveloperResponse)
async def register(data: DeveloperCreate, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.register_user(data)


@router.post("/login", response_model=Token)
async def login_user(data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.login(data)



@router.post("/change-password")
async def change_password(change_current_password: ChangePasswordRequest, db: AsyncSession = Depends(get_db), current_user: Developer = Depends(get_current_user)):

    if not verify_password(change_current_password.current_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")

    await check_password_history(user_id=current_user.id,
                                 new_password=change_current_password.new_password,
                                 db=db)
    old_entry = PasswordHistory(
        developer_id=current_user.id,
        hashed_password=current_user.hashed_password
    )
    db.add(old_entry)
    current_user.hashed_password = hash_password(change_current_password.new_password)
    current_user.token_version += 1
    rows = await db.execute(select(PasswordHistory).where(PasswordHistory.developer_id == current_user.id).order_by(PasswordHistory.created_at.desc()).offset(5))
    passwords = rows.scalars().all()
    ids = [password.id for password in passwords]
    if ids:
        await db.execute(delete(PasswordHistory).where(PasswordHistory.id.in_(ids)))

    await db.commit()


    return {"message": "Password changed successfully."}



@router.get("/me", response_model=DeveloperResponse)
async def me(current_user: Developer = Depends(get_current_user)):
    return current_user

@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme), redis = Depends(get_redis)):
    await blacklist_token(redis, token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return {"message": "Logged out"}

@router.get("/profile")
async def profile(token=Depends(verify_blacklisted_token), current_user: Developer = Depends(get_current_user)):
    return current_user