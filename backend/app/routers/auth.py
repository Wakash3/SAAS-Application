# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import httpx
import logging
import jwt
import base64
import json

from ..core.database import get_db, get_current_tenant
from ..core.config import settings
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

class TokenValidationRequest(BaseModel):
    token: str

# ==================== HELPER FUNCTIONS ====================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from Clerk token"""
    token = credentials.credentials
    
    try:
        # Verify token with Clerk (in production)
        if settings.CLERK_SECRET_KEY:
            # For production - verify signature
            payload = jwt.decode(
                token, 
                settings.CLERK_SECRET_KEY,
                algorithms=["RS256"],
                options={"verify_aud": False}
            )
        else:
            # For development - skip signature verification
            logger.warning("CLERK_SECRET_KEY not set - skipping JWT signature verification")
            payload = jwt.decode(token, options={"verify_signature": False})
        
        clerk_user_id = payload.get("sub")
        
        if not clerk_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing user ID"
            )
        
        # Find or create user in your database
        user = db.query(User).filter(User.clerk_id == clerk_user_id).first()
        
        if not user:
            # Create user if not exists
            user = User(
                clerk_id=clerk_user_id,
                email=payload.get("email", payload.get("email_addresses", [{}])[0].get("email_address", "")),
                first_name=payload.get("first_name", ""),
                last_name=payload.get("last_name", ""),
                avatar_url=payload.get("picture", payload.get("profile_image_url", "")),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"New user created from token: {clerk_user_id}")
        
        return user
        
    except jwt.ExpiredSignatureError:
        logger.error("JWT token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

# Optional: Get current user without raising exception (for optional auth)
def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

def get_tenant_by_identifier(db: Session, tenant_id: str) -> Optional[Tenant]:
    """
    Helper function to find tenant by either:
    1. clerk_organization_id (org_xxxxx format)
    2. id (UUID format)
    """
    logger.info(f"Looking up tenant for identifier: {tenant_id}")
    
    # Try by clerk_organization_id first (org_xxxxx format)
    tenant = db.query(Tenant).filter(
        Tenant.clerk_organization_id == tenant_id
    ).first()
    
    # Fall back to id (UUID)
    if not tenant:
        tenant = db.query(Tenant).filter(
            Tenant.id == tenant_id
        ).first()
    
    if tenant:
        logger.info(f"Tenant found: {tenant.name} (ID: {tenant.id}, Clerk Org ID: {tenant.clerk_organization_id})")
    else:
        logger.warning(f"No tenant found for identifier: {tenant_id}")
    
    return tenant

# ==================== AUTH ENDPOINTS ====================

@router.get("/me")
async def get_me(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Get current user with tenant and branch information
    Supports tenant lookup by both clerk_organization_id and tenant.id
    """
    try:
        logger.info(f"GET /me called with tenant_id: {tenant_id}")
        
        # Find tenant using the helper function
        tenant = get_tenant_by_identifier(db, tenant_id)
        
        # Get branches if tenant exists
        branches = []
        if tenant:
            branches = db.query(Branch).filter(
                Branch.tenant_id == tenant.id,
                Branch.is_active == True
            ).all()
            logger.info(f"Found {len(branches)} branches for tenant {tenant.name}")
        
        # Build response
        response = {
            "tenant_id": tenant_id,
            "tenant": {
                "id": str(tenant.id),
                "name": tenant.name,
                "plan": tenant.plan,
                "is_active": tenant.is_active,
                "slug": tenant.slug,
                "clerk_organization_id": tenant.clerk_organization_id
            } if tenant else None,
            "branches": [
                {
                    "id": str(b.id),
                    "name": b.name,
                    "has_fuel": b.has_fuel_station,
                    "location": b.location,
                    "is_active": b.is_active,
                    "phone": getattr(b, 'phone', None),
                    "email": getattr(b, 'email', None)
                }
                for b in branches
            ],
        }
        
        # Add user info if authenticated
        if current_user:
            response["user"] = {
                "id": current_user.id,
                "clerk_id": current_user.clerk_id,
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "avatar_url": current_user.avatar_url,
                "is_superuser": current_user.is_superuser,
                "is_active": current_user.is_active
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in get_me: {e}", exc_info=True)
        return {
            "tenant_id": tenant_id,
            "tenant": None,
            "branches": [],
            "error": str(e) if settings.DEBUG else "Internal server error"
        }

@router.get("/debug-token")
async def debug_token(
    authorization: str = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    """
    DEBUG ENDPOINT - Remove after fixing authentication issues
    This endpoint helps debug JWT token and tenant mapping problems
    """
    if not authorization:
        return {"error": "No authorization header provided"}
    
    # Extract token
    token = authorization.replace("Bearer ", "").strip()
    
    if not token or token in ("null", "undefined"):
        return {"error": "Invalid token value"}
    
    try:
        # Decode JWT payload manually
        parts = token.split(".")
        if len(parts) != 3:
            return {"error": f"Invalid JWT format: expected 3 parts, got {len(parts)}"}
        
        payload_b64 = parts[1]
        # Add padding for base64 decoding
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding
        
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
        
        # Extract organization info
        org_data = payload.get("o")
        org_id = None
        if org_data and isinstance(org_data, dict):
            org_id = org_data.get("id")
        
        # Get organization ID from top-level claim as fallback
        top_level_org_id = payload.get("org_id")
        
        # Get user ID
        user_id = payload.get("sub")
        
        # Query all tenants from database for comparison
        from sqlalchemy import text
        tenants_query = db.execute(text("""
            SELECT id, name, clerk_organization_id, slug, is_active 
            FROM tenants 
            ORDER BY created_at DESC 
            LIMIT 20
        """))
        
        all_tenants = [
            {
                "id": str(row[0]), 
                "name": row[1], 
                "clerk_org_id": row[2],
                "slug": row[3],
                "is_active": row[4]
            } 
            for row in tenants_query.fetchall()
        ]
        
        # Try to find matching tenant
        matching_tenant = None
        if org_id:
            for tenant in all_tenants:
                if tenant["clerk_org_id"] == org_id:
                    matching_tenant = tenant
                    break
        
        if not matching_tenant and top_level_org_id:
            for tenant in all_tenants:
                if tenant["clerk_org_id"] == top_level_org_id:
                    matching_tenant = tenant
                    break
        
        return {
            "token_org_id_from_o_claim": org_id,
            "token_org_id_top_level": top_level_org_id,
            "token_user_id": user_id,
            "token_email": payload.get("email"),
            "token_name": payload.get("name"),
            "token_o_claim_full": org_data,
            "all_token_claims": list(payload.keys()),
            "tenants_in_db": all_tenants,
            "matching_tenant": matching_tenant,
            "tenant_mapping_suggestion": f"Create tenant with clerk_organization_id = '{org_id or top_level_org_id}'" if not matching_tenant and (org_id or top_level_org_id) else None,
            "debug_mode": settings.DEBUG,
            "clerk_configured": bool(settings.CLERK_SECRET_KEY)
        }
        
    except base64.binascii.Error as e:
        logger.error(f"Base64 decoding error in debug-token: {e}")
        return {"error": f"Base64 decoding failed: {str(e)}", "token_preview": token[:50] + "..."}
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in debug-token: {e}")
        return {"error": f"JSON decode failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error in debug-token: {e}", exc_info=True)
        return {"error": f"Unexpected error: {str(e)}"}

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
        
        # Verify webhook signature (implement if needed)
        # For now, just log
        logger.info(f"Clerk webhook received: {event_type}")
        
        if event_type == "user.created":
            # Create user in your database
            email = data.get("email_addresses", [{}])[0].get("email_address", "")
            user = User(
                clerk_id=data.get("id"),
                email=email,
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                phone_number=data.get("phone_numbers", [{}])[0].get("phone_number", "") if data.get("phone_numbers") else "",
                avatar_url=data.get("profile_image_url", ""),
                is_active=True
            )
            db.add(user)
            db.commit()
            logger.info(f"User created via webhook: {user.clerk_id}")
            return {"status": "success", "event": event_type, "user_id": user.clerk_id}
            
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
                logger.info(f"User updated via webhook: {user.clerk_id}")
                return {"status": "success", "event": event_type, "user_id": user.clerk_id}
            else:
                logger.warning(f"User not found for update: {data.get('id')}")
                return {"status": "warning", "event": event_type, "message": "User not found"}
                
        elif event_type == "user.deleted":
            # Soft delete user
            user = db.query(User).filter(User.clerk_id == data.get("id")).first()
            if user:
                user.is_active = False
                db.commit()
                logger.info(f"User soft deleted via webhook: {user.clerk_id}")
                return {"status": "success", "event": event_type, "user_id": user.clerk_id}
            else:
                return {"status": "warning", "event": event_type, "message": "User not found"}
        
        elif event_type == "organization.created":
            # Handle organization creation (tenant)
            logger.info(f"Organization created: {data.get('id')} - {data.get('name')}")
            # You might want to automatically create a tenant here
            
        elif event_type == "organization.updated":
            # Handle organization update
            logger.info(f"Organization updated: {data.get('id')}")
            
        elif event_type == "organization.deleted":
            # Handle organization deletion
            logger.info(f"Organization deleted: {data.get('id')}")
        
        return {"status": "received", "event": event_type}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
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
                is_active=True
            )
            db.add(user)
            action = "created"
        else:
            user.email = sync_data.email
            user.first_name = sync_data.first_name
            user.last_name = sync_data.last_name
            user.phone_number = sync_data.phone_number
            user.avatar_url = sync_data.avatar_url
            action = "updated"
        
        db.commit()
        db.refresh(user)
        
        return {
            "status": "success",
            "action": action,
            "user": UserResponse.model_validate(user)
        }
        
    except Exception as e:
        logger.error(f"Sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-token")
async def validate_token(
    request: TokenValidationRequest,
    db: Session = Depends(get_db)
):
    """Validate a Clerk token and return user info"""
    try:
        # Decode and validate token
        if settings.CLERK_SECRET_KEY:
            payload = jwt.decode(
                request.token, 
                settings.CLERK_SECRET_KEY,
                algorithms=["RS256"]
            )
        else:
            payload = jwt.decode(request.token, options={"verify_signature": False})
        
        clerk_user_id = payload.get("sub")
        if not clerk_user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get or create user
        user = db.query(User).filter(User.clerk_id == clerk_user_id).first()
        if not user:
            user = User(
                clerk_id=clerk_user_id,
                email=payload.get("email", ""),
                first_name=payload.get("first_name", ""),
                last_name=payload.get("last_name", ""),
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return {
            "valid": True,
            "user": UserResponse.model_validate(user),
            "clerk_data": {
                "sub": clerk_user_id,
                "email": payload.get("email"),
                "name": payload.get("name")
            }
        }
        
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "Token expired"}
    except jwt.InvalidTokenError as e:
        return {"valid": False, "error": f"Invalid token: {str(e)}"}
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return {"valid": False, "error": str(e)}

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user
    Note: Actual token invalidation should be handled by Clerk on frontend
    """
    logger.info(f"User logged out: {current_user.clerk_id}")
    return {"message": "Successfully logged out"}

@router.get("/health")
async def auth_health():
    """Health check for auth service"""
    return {
        "status": "healthy",
        "clerk_configured": bool(settings.CLERK_SECRET_KEY),
        "service": "Authentication",
        "version": "1.0.0"
    }

@router.get("/tenant-info")
def get_tenant_info(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
    current_user: User = Depends(get_current_user),
):
    """Get current tenant information (requires auth)"""
    try:
        tenant = get_tenant_by_identifier(db, tenant_id)
        
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        branches = db.query(Branch).filter(
            Branch.tenant_id == tenant.id,
            Branch.is_active == True
        ).all()
        
        return {
            "tenant_id": tenant_id,
            "tenant": {
                "id": str(tenant.id),
                "name": tenant.name, 
                "plan": tenant.plan,
                "slug": tenant.slug,
                "is_active": tenant.is_active,
                "clerk_organization_id": tenant.clerk_organization_id
            },
            "branches": [
                {
                    "id": str(b.id), 
                    "name": b.name, 
                    "has_fuel": b.has_fuel_station,
                    "location": b.location,
                    "is_active": b.is_active,
                    "phone": getattr(b, 'phone', None),
                    "email": getattr(b, 'email', None)
                } for b in branches
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in tenant-info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PUBLIC ENDPOINTS (No Auth Required) ====================

@router.get("/tenant-info/public")
async def get_tenant_info_public(
    tenant_slug: Optional[str] = None,
    tenant_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to get tenant info without authentication
    Useful for testing and public-facing pages
    Can query by tenant_slug or tenant_id
    """
    try:
        tenant = None
        
        if tenant_slug:
            tenant = db.query(Tenant).filter(
                Tenant.slug == tenant_slug, 
                Tenant.is_active == True
            ).first()
        elif tenant_id:
            tenant = get_tenant_by_identifier(db, tenant_id)
        else:
            # Get first active tenant
            tenant = db.query(Tenant).filter(Tenant.is_active == True).first()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="No active tenant found")
        
        branches = db.query(Branch).filter(
            Branch.tenant_id == tenant.id, 
            Branch.is_active == True
        ).all()
        
        return {
            "tenant_id": str(tenant.id),
            "tenant": {
                "name": tenant.name,
                "slug": tenant.slug,
                "plan": tenant.plan,
                "logo_url": getattr(tenant, 'logo_url', None),
                "primary_color": getattr(tenant, 'primary_color', None),
                "clerk_organization_id": tenant.clerk_organization_id
            },
            "branches": [
                {
                    "id": str(b.id),
                    "name": b.name,
                    "has_fuel": b.has_fuel_station,
                    "location": b.location,
                    "phone": getattr(b, 'phone', None),
                    "email": getattr(b, 'email', None),
                    "working_hours": getattr(b, 'working_hours', None)
                } for b in branches
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in tenant-info/public: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tenants")
async def list_all_tenants_public(
    db: Session = Depends(get_db)
):
    """
    Public endpoint to list all active tenants (no auth required)
    Useful for landing pages and tenant selection
    """
    try:
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
        
        return {
            "tenants": [
                {
                    "id": str(t.id),
                    "name": t.name,
                    "slug": t.slug,
                    "plan": t.plan,
                    "logo_url": getattr(t, 'logo_url', None),
                    "clerk_organization_id": t.clerk_organization_id
                } for t in tenants
            ],
            "count": len(tenants)
        }
    except Exception as e:
        logger.error(f"Error listing tenants: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tenant-by-slug/{slug}")
async def get_tenant_by_slug_public(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Public endpoint to get tenant by slug (no auth required)
    """
    try:
        tenant = db.query(Tenant).filter(
            Tenant.slug == slug, 
            Tenant.is_active == True
        ).first()
        
        if not tenant:
            raise HTTPException(
                status_code=404, 
                detail=f"Tenant with slug '{slug}' not found"
            )
        
        branches = db.query(Branch).filter(
            Branch.tenant_id == tenant.id, 
            Branch.is_active == True
        ).all()
        
        return {
            "tenant_id": str(tenant.id),
            "tenant": {
                "name": tenant.name,
                "slug": tenant.slug,
                "plan": tenant.plan,
                "is_active": tenant.is_active,
                "clerk_organization_id": tenant.clerk_organization_id
            },
            "branches": [
                {
                    "id": str(b.id),
                    "name": b.name,
                    "has_fuel": b.has_fuel_station,
                    "location": b.location,
                    "phone": getattr(b, 'phone', None),
                    "email": getattr(b, 'email', None)
                } for b in branches
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in tenant-by-slug: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))