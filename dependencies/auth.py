from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from dependencies.redis import get_redis
from fastapi import HTTPException
from services.auth_service import AuthService, get_auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.get_user_by_token(token)

async def verify_blacklisted_token(token: str = Depends(oauth2_scheme), redis = Depends(get_redis)):
    blacklisted = await redis.get(f"blacklist:{token}")

    if blacklisted:
        raise HTTPException(status_code=401, detail="Token revoked")
    return token