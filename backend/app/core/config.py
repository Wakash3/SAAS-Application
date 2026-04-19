from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Msingi Retail SaaS"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Neon PostgreSQL — REQUIRED
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30

    # Upstash Redis — REQUIRED
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_BACKEND_URL: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = 10

    # Clerk — REQUIRED
    CLERK_SECRET_KEY: str
    CLERK_WEBHOOK_SECRET: str
    CLERK_API_BASE_URL: str = "https://api.clerk.com/v1"

    # Groq — REQUIRED
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_MAX_TOKENS: int = 600
    GROQ_TEMPERATURE: float = 0.3
    GROQ_TIMEOUT: int = 60

    # M-Pesa — optional with safe defaults
    MPESA_CONSUMER_KEY: str = ""
    MPESA_CONSUMER_SECRET: str = ""
    MPESA_PASSKEY: str = ""
    MPESA_SHORTCODE: str = "174379"
    MPESA_CALLBACK_URL: str = ""
    MPESA_ENVIRONMENT: str = "sandbox"
    MPESA_TIMEOUT: int = 30

    # Stripe — optional with safe defaults
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_API_VERSION: str = "2024-12-18.acacia"
    STRIPE_TIMEOUT: int = 30

    # Cloudflare R2 — fully optional
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_BUCKET_NAME: str = "msingi-files"
    R2_PUBLIC_URL: str = ""
    R2_REGION: str = "auto"

    # Sentry — fully optional
    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1

    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW: int = 60

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://*.msingi.app",
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_HEADERS: list = ["*"]

    # Security
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440
    BCRYPT_ROUNDS: int = 12

    # File Upload
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

    # Helper methods
    def get_celery_backend(self) -> str:
        return self.CELERY_BACKEND_URL or self.REDIS_URL

    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def get_mpesa_api_url(self) -> str:
        if self.MPESA_ENVIRONMENT == "production":
            return "https://api.safaricom.co.ke"
        return "https://sandbox.safaricom.co.ke"

    def get_r2_endpoint(self) -> str:
        if self.R2_ACCOUNT_ID:
            return f"https://{self.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
        return ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def get_groq_config() -> dict:
    return {
        "api_key": settings.GROQ_API_KEY,
        "model": settings.GROQ_MODEL,
        "max_tokens": settings.GROQ_MAX_TOKENS,
        "temperature": settings.GROQ_TEMPERATURE,
        "timeout": settings.GROQ_TIMEOUT,
    }