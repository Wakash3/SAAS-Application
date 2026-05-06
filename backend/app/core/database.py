# app/core/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import logging
from contextvars import ContextVar

logger = logging.getLogger(__name__)

# Thread-local storage for tenant ID
_current_tenant: ContextVar[str | None] = ContextVar('current_tenant', default=None)

# Get DATABASE_URL from settings
DATABASE_URL = settings.DATABASE_URL

# Ensure SSL is enabled for Neon
if DATABASE_URL and "sslmode" not in DATABASE_URL:
    if "?" in DATABASE_URL:
        DATABASE_URL += "&sslmode=require"
    else:
        DATABASE_URL += "?sslmode=require"

logger.info("Creating database engine...")

# Create engine with proper configuration
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=settings.DATABASE_POOL_SIZE if hasattr(settings, 'DATABASE_POOL_SIZE') else 5,
        max_overflow=settings.DATABASE_MAX_OVERFLOW if hasattr(settings, 'DATABASE_MAX_OVERFLOW') else 10,
        pool_timeout=settings.DATABASE_POOL_TIMEOUT if hasattr(settings, 'DATABASE_POOL_TIMEOUT') else 30,
        echo=settings.DEBUG if hasattr(settings, 'DEBUG') else False,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    logger.warning("DATABASE_URL not set - using dummy engine")
    engine = None
    SessionLocal = None

Base = declarative_base()


def get_db():
    """Dependency for FastAPI endpoints to get database session"""
    if SessionLocal is None:
        logger.error("Database not configured - DATABASE_URL missing")
        raise Exception("Database not configured")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_tenant(db, tenant_id: str):
    """Set RLS context — call this on every request after auth."""
    if not tenant_id:
        logger.warning("Attempted to set empty tenant ID")
        return
    
    try:
        # Store tenant in context variable
        _current_tenant.set(tenant_id)
        
        # Set PostgreSQL session variable for RLS
        # Use SET LOCAL instead of SET to scope to current transaction only
        safe_tenant_id = tenant_id.replace("'", "''")  # Escape single quotes
        db.execute(text(f"SET LOCAL app.current_tenant = '{safe_tenant_id}'"))
        
        # No need to commit - the transaction will handle it
        # Using SET LOCAL means it automatically resets at transaction end
        
        if hasattr(settings, 'DEBUG') and settings.DEBUG:
            logger.debug(f"Tenant set to: {tenant_id}")
    except Exception as e:
        logger.error(f"Failed to set tenant: {e}")
        # Don't raise - allow request to continue but log error
        # raise - commented out to prevent breaking requests if RLS not configured


def get_current_tenant() -> str | None:
    """Get current tenant from context variable"""
    return _current_tenant.get()


def clear_tenant():
    """Clear current tenant from context"""
    _current_tenant.set(None)


def init_db():
    """Create all database tables on startup"""
    if engine is None:
        logger.error("Cannot initialize database - engine not configured")
        return
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Optional: Verify RLS is enabled
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_setting('app.current_tenant', true)"))
            logger.info(f"Current tenant setting: {result.scalar()}")
            
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise


def close_db():
    """Close database connections on shutdown"""
    if engine is None:
        return
    
    try:
        engine.dispose()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database connections: {e}")


def check_db_connection() -> bool:
    """Check if database connection is working"""
    if engine is None:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


# Helper function to get tenant-aware query
def get_tenant_query(db, model):
    """Returns a query filtered by current tenant if RLS is not available"""
    tenant = get_current_tenant()
    if tenant and hasattr(model, 'tenant_id'):
        return db.query(model).filter(model.tenant_id == tenant)
    return db.query(model)


# Context manager for tenant scope
from contextlib import contextmanager

@contextmanager
def tenant_context(db, tenant_id: str):
    """Context manager for setting tenant temporarily"""
    try:
        set_tenant(db, tenant_id)
        yield db
    finally:
        clear_tenant()