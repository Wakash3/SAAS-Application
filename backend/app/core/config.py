import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # App
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    APP_NAME = os.getenv("APP_NAME", "Msingi Retail SaaS")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "")
    CELERY_BACKEND_URL = os.getenv("CELERY_BACKEND_URL", "")
    REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
    
    # Clerk
    CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "")
    CLERK_WEBHOOK_SECRET = os.getenv("CLERK_WEBHOOK_SECRET", "")
    CLERK_API_BASE_URL = os.getenv("CLERK_API_BASE_URL", "https://api.clerk.com/v1")
    CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY", "")
    
    # Groq
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "600"))
    GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.3"))
    GROQ_TIMEOUT = int(os.getenv("GROQ_TIMEOUT", "60"))
    
    # M-Pesa
    MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "")
    MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "")
    MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "")
    MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")
    MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "")
    MPESA_ENVIRONMENT = os.getenv("MPESA_ENVIRONMENT", "sandbox")
    MPESA_TIMEOUT = int(os.getenv("MPESA_TIMEOUT", "30"))
    
    # INTASEND
    INTASEND_PUBLISHABLE_KEY = os.getenv("INTASEND_PUBLISHABLE_KEY", "")
    INTASEND_SECRET_KEY = os.getenv("INTASEND_SECRET_KEY", "")
    INTASEND_ENVIRONMENT = os.getenv("INTASEND_ENVIRONMENT", "sandbox")
    INTASEND_API_URL = os.getenv("INTASEND_API_URL", "https://sandbox.intasend.com/api/")
    
    # Cloudflare R2
    R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "")
    R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY", "")
    R2_SECRET_KEY = os.getenv("R2_SECRET_KEY", "")
    R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "msingi-files")
    R2_PUBLIC_URL = os.getenv("R2_PUBLIC_URL", "")
    R2_REGION = os.getenv("R2_REGION", "auto")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    # File Upload
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", ".jpg,.jpeg,.png,.pdf,.doc,.docx").split(",")
    
    # Helper methods
    def get_celery_backend(self) -> str:
        return self.CELERY_BACKEND_URL or self.REDIS_URL
    
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    def get_mpesa_api_url(self) -> str:
        if self.MPESA_ENVIRONMENT == "production":
            return "https://api.safaricom.co.ke"
        return "https://sandbox.safaricom.co.ke"
    
    def get_intasend_api_url(self) -> str:
        if self.INTASEND_ENVIRONMENT == "production":
            return "https://payment.intasend.com/api/"
        return "https://sandbox.intasend.com/api/"
    
    def get_r2_endpoint(self) -> str:
        if self.R2_ACCOUNT_ID:
            return f"https://{self.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
        return ""


settings = Settings()

# Debug: Print which variables are loaded (remove in production)
if settings.DEBUG:
    print("\n" + "=" * 50)
    print("ENVIRONMENT VARIABLES LOADED:")
    print("=" * 50)
    print(f"DATABASE_URL: {'✅' if settings.DATABASE_URL else '❌'}")
    print(f"DATABASE_POOL_SIZE: {settings.DATABASE_POOL_SIZE}")
    print(f"DATABASE_MAX_OVERFLOW: {settings.DATABASE_MAX_OVERFLOW}")
    print(f"CLERK_SECRET_KEY: {'✅' if settings.CLERK_SECRET_KEY else '❌'}")
    print(f"CLERK_WEBHOOK_SECRET: {'✅' if settings.CLERK_WEBHOOK_SECRET else '❌'}")
    print(f"GROQ_API_KEY: {'✅' if settings.GROQ_API_KEY else '❌'}")
    print("=" * 50 + "\n")