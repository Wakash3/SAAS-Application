# test_env_loading.py
from dotenv import load_dotenv
import os
from pathlib import Path

# Find and load .env
env_path = Path(__file__).parent / ".env"
print(f"Looking for .env at: {env_path}")
print(f".env exists: {env_path.exists()}")

if env_path.exists():
    load_dotenv(env_path)
    print("\n✅ .env file loaded successfully!")
    
    # Check critical variables
    critical_vars = [
        'DATABASE_URL',
        'REDIS_URL', 
        'CELERY_BROKER_URL',
        'CLERK_SECRET_KEY',
        'CLERK_WEBHOOK_SECRET',
        'GROQ_API_KEY'
    ]
    
    print("\n" + "=" * 50)
    print("CRITICAL VARIABLES CHECK:")
    print("=" * 50)
    
    all_present = True
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            masked = value[:20] + "..." if len(value) > 20 else value
            print(f"✅ {var}: {masked}")
        else:
            print(f"❌ {var}: MISSING")
            all_present = False
    
    if all_present:
        print("\n🎉 All critical variables are present!")
    else:
        print("\n⚠️ Some variables are missing. Please update your .env file.")
else:
    print("\n❌ .env file NOT found in:", env_path)