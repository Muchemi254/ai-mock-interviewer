# backend/common/config.py
import os
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional

class Settings(BaseSettings):
    # Database - using Field for better validation and defaults
    database_url: str = Field(
        default=os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_interviewer"),
        description="PostgreSQL database URL (can use asyncpg or psycopg2)"
    )
    
    # Property to get sync URL for migrations
    @property
    def sync_database_url(self) -> str:
        """Convert to synchronous database URL for Alembic migrations"""
        if self.database_url.startswith("postgresql+asyncpg://"):
            return self.database_url.replace("postgresql+asyncpg://", "postgresql://")
        elif self.database_url.startswith("postgresql+psycopg2://"):
            return self.database_url  # Already sync
        else:
            # Handle other cases - ensure it starts with postgresql://
            if self.database_url.startswith("postgresql://"):
                return self.database_url
            # Extract the part after :// and prepend with postgresql://
            return f"postgresql://{self.database_url.split('://')[1]}"

    # Redis
    redis_url: str = Field(
        default=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        description="Redis connection URL"
    )

    # JWT
    jwt_secret_key: str = Field(
        default=os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production"),
        description="JWT secret key for token signing"
    )
    
    jwt_algorithm: str = Field(
        default=os.getenv("JWT_ALGORITHM", "HS256"),
        description="JWT algorithm for token signing"
    )
    
    jwt_access_token_expire_minutes: int = Field(
        default=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        description="Access token expiration time in minutes"
    )

    # LLM
    gemini_api_key: str = Field(
        default=os.getenv("GEMINI_API_KEY", ""),
        description="Google Gemini API key for AI capabilities"
    )
    
    # OpenAI (for future use)
    openai_api_key: str = Field(
        default=os.getenv("OPENAI_API_KEY", ""),
        description="OpenAI API key for alternative AI capabilities"
    )

    # CORS origins
    cors_origins: list[str] = Field(
        default=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
        description="Allowed CORS origins"
    )

    # Validator to ensure database URL is properly formatted
    @validator('database_url')
    def validate_database_url(cls, v):
        if not v.startswith(('postgresql://', 'postgresql+asyncpg://', 'postgresql+psycopg2://')):
            raise ValueError('Database URL must start with postgresql://, postgresql+asyncpg://, or postgresql+psycopg2://')
        return v

    # Validator to ensure JWT secret is not default in production
    @validator('jwt_secret_key')
    def validate_jwt_secret(cls, v, values):
        if v == "your-super-secret-jwt-key-change-in-production" and os.getenv("ENVIRONMENT") == "production":
            raise ValueError("JWT secret key must be changed in production environment")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True
        # Allow extra environment variables without throwing errors
        extra = "ignore"

settings = Settings()