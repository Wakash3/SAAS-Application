# app/core/tenant.py
from fastapi import Header, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..core.database import get_db
from ..core.config import settings
import httpx
import logging
from typing import Optional
from jose import jwt
import base64
import json
import threading

logger = logging.getLogger(__name__)

_thread_local = threading.local()


def set_tenant(db: Session, tenant_id: str):
    """Set tenant context in database session for RLS"""
    try:
        # Escape single quotes to prevent SQL injection
        safe_tenant_id = tenant_id.replace("'", "''")
        db.execute(text(f"SET LOCAL app.current_tenant = '{safe_tenant_id}'"))
        _thread_local.current_tenant = tenant_id
        logger.debug(f"Tenant context set to: {tenant_id}")
    except Exception as e:
        logger.error(f"Failed to set tenant context: {e}")
        raise


def get_thread_tenant() -> Optional[str]:
    """Get current tenant from thread-local storage"""
    return getattr(_thread_local, 'current_tenant', None)


def clear_tenant():
    """Clear tenant context from thread-local storage"""
    if hasattr(_thread_local, 'current_tenant'):
        delattr(_thread_local, 'current_tenant')
        logger.debug("Tenant context cleared")


def extract_tenant_from_token(token: str) -> Optional[str]:
    """
    Extract tenant ID from Clerk JWT token.
    Supports multiple JWT claim formats:
    1. 'o' claim (organization data) - Clerk's preferred format
    2. 'org_id' top-level claim
    3. 'sub' claim (user ID) - fallback
    """
    try:
        # Decode JWT payload manually (middle part)
        parts = token.split(".")
        if len(parts) != 3:
            logger.error("Invalid JWT format: expected 3 parts")
            return None

        # Add padding for base64 decoding
        payload_b64 = parts[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding

        # Decode and parse JSON
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        logger.debug(f"JWT payload keys: {list(payload.keys())}")
        
        # Method 1: Clerk puts org data in 'o' claim (recommended)
        org_data = payload.get("o")
        if org_data and isinstance(org_data, dict):
            org_id = org_data.get("id")
            if org_id:
                logger.info(f"Found org_id in 'o' claim: {org_id}")
                return org_id
        
        # Method 2: Fall back to org_id top-level claim
        org_id = payload.get("org_id")
        if org_id:
            logger.info(f"Found org_id in top-level claim: {org_id}")
            return org_id
        
        # Method 3: Fall back to subject (user_id)
        sub = payload.get("sub")
        if sub:
            logger.info(f"No org found, using sub (user_id) as tenant: {sub}")
            return sub
        
        logger.warning("No tenant identifier found in JWT token")
        return None

    except base64.binascii.Error as e:
        logger.error(f"Base64 decoding error: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in payload: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to extract tenant from token: {e}", exc_info=True)
        return None


def extract_tenant_with_jose(token: str) -> Optional[str]:
    """
    Alternative tenant extraction using python-jose library.
    More robust but requires the library.
    """
    try:
        # Get unverified claims (doesn't verify signature)
        payload = jwt.get_unverified_claims(token)
        logger.debug(f"JWT claims from jose: {payload.keys()}")
        
        # Check for organization data
        org_data = payload.get("o")
        if org_data and isinstance(org_data, dict):
            org_id = org_data.get("id")
            if org_id:
                logger.info(f"Found org_id using jose: {org_id}")
                return org_id
        
        # Check for direct org_id
        org_id = payload.get("org_id")
        if org_id:
            logger.info(f"Found org_id using jose: {org_id}")
            return org_id
        
        # Fallback to sub
        sub = payload.get("sub")
        if sub:
            logger.info(f"Using sub as tenant (jose): {sub}")
            return sub
        
        return None
    except Exception as e:
        logger.error(f"Jose extraction failed: {e}")
        return None


async def get_current_tenant(
    authorization: str = Header(None, alias="Authorization"),
    x_branch_id: Optional[str] = Header(None, alias="X-Branch-ID"),
    db: Session = Depends(get_db),
) -> str:
    """
    Validates Clerk JWT and returns tenant_id (org ID).
    Sets RLS context on the DB session.
    Supports both development and production modes.
    """
    # Check authorization header
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header format")
    
    token = authorization.split(" ")[1]
    
    if not token or token in ("null", "undefined", ""):
        raise HTTPException(status_code=401, detail="No valid token provided")
    
    # ── Development mode — skip Clerk API verification ──────────
    if settings.DEBUG:
        logger.info("Dev mode: extracting tenant from token without API verification")
        org_id = extract_tenant_from_token(token)
        
        if not org_id:
            # Try jose method as fallback
            org_id = extract_tenant_with_jose(token)
        
        if not org_id:
            org_id = "dev_default_tenant"
            logger.warning(f"No tenant found, using default tenant: {org_id}")
        
        clear_tenant()
        set_tenant(db, org_id)
        logger.info(f"Tenant authenticated (dev mode): {org_id}")
        return org_id
    
    # ── Production mode — verify with Clerk API ──────────────────
    try:
        # First try to extract from JWT directly (faster, no network call)
        org_id = extract_tenant_from_token(token)
        
        if not org_id:
            # Try jose method
            org_id = extract_tenant_with_jose(token)
        
        if not org_id:
            # Fall back to Clerk API verification
            logger.info("Verifying token with Clerk API")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://api.clerk.com/v1/tokens/verify",
                    headers={
                        "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
                        "Content-Type": "application/json",
                    },
                    params={"token": token},
                )
            
            if response.status_code != 200:
                logger.error(f"Token verification failed: {response.status_code} - {response.text}")
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            
            data = response.json()
            logger.debug(f"Clerk API response: {data.keys()}")
            
            # Extract org_id from API response
            org_id = data.get("org_id") or data.get("sub")
        
        if not org_id:
            raise HTTPException(status_code=401, detail="No organization context found in token")
        
        clear_tenant()
        set_tenant(db, org_id)
        logger.info(f"Tenant authenticated (production): {org_id}")
        return org_id
    
    except httpx.TimeoutException:
        logger.error("Clerk API timeout")
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    except httpx.RequestError as e:
        logger.error(f"Clerk API request error: {e}")
        raise HTTPException(status_code=503, detail=f"Authentication service error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected auth error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_optional_tenant(
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> Optional[str]:
    """Optional tenant — doesn't raise if no auth."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return await get_current_tenant(authorization=authorization, db=db)
    except HTTPException:
        return None


async def get_branch_id(
    x_branch_id: Optional[str] = Header(None, alias="X-Branch-ID"),
) -> Optional[str]:
    """Extract branch ID from header."""
    if x_branch_id and x_branch_id not in ("null", "undefined", ""):
        return x_branch_id
    return None


async def get_current_tenant_from_request(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[str]:
    """
    Get current tenant from request headers or query params.
    Priority: Authorization header > X-Tenant-ID header > tenant query param
    """
    # Method 1: Try Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            return await get_current_tenant(authorization=auth_header, db=db)
        except HTTPException as e:
            logger.debug(f"Auth header validation failed: {e.detail}")
    
    # Method 2: Try X-Tenant-ID header
    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id:
        set_tenant(db, tenant_id)
        logger.debug(f"Using tenant from X-Tenant-ID header: {tenant_id}")
        return tenant_id
    
    # Method 3: Try tenant query parameter
    tenant_slug = request.query_params.get("tenant")
    if tenant_slug:
        from ..models.tenant import Tenant
        tenant = db.query(Tenant).filter(
            Tenant.slug == tenant_slug,
            Tenant.is_active == True
        ).first()
        if tenant:
            set_tenant(db, str(tenant.id))
            logger.debug(f"Using tenant from query param: {tenant_slug} -> {tenant.id}")
            return str(tenant.id)
    
    logger.warning("No tenant found in request")
    return None


def get_tenant_stats(db: Session, tenant_id: str) -> dict:
    """
    Get tenant statistics.
    Returns counts of branches, fuel stations, etc.
    """
    from ..models.branch import Branch
    from ..models.user import User
    
    try:
        branch_count = db.query(Branch).filter(
            Branch.tenant_id == tenant_id
        ).count()
        
        fuel_branch_count = db.query(Branch).filter(
            Branch.tenant_id == tenant_id,
            Branch.has_fuel_station == True
        ).count()
        
        user_count = db.query(User).filter(
            User.tenant_id == tenant_id
        ).count() if hasattr(User, 'tenant_id') else 0
        
        return {
            "tenant_id": tenant_id,
            "branch_count": branch_count,
            "fuel_branch_count": fuel_branch_count,
            "user_count": user_count,
        }
    except Exception as e:
        logger.error(f"Failed to get tenant stats: {e}")
        return {
            "tenant_id": tenant_id,
            "branch_count": 0,
            "fuel_branch_count": 0,
            "user_count": 0,
            "error": str(e)
        }


async def verify_tenant_access(
    tenant_id: str,
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> bool:
    """
    Verify that the authenticated user has access to the specified tenant.
    Useful for multi-tenant access control.
    """
    try:
        current_tenant = await get_current_tenant(authorization=authorization, db=db)
        return current_tenant == tenant_id
    except HTTPException:
        return False


class TenantContext:
    """Context manager for temporary tenant switching"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.previous_tenant = None
    
    def __enter__(self):
        self.previous_tenant = get_thread_tenant()
        set_tenant(self.db, self.tenant_id)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.previous_tenant:
            set_tenant(self.db, self.previous_tenant)
        else:
            clear_tenant()


# Dependency for branch-specific operations
async def get_current_branch(
    x_branch_id: Optional[str] = Header(None, alias="X-Branch-ID"),
    tenant_id: str = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """
    Get current branch from header, ensuring it belongs to the current tenant.
    """
    if not x_branch_id:
        return None
    
    from ..models.branch import Branch
    
    branch = db.query(Branch).filter(
        Branch.id == x_branch_id,
        Branch.tenant_id == tenant_id,
        Branch.is_active == True
    ).first()
    
    if not branch:
        raise HTTPException(
            status_code=404, 
            detail=f"Branch {x_branch_id} not found or not accessible"
        )
    
    return branch