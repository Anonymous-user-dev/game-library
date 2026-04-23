
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth_utils import get_current_user
from database import get_db
from schemas import GameResponse, GameCreate
from sqlalchemy import select
from models import Game, Developer
from fastapi import HTTPException, APIRouter, Depends

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)

@router.post("/post_game", response_model=GameResponse)
async def post_game(create_game: GameCreate, db: AsyncSession = Depends(get_db), current_user: Developer = Depends(get_current_user)):
    new_game = Game(**create_game.model_dump())
    db.add(new_game)
    await db.commit()
    await db.refresh(new_game)
    return new_game


@router.get("/get_games", response_model=list[GameResponse])
async def get_all_games(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Game))
    return result.scalars().all()

@router.get("/{game_id}", response_model=GameResponse)
async def get_game_by_id(game_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalars().first()
    if not game:
        raise HTTPException(status_code=404, detail="Not found")
    return game

@router.put("/{game_id}", response_model=GameResponse)
async def update_game(game_id: int, create_game: GameCreate, db: AsyncSession = Depends(get_db), current_user: Developer = Depends(get_current_user)):
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalars().first()
    if not game:
        raise HTTPException(status_code=404, detail="Not found")

    game.name = create_game.name
    game.genre = create_game.genre
    game.price = create_game.price
    game.developer_id = create_game.developer_id

    await db.commit()
    await db.refresh(game)
    return game

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_by_id(game_id: int, db: AsyncSession = Depends(get_db), current_user: Developer = Depends(get_current_user)):
    result = await db.execute(select(Game).where(Game.id == game_id))
    game = result.scalars().first()
    if not game:
        raise HTTPException(status_code=404, detail="Not found")

    await db.delete(game)
    await db.commit()
