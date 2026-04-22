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
from ..core.tenant import get_current_tenant
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

# ==================== HELPER FUNCTIONS ====================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from Clerk token"""
    token = credentials.credentials
    
    try:
        # Decode JWT token (for development - verify signature in production)
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
                first_name=payload.get("first_name", ""),
                last_name=payload.get("last_name", ""),
                avatar_url=payload.get("picture", ""),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
        
    except jwt.PyJWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
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
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    branches = db.query(Branch).filter(Branch.tenant_id == tenant_id).all()
    
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

@router.post("/clerk/webhook")
async def clerk_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook endpoint for Clerk user events
    Clerk sends user.created, user.updated, user.deleted events here
    """
    try:
        payload = await request.json()
        event_type = payload.get("type")
        data = payload.get("data", {})
        
        logger.info(f"Clerk webhook received: {event_type}")
        
        if event_type == "user.created":
            # Create user in your database
            email = data.get("email_addresses", [{}])[0].get("email_address", "")
            user = User(
                clerk_id=data.get("id"),
                email=email,
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                phone_number=data.get("phone_numbers", [{}])[0].get("phone_number", ""),
                avatar_url=data.get("profile_image_url", ""),
            )
            db.add(user)
            db.commit()
            logger.info(f"User created: {user.clerk_id}")
            
        elif event_type == "user.updated":
            # Update user in your database
            user = db.query(User).filter(User.clerk_id == data.get("id")).first()
            if user:
                email = data.get("email_addresses", [{}])[0].get("email_address", user.email)
                user.email = email
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
        "service": "Authentication"
    }

@router.get("/tenant-info")
def get_tenant_info(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    """Get current tenant information without user data"""
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    branches = db.query(Branch).filter(Branch.tenant_id == tenant_id).all()
    
    return {
        "tenant_id": tenant_id,
        "tenant": {
            "name": tenant.name, 
            "plan": tenant.plan,
            "slug": tenant.slug
        } if tenant else None,
        "branches": [
            {
                "id": str(b.id), 
                "name": b.name, 
                "has_fuel": b.has_fuel_station
            } for b in branches
        ],
    }