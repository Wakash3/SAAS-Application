# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import logging
import jwt

from ..core.database import get_db
from ..core.config import settings
from ..core.tenant import get_current_tenant, get_optional_tenant
from ..models.tenant import Tenant
from ..models.branch import Branch
from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

# ==================== PYDANTIC SCHEMAS ====================

class ClerkWebhookData(BaseModel):
    type: str
    data: dict

class UserSyncRequest(BaseModel):
    clerk_id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    clerk_id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True

class TenantInfoResponse(BaseModel):
    tenant_id: str
    tenant: Optional[dict] = None
    branches: list = []

# ==================== HELPER FUNCTIONS ====================

async def verify_clerk_token(token: str) -> dict:
    """Verify Clerk token with Clerk API"""
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
            logger.error(f"Token verification failed: {response.status_code}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return response.json()
    except httpx.TimeoutException:
        logger.error("Clerk API timeout")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from Clerk token"""
    token = credentials.credentials
    
    # Check token is not null
    if not token or token == "null" or token == "undefined":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No valid token provided"
        )
    
    try:
        # First try to verify with Clerk API (production)
        if settings.CLERK_SECRET_KEY and not settings.DEBUG:
            payload = verify_clerk_token(token)
            clerk_user_id = payload.get("sub")
        else:
            # For development, decode without verification
            payload = jwt.decode(token, options={"verify_signature": False})
            clerk_user_id = payload.get("sub")
        
        if not clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Find or create user in your database
        user = db.query(User).filter(User.clerk_id == clerk_user_id).first()
        if not user:
            # Create user if not exists
            user = User(
                clerk_id=clerk_user_id,
                email=payload.get("email", ""),
                first_name=payload.get("first_name", payload.get("given_name", "")),
                last_name=payload.get("last_name", payload.get("family_name", "")),
                avatar_url=payload.get("picture", payload.get("avatar_url", "")),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"User created: {clerk_user_id}")
        
        return user
        
    except jwt.PyJWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

# ==================== AUTH ENDPOINTS ====================

@router.get("/me")
def get_me(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
):
    """Get current user with tenant and branch information"""
    tenant = db.query(Tenant).filter(Tenant.clerk_organization_id == tenant_id).first()
    
    if not tenant:
        logger.warning(f"Tenant not found for organization: {tenant_id}")
        return {
            "user": {
                "id": current_user.id,
                "clerk_id": current_user.clerk_id,
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "avatar_url": current_user.avatar_url,
            },
            "tenant_id": tenant_id,
            "tenant": None,
            "branches": [],
            "message": "Tenant not found. Please create an organization in Clerk."
        }
    
    branches = db.query(Branch).filter(Branch.tenant_id == tenant.id).all()
    
    return {
        "user": {
            "id": current_user.id,
            "clerk_id": current_user.clerk_id,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "avatar_url": current_user.avatar_url,
        },
        "tenant_id": tenant_id,
        "tenant": {
            "id": str(tenant.id),
            "name": tenant.name, 
            "plan": tenant.plan,
            "slug": tenant.slug
        } if tenant else None,
        "branches": [
            {
                "id": str(b.id), 
                "name": b.name, 
                "has_fuel": b.has_fuel_station,
                "location": b.location
            } for b in branches
        ],
    }

@router.get("/me/simple")
def get_me_simple(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    """Simple endpoint to get just tenant info (faster)"""
    tenant = db.query(Tenant).filter(Tenant.clerk_organization_id == tenant_id).first()
    
    return {
        "tenant_id": tenant_id,
        "tenant_name": tenant.name if tenant else None,
        "tenant_slug": tenant.slug if tenant else None,
    }

@router.post("/clerk/webhook")
async def clerk_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook endpoint for Clerk user events
    Clerk sends user.created, user.updated, user.deleted, organization.created events here
    """
    try:
        payload = await request.json()
        event_type = payload.get("type")
        data = payload.get("data", {})
        
        logger.info(f"Clerk webhook received: {event_type}")
        
        if event_type == "user.created":
            # Create user in your database
            email_addresses = data.get("email_addresses", [])
            primary_email = email_addresses[0].get("email_address", "") if email_addresses else ""
            
            phone_numbers = data.get("phone_numbers", [])
            primary_phone = phone_numbers[0].get("phone_number", "") if phone_numbers else ""
            
            user = User(
                clerk_id=data.get("id"),
                email=primary_email,
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                phone_number=primary_phone,
                avatar_url=data.get("profile_image_url", ""),
                is_active=True,
            )
            db.add(user)
            db.commit()
            logger.info(f"User created: {user.clerk_id}")
            
        elif event_type == "user.updated":
            # Update user in your database
            user = db.query(User).filter(User.clerk_id == data.get("id")).first()
            if user:
                email_addresses = data.get("email_addresses", [])
                primary_email = email_addresses[0].get("email_address", user.email) if email_addresses else user.email
                
                user.email = primary_email
                user.first_name = data.get("first_name", user.first_name)
                user.last_name = data.get("last_name", user.last_name)
                user.avatar_url = data.get("profile_image_url", user.avatar_url)
                db.commit()
                logger.info(f"User updated: {user.clerk_id}")
                
        elif event_type == "user.deleted":
            # Soft delete user
            user = db.query(User).filter(User.clerk_id == data.get("id")).first()
            if user:
                user.is_active = False
                db.commit()
                logger.info(f"User deleted: {user.clerk_id}")
        
        elif event_type == "organization.created":
            # Create tenant from organization
            org_id = data.get("id")
            org_name = data.get("name")
            org_slug = data.get("slug")
            
            existing_tenant = db.query(Tenant).filter(Tenant.clerk_organization_id == org_id).first()
            if not existing_tenant:
                tenant = Tenant(
                    clerk_organization_id=org_id,
                    name=org_name,
                    slug=org_slug,
                    plan="starter",
                    is_active=True,
                )
                db.add(tenant)
                db.commit()
                logger.info(f"Tenant created from organization: {org_name} ({org_id})")
            else:
                logger.info(f"Tenant already exists for organization: {org_id}")
        
        return {"status": "received", "event": event_type}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/clerk/sync")
async def sync_clerk_user(
    sync_data: UserSyncRequest,
    db: Session = Depends(get_db)
):
    """Sync Clerk user data to your database"""
    try:
        # Find or create user
        user = db.query(User).filter(User.clerk_id == sync_data.clerk_id).first()
        if not user:
            user = User(
                clerk_id=sync_data.clerk_id,
                email=sync_data.email,
                first_name=sync_data.first_name,
                last_name=sync_data.last_name,
                phone_number=sync_data.phone_number,
                avatar_url=sync_data.avatar_url,
            )
            db.add(user)
        else:
            user.email = sync_data.email
            user.first_name = sync_data.first_name
            user.last_name = sync_data.last_name
            user.phone_number = sync_data.phone_number
            user.avatar_url = sync_data.avatar_url
        
        db.commit()
        db.refresh(user)
        
        return {
            "status": "success",
            "user": {
                "id": user.id,
                "clerk_id": user.clerk_id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
        }
        
    except Exception as e:
        logger.error(f"Sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user
    Note: Actual token invalidation should be handled by Clerk on frontend
    """
    return {"message": "Successfully logged out"}

@router.get("/health")
async def auth_health():
    """Health check for auth service"""
    return {
        "status": "healthy",
        "clerk_configured": bool(settings.CLERK_SECRET_KEY),
        "service": "Authentication",
        "debug_mode": settings.DEBUG
    }

@router.get("/tenant-info")
def get_tenant_info(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
) -> TenantInfoResponse:
    """Get current tenant information without user data"""
    tenant = db.query(Tenant).filter(Tenant.clerk_organization_id == tenant_id).first()
    branches = db.query(Branch).filter(Branch.tenant_id == tenant.id).all() if tenant else []
    
    return TenantInfoResponse(
        tenant_id=tenant_id,
        tenant={
            "id": str(tenant.id),
            "name": tenant.name, 
            "plan": tenant.plan,
            "slug": tenant.slug
        } if tenant else None,
        branches=[
            {
                "id": str(b.id), 
                "name": b.name, 
                "has_fuel": b.has_fuel_station,
                "location": b.location
            } for b in branches
        ],
    )

@router.get("/public-info")
async def public_info(
    tenant_id: Optional[str] = Depends(get_optional_tenant),
):
    """Public endpoint that works even without authentication"""
    return {
        "service": "Msingi Auth API",
        "authenticated": tenant_id is not None,
        "tenant_id": tenant_id,
    }