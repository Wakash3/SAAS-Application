from sqlalchemy import Column, String, Boolean, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from ..core.database import Base
import uuid
from datetime import datetime, timezone


class FuelProduct(Base):
    __tablename__ = "fuel_products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"))
    fuel_type = Column(String(50), nullable=False)
    pump_number = Column(Integer)
    nozzle_number = Column(Integer)
    price_per_litre = Column(Numeric(10, 2), nullable=False)
    current_meter = Column(Numeric(12, 4), default=0)
    tank_capacity_litres = Column(Numeric(10, 2))
    current_stock_litres = Column(Numeric(10, 2), default=0)
    reorder_level_litres = Column(Numeric(10, 2), default=200)
    is_active = Column(Boolean, default=True)
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )