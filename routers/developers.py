from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from dependencies.redis import get_redis
from services.user_service import DeveloperService

from dependencies.auth import get_current_user
from database import get_db
from schemas.developer import DeveloperResponse, DeveloperCreate
from sqlalchemy import select
from models import Developer
from fastapi import HTTPException, APIRouter, Depends

router = APIRouter(
    prefix="/developer",
    tags=["Developers"]
)

@router.get("/get_developers", response_model=list[DeveloperResponse])
async def get_developers_name(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Developer).options(selectinload(Developer.games)))
    developers = result.scalars().all()
    return developers

@router.get("/get_developer/{developer_id}", response_model=DeveloperResponse)
async def get_developer_by_id(developer_id: int, db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    service = DeveloperService(db, redis)

    developer = await service.get_developer_by_id(developer_id)
    if not developer:
        raise HTTPException(status_code=404, detail="not found")
    return developer

@router.delete("/delete_developer/{developer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_developer(developer_id: int, db: AsyncSession = Depends(get_db), current_user: Developer = Depends(get_current_user)):
    result = await db.execute(select(Developer).where(Developer.id == developer_id))
    dev = result.scalars().first()
    if not dev:
        raise HTTPException(status_code=404, detail="Developer with this id does not exist.")

    await db.delete(dev)
    await db.commit()   

@router.put("/update_developer/{developer_id}", response_model=DeveloperResponse)
async def update_developer(developer_id: int, developer_create: DeveloperCreate, db: AsyncSession = Depends(get_db), current_user: Developer = Depends(get_current_user), redis=Depends(get_redis)):
    service = DeveloperService(db, redis)

    dev = await service.update_developer(developer_id, developer_create)

    return dev


