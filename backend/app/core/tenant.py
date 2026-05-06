from fastapi import Header, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..core.database import get_db
from ..core.config import settings
import httpx
import logging
from typing import Optional
from jose import jwt

logger = logging.getLogger(__name__)

import threading
_thread_local = threading.local()


def set_tenant(db: Session, tenant_id: str):
    """Set tenant context in database session for RLS"""
    try:
        db.execute(text(f"SET app.current_tenant = '{tenant_id}'"))
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
    Clerk stores org info in the 'o' claim.
    """
    try:
        payload = jwt.get_unverified_claims(token)
        logger.debug(f"JWT claims: {payload}")

        # Clerk puts org data in 'o' claim
        org_data = payload.get("o")
        if org_data and isinstance(org_data, dict):
            org_id = org_data.get("id")
            if org_id:
                logger.debug(f"Found org_id in 'o' claim: {org_id}")
                return org_id

        # Fall back to org_id top-level claim
        org_id = payload.get("org_id")
        if org_id:
            logger.debug(f"Found org_id in top-level claim: {org_id}")
            return org_id

        # Fall back to subject (user_id)
        sub = payload.get("sub")
        if sub:
            logger.debug(f"No org found, using sub: {sub}")
            return sub

        return None

    except Exception as e:
        logger.error(f"Failed to extract tenant from token: {e}")
        return None


async def get_current_tenant(
    authorization: str = Header(None, alias="Authorization"),
    x_branch_id: Optional[str] = Header(None, alias="X-Branch-ID"),
    db: Session = Depends(get_db),
) -> str:
    """
    Validates Clerk JWT and returns tenant_id (org ID).
    Sets RLS context on the DB session.
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
            org_id = "dev_default_tenant"
            logger.warning(f"Using default tenant: {org_id}")

        clear_tenant()
        set_tenant(db, org_id)
        logger.info(f"Tenant authenticated (dev): {org_id}")
        return org_id

    # ── Production mode — verify with Clerk API ──────────────────
    try:
        # First try to extract from JWT directly (faster)
        org_id = extract_tenant_from_token(token)

        if not org_id:
            # Fall back to Clerk API verification
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
                logger.error(f"Token verification failed: {response.status_code}")
                raise HTTPException(status_code=401, detail="Invalid or expired token")

            data = response.json()
            org_id = data.get("org_id") or data.get("sub")

        if not org_id:
            raise HTTPException(status_code=401, detail="No organization context found")

        clear_tenant()
        set_tenant(db, org_id)
        logger.info(f"Tenant authenticated: {org_id}")
        return org_id

    except httpx.TimeoutException:
        raise HTTPException(status_code=503, detail="Authentication service unavailable")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Authentication service error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected auth error: {str(e)}")
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
    if x_branch_id and x_branch_id not in ("null", "undefined"):
        return x_branch_id
    return None


async def get_current_tenant_from_request(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[str]:
    """Get current tenant from request headers."""
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            return await get_current_tenant(authorization=auth_header, db=db)
        except HTTPException:
            pass

    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id:
        set_tenant(db, tenant_id)
        return tenant_id

    tenant_slug = request.query_params.get("tenant")
    if tenant_slug:
        from ..models.tenant import Tenant
        tenant = db.query(Tenant).filter(
            Tenant.slug == tenant_slug,
            Tenant.is_active == True
        ).first()
        if tenant:
            set_tenant(db, str(tenant.id))
            return str(tenant.id)

    return None


def get_tenant_stats(db: Session, tenant_id: str) -> dict:
    """Get tenant statistics."""
    from ..models.branch import Branch
    branch_count = db.query(Branch).filter(
        Branch.tenant_id == tenant_id
    ).count()
    fuel_branch_count = db.query(Branch).filter(
        Branch.tenant_id == tenant_id,
        Branch.has_fuel_station == True
    ).count()
    return {
        "branch_count": branch_count,
        "fuel_branch_count": fuel_branch_count,
        "tenant_id": tenant_id,
    }