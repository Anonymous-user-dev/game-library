from fastapi import FastAPI
from routers import auth, games, developers
from config import settings
app = FastAPI(
)
print("DATABASE URL =", settings.DATABASE_URL)

app.include_router(auth.router)
app.include_router(games.router)
app.include_router(developers.router)