
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from dependencies.auth import get_current_user
from database import get_db
from schemas.game import GameResponse, GameCreate
from sqlalchemy import select
from models import Game, Developer
from services.user_service import GameService
from dependencies.auth import get_redis
from fastapi import HTTPException, APIRouter, Depends

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)

@router.post("/post_game", response_model=GameResponse)
async def post_game(create_game: GameCreate, db: AsyncSession = Depends(get_db), current_user: Developer = Depends(get_current_user)):
    new_game = Game(
        name=create_game.name,
        genre=create_game.genre,
        price=create_game.price,
        developer_id=current_user.id
    )
    db.add(new_game)
    await db.commit()
    await db.refresh(new_game)
    return GameResponse.model_validate(new_game)


@router.get("/get_games", response_model=list[GameResponse])
async def get_all_games(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Game))
    return result.scalars().all()

@router.get("/{game_id}", response_model=GameResponse)
async def get_game_by_id(game_id: int, db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    service = GameService(db, redis)
    game = await service.get_game_by_id(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Not found")
    return game

@router.put("/{game_id}", response_model=GameResponse)
async def update_game(game_id: int, create_game: GameCreate, db: AsyncSession = Depends(get_db), current_user: Developer = Depends(get_current_user), redis=Depends(get_redis)):
    service = GameService(db, redis)

    game = await service.update_game(game_id, create_game, current_user)

    return game

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(game_id: int, db: AsyncSession = Depends(get_db), current_user: Developer = Depends(get_current_user)):
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalars().first()
    if not game:
        raise HTTPException(status_code=404, detail="Not found")
    
    if game.developer_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not the owner of this game")

    await db.delete(game)
    await db.commit()
