# app/models/branch.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid
from datetime import datetime, timezone


class Branch(Base):
    __tablename__ = "branches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(500), nullable=True)
    has_fuel_station = Column(Boolean, default=False)
    mpesa_till = Column(String(20), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    manager_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="branches")
    
    def __repr__(self):
        return f"<Branch(id={self.id}, name={self.name}, tenant_id={self.tenant_id})>"
    
    def to_dict(self):
        """Convert branch to dictionary"""
        return {
            "id": str(self.id),
            "tenant_id": str(self.tenant_id) if self.tenant_id else None,
            "name": self.name,
            "location": self.location,
            "has_fuel_station": self.has_fuel_station,
            "mpesa_till": self.mpesa_till,
            "phone": self.phone,
            "email": self.email,
            "manager_name": self.manager_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_simple_dict(self):
        """Convert branch to simple dictionary for API responses"""
        return {
            "id": str(self.id),
            "name": self.name,
            "location": self.location,
            "has_fuel": self.has_fuel_station,
        }