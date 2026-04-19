from sqlalchemy import Column, String, Numeric, DateTime, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from ..core.database import Base
import uuid
from datetime import datetime, timezone


class StocktakeSnapshot(Base):
    __tablename__ = "stocktake_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    branch_id = Column(UUID(as_uuid=True), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    snapshot_type = Column(String(20), default="auto")
    generated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    completed_at = Column(
        DateTime(timezone=True), 
        nullable=True
    )


class StocktakeItem(Base):
    __tablename__ = "stocktake_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id = Column(UUID(as_uuid=True), ForeignKey("stocktake_snapshots.id"))
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    item_type = Column(String(20))
    product_id = Column(UUID(as_uuid=True))
    fuel_product_id = Column(UUID(as_uuid=True))
    product_name = Column(String(255))
    system_qty = Column(Numeric(10, 4))
    physical_qty = Column(Numeric(10, 4))
    variance = Column(Numeric(10, 4))
    variance_value_kes = Column(Numeric(10, 2))
    status = Column(String(20), default="ok")
    counted_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )