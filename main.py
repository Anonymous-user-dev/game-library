from fastapi import FastAPI
from routers import auth, games, developers
app = FastAPI(
)

app.include_router(auth.router)
app.include_router(games.router)
app.include_router(developers.router)