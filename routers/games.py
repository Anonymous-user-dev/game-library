
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal, get_db
from schemas import GameResponse, GameCreate
from sqlalchemy import select
from models import Game
from fastapi import HTTPException, APIRouter, Depends

router = APIRouter(
    prefix="/games",
    tags=["Games"]
)

@router.post("/post_game", response_model=GameResponse)
async def post_game(create_game: GameCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Game).where(Game.name == create_game.name))
    game = result.scalars().first()
    if game:
        raise HTTPException(status_code=422, detail="Game with this name already exists.")
    db.add(game)
    await db.commit()
    return game
