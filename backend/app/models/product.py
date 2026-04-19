from sqlalchemy import Column, String, Boolean, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from ..core.database import Base
import uuid
from datetime import datetime, timezone  


class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"))
    name = Column(String(255), nullable=False)
    sku = Column(String(100))
    barcode = Column(String(100))
    category = Column(String(100))
    buying_price = Column(Numeric(10, 2))
    selling_price = Column(Numeric(10, 2), nullable=False)
    current_stock = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    unit = Column(String(50), default="piece")
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))  