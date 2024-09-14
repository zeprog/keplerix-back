from pydantic_settings import BaseSettings  # Импортируем из pydantic-settings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME", "Keplerix")
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DATABASE_URL_ASYNC: str = os.getenv("DATABASE_URL_ASYNC")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    # ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    # REDIS_URL: str = os.getenv("REDIS_URL")

    class Config:
        env_file = ".env"

settings = Settings()