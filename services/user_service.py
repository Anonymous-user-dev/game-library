import json
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models import Developer
from fastapi import HTTPException
import logging
from schemas.developer import DeveloperResponse, DeveloperCreate
from schemas.game import GameResponse, GameCreate
from models import Game
from redis.asyncio import RedisError

logger = logging.getLogger(__name__)

class DeveloperService:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis

    async def get_developer_by_id(self, user_id: int):
        cache_key = f"developer:{user_id}"

        try:
            cached = await self.redis.get(cache_key)
        except RedisError as e:
            logger.error(f"Redis connection error: {e}")
            cached = None
        if cached:
            logger.debug(f"CACHE HIT for developer: {user_id}")
            return DeveloperResponse(**json.loads(cached))

        
        result = await self.db.execute(select(Developer).where(Developer.id == user_id).options(selectinload(Developer.games)))
        user = result.scalars().first()

        if not user:
            return None
 
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "games": [{"id": game.id, "name": game.name, "genre": game.genre, "price": game.price, "developer_id": game.developer_id} for game in user.games],
            "age": user.age
        }
        try:
            await self.redis.set(cache_key, json.dumps(data), ex=60)
        except RedisError as e:
            logger.error(f"Redis cache error: {e}")

        return DeveloperResponse(**data)

    async def update_developer(self, developer_id: int, create_developer: DeveloperCreate):
        result = await self.db.execute(select(Developer).where(Developer.id == developer_id).options(selectinload(Developer.games)))
        developer = result.scalars().first()

        if not developer:
            return None

        developer.username = create_developer.username
        developer.age = create_developer.age
        developer.email = create_developer.email

        await self.db.commit()

        delete = await self.redis.delete(f"developer:{developer_id}")
        if delete:
            logger.info(f"Developer deleted from cache: {developer_id}")

        return developer
    


class GameService:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis

    async def get_game_by_id(self, game_id: int):
        cache_key = f"game:{game_id}"

        try:
            cached = await self.redis.get(cache_key)
        except RedisError as e: 
            logger.error(f"Redis connection error: {e}")
            cached = None
        if cached:
            logger.debug(f"CACHE HIT for game: {game_id}")
            return GameResponse(**json.loads(cached))
        
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        game = result.scalars().first()
        
        logger.debug(f"CACHE MISS - querying DB for game: {game_id}")
        if not game:
            return None

        data = {
            "id": game.id,
            "genre": game.genre,
            "name": game.name,
            "price": game.price,
            "developer_id": game.developer_id
        }

        try:
            await self.redis.set(cache_key, json.dumps(data), ex=60)
        except RedisError as e:
            logger.error(f"Redis cache error: {e}")

        return GameResponse(**data)
    async def update_game(self, game_id: int, create_game: GameCreate, current_user):
        result = await self.db.execute(select(Game).where(Game.id == game_id))
        game = result.scalars().first()

        if not game:
            raise HTTPException(status_code=404, detail="Not found")

        if game.developer_id != current_user.id:
            raise HTTPException(status_code=403, detail="You are not the owner of this game")

        game.name = create_game.name
        game.genre = create_game.genre
        game.price = create_game.price

        await self.db.commit()

        delete = await self.redis.delete(f"game:{game_id}")
        if delete:
            logger.info(f"Cache with game:{game_id} was deleted")

        return game


        
        


