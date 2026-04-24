import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # App
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    SENTRY_DSN = os.getenv("SENTRY_DSN", "")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/db")
    
    # M-Pesa
    MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "")
    
    # Clerk
    CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "")
    CLERK_API_BASE_URL = os.getenv("CLERK_API_BASE_URL", "https://api.clerk.com/v1")

settings = Settings()
