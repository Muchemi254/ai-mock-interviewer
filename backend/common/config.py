# backend/common/config.py
import os
from pydantic_settings import BaseSettings # Requires pydantic-settings

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your_default_secret_key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_access_token_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    # LLM
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    # openai_api_key: str = os.getenv("OPENAI_API_KEY", "") # For future

    class Config:
        env_file = ".env" # Load from .env file in the directory where the app runs

settings = Settings()