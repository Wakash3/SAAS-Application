# app/core/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Use the DATABASE_URL as is
DATABASE_URL = settings.DATABASE_URL

# Ensure SSL is enabled for Neon
if "sslmode" not in DATABASE_URL:
    if "?" in DATABASE_URL:
        DATABASE_URL += "&sslmode=require"
    else:
        DATABASE_URL += "?sslmode=require"

logger.info("Creating database engine...")

# Create engine - SQLAlchemy will use psycopg2
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI endpoints to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_tenant(db, tenant_id: str):
    """Set RLS context — call this on every request after auth."""
    try:
        safe_tenant_id = tenant_id.replace("'", "''")
        db.execute(text(f"SET app.current_tenant = '{safe_tenant_id}'"))
        db.execute(text("COMMIT"))
        if settings.DEBUG:
            logger.debug(f"Tenant set to: {tenant_id}")
    except Exception as e:
        logger.error(f"Failed to set tenant: {e}")
        raise


def init_db():
    """Create all database tables on startup"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def close_db():
    """Close database connections on shutdown"""
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")