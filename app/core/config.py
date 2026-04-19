# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    REDIS_URL: str = "redis://localhost:6379/1"
    
    class Config:
        env_file = ".env"

settings = Settings()