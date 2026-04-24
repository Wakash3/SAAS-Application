from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db, set_tenant, get_current_tenant, clear_tenant
import httpx
from .config import settings
import logging

logger = logging.getLogger(__name__)


async def get_current_tenant(
    authorization: str = Header(...),
    x_branch_id: str = Header(None),
    db: Session = Depends(get_db),
) -> str:
    """
    Validates Clerk JWT and returns tenant_id (org ID).
    Sets RLS context on the DB session.
    """
    # Check authorization header exists and is valid
    if not authorization:
        logger.warning("Missing authorization header")
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        logger.warning("Invalid auth header format")
        raise HTTPException(status_code=401, detail="Invalid auth header format")

    token = authorization.split(" ")[1]
    
    # Check token is not null or empty
    if not token or token == "null" or token == "undefined":
        logger.warning("Token is null or empty")
        raise HTTPException(status_code=401, detail="No valid token provided")

    # Verify token with Clerk API
    try:
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
        logger.debug(f"Token verification successful. Data: {data}")
        
        # Extract organization ID or fall back to user ID
        org_id = data.get("org_id") or data.get("sub")
        
        if not org_id:
            logger.error("No organization ID or user ID found in token")
            raise HTTPException(status_code=401, detail="No organization context found")

        # Clear any existing tenant context first
        clear_tenant()
        
        # Set tenant in database session for RLS
        set_tenant(db, org_id)
        
        # Verify tenant was set correctly
        current_tenant = get_current_tenant()
        logger.info(f"Tenant authenticated: {org_id} (context verified: {current_tenant == org_id})")
        
        return org_id

    except httpx.TimeoutException:
        logger.error("Clerk API timeout - authentication service unavailable")
        raise HTTPException(status_code=503, detail="Authentication service temporarily unavailable")
    except httpx.RequestError as e:
        logger.error(f"Clerk API request error: {str(e)}")
        raise HTTPException(status_code=503, detail="Authentication service error")
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")


async def get_optional_tenant(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> str | None:
    """
    Optional tenant resolution - doesn't raise exception if no auth.
    Useful for public endpoints.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        return await get_current_tenant(authorization=authorization, db=db)
    except HTTPException:
        return None


async def get_branch_id(
    x_branch_id: str = Header(None),
) -> str | None:
    """
    Extract branch ID from header if present.
    """
    if x_branch_id and x_branch_id != "null" and x_branch_id != "undefined":
        logger.debug(f"Branch ID from header: {x_branch_id}")
        return x_branch_id
    return None