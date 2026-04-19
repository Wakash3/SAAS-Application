from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Msingi Retail SaaS"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # Neon PostgreSQL
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    DATABASE_POOL_TIMEOUT: int = 30

    # Upstash Redis
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_BACKEND_URL: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = 10

    # Clerk
    CLERK_SECRET_KEY: str
    CLERK_WEBHOOK_SECRET: str
    CLERK_API_BASE_URL: str = "https://api.clerk.com/v1"

    # Groq (Gladwell) — BACKEND ONLY
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"  # or "llama3-70b-8192", "mixtral-8x7b-32768"
    GROQ_MAX_TOKENS: int = 600
    GROQ_TEMPERATURE: float = 0.3
    GROQ_TIMEOUT: int = 60

    # M-Pesa
    MPESA_CONSUMER_KEY: str
    MPESA_CONSUMER_SECRET: str
    MPESA_PASSKEY: str
    MPESA_SHORTCODE: str
    MPESA_CALLBACK_URL: str
    MPESA_ENVIRONMENT: str = "sandbox"  # sandbox or production
    MPESA_TIMEOUT: int = 30

    # Stripe
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_API_VERSION: str = "2024-12-18.acacia"
    STRIPE_TIMEOUT: int = 30

    # Cloudflare R2 (optional — defaults provided)
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_BUCKET_NAME: str = "msingi-files"
    R2_PUBLIC_URL: str = ""
    R2_REGION: str = "auto"

    # Sentry (optional)
    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "https://*.msingi.app"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_HEADERS: list = ["*"]

    # Security
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 hours
    BCRYPT_ROUNDS: int = 12

    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # ignore unknown vars like NEXT_PUBLIC_* in .env

    def get_redis_url(self) -> str:
        """Get Redis URL with default if not set"""
        return self.REDIS_URL or self.CELERY_BROKER_URL

    def get_celery_backend(self) -> str:
        """Get Celery backend URL"""
        return self.CELERY_BACKEND_URL or self.REDIS_URL

    def is_production(self) -> bool:
        """Check if environment is production"""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if environment is development"""
        return self.ENVIRONMENT == "development"

    def get_mpesa_api_url(self) -> str:
        """Get M-Pesa API URL based on environment"""
        if self.MPESA_ENVIRONMENT == "production":
            return "https://api.safaricom.co.ke"
        return "https://sandbox.safaricom.co.ke"

    def get_r2_endpoint(self) -> str:
        """Get Cloudflare R2 endpoint"""
        if self.R2_ACCOUNT_ID:
            return f"https://{self.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
        return ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create a single instance for import
settings = get_settings()


# Helper functions for common settings
def get_database_url() -> str:
    """Get database URL for SQLAlchemy"""
    return settings.DATABASE_URL


def is_debug_mode() -> bool:
    """Check if debug mode is enabled"""
    return settings.DEBUG


def get_groq_config() -> dict:
    """Get Groq configuration as dictionary"""
    return {
        "api_key": settings.GROQ_API_KEY,
        "model": settings.GROQ_MODEL,
        "max_tokens": settings.GROQ_MAX_TOKENS,
        "temperature": settings.GROQ_TEMPERATURE,
        "timeout": settings.GROQ_TIMEOUT,
    }