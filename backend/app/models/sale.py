from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from ..core.database import Base
import uuid
from datetime import datetime, timezone


class Sale(Base):
    __tablename__ = "sales"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    branch_id = Column(UUID(as_uuid=True), nullable=False)
    sale_number = Column(String(50), unique=True, nullable=False)
    cashier_id = Column(String(255), nullable=False)
    sale_type = Column(String(20), default="mixed")
    subtotal = Column(Numeric(10, 2))
    total_amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50))
    payment_status = Column(String(50), default="pending")
    mpesa_receipt = Column(String(100))
    mpesa_phone = Column(String(20))
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.id", ondelete="CASCADE"))
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    item_type = Column(String(20), nullable=False)  # 'fmcg' or 'fuel'
    product_id = Column(UUID(as_uuid=True))
    fuel_product_id = Column(UUID(as_uuid=True))
    description = Column(String(255))
    quantity = Column(Numeric(10, 4), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    meter_start = Column(Numeric(12, 4))
    meter_end = Column(Numeric(12, 4))
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )