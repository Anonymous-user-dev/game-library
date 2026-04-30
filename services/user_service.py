import json
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models import Developer
from schemas.developer import DeveloperResponse

class DeveloperService:
    def __init__(self, db, redis):
        self.db = db
        self.redis = redis

    async def get_developer_by_id(self, user_id: int):
        cache_key = f"developer:{user_id}"

        try:
            cached = await self.redis.get(cache_key)
        except Exception:
            cached = None
        if cached:
            return json.loads(cached)
        
        result = await self.db.execute(select(Developer).where(Developer.id == user_id).options(selectinload(Developer.games)))
        user = result.scalars().first()

        if not user:
            return None
        
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
        try:
            await self.redis.set(cache_key, json.dumps(data), ex=60)
        except Exception as e:
            print("Redis cache error: ", e)

        return DeveloperResponse(**data)


