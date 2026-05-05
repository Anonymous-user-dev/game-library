from fastapi import FastAPI
from routers import auth, games, developers
from config import settings
from contextlib import asynccontextmanager
from dependencies.redis import init_redis, close_redis
import logging 


logger = logging.getLogger(__name__)
logging.basicConfig(filename="app.log", encoding="utf-8", level=logging.DEBUG if settings.APP_ENV == "development" else logging.INFO)
logger.info(f"Starting application in {settings.APP_ENV} environment")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()



app = FastAPI(lifespan=lifespan)


app.include_router(auth.router)
app.include_router(games.router)
app.include_router(developers.router)