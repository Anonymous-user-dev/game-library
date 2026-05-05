from redis.asyncio import Redis, ConnectionPool
from config import settings

pool = None

async def init_redis():
    global pool 
    pool = ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True, max_connections=10)
async def close_redis():
    await pool.disconnect()


async def get_redis():
    redis = Redis(connection_pool=pool)
    return redis