from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings

engine = create_async_engine(settings.DATABASE_URL, pool_size=10, max_overflow=20, pool_pre_ping=True)


SessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)
print("FINAL DATABASE URL:", settings.DATABASE_URL)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as db:
        yield db

