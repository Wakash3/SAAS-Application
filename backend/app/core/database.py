from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Neon requires SSL — add sslmode=require if not already in URL
DATABASE_URL = settings.DATABASE_URL
if "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_tenant(db, tenant_id: str):
    """Set RLS context — call this on every request after auth."""
    db.execute(text(f"SET app.current_tenant = '{tenant_id}'"))
    db.execute(text("COMMIT"))