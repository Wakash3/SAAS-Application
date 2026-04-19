from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from ..core.database import Base
import uuid
from datetime import datetime, timezone


class MpesaTransaction(Base):
    __tablename__ = "mpesa_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    sale_id = Column(UUID(as_uuid=True), ForeignKey("sales.id"))
    checkout_request_id = Column(String(255), unique=True)
    mpesa_receipt_number = Column(String(100))
    phone_number = Column(String(20))
    amount = Column(Numeric(10, 2))
    status = Column(String(50), default="pending")
    raw_callback = Column(JSONB)
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )