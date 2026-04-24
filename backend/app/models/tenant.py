# app/models/tenant.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid
from datetime import datetime, timezone


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_organization_id = Column(String(255), unique=True, index=True, nullable=True)  # Clerk org ID - Required for tenant resolution
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    plan = Column(String(50), default="starter")
    stripe_customer_id = Column(String(255), nullable=True)
    mpesa_shortcode = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Settings JSON field for additional configuration
    settings = Column(String, nullable=True)  # JSON string for settings
    
    # Relationships
    branches = relationship("Branch", back_populates="tenant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name}, slug={self.slug}, clerk_organization_id={self.clerk_organization_id})>"
    
    def to_dict(self):
        """Convert tenant to dictionary"""
        return {
            "id": str(self.id),
            "clerk_organization_id": self.clerk_organization_id,
            "name": self.name,
            "slug": self.slug,
            "plan": self.plan,
            "stripe_customer_id": self.stripe_customer_id,
            "mpesa_shortcode": self.mpesa_shortcode,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_simple_dict(self):
        """Convert tenant to simple dictionary for API responses"""
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "plan": self.plan,
        }
    
    def get_branches(self, db_session):
        """Get all branches for this tenant"""
        from .branch import Branch
        return db_session.query(Branch).filter(Branch.tenant_id == self.id, Branch.is_active == True).all()