from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    APP_ENV: str = "development"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str
    SECRET_KEY: str
    class Config:
        env_file = ".env"

settings = Settings()