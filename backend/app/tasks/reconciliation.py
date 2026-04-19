from celery import shared_task
from ..core.database import SessionLocal
from ..models.payment import MpesaTransaction
from ..services.mpesa_service import mpesa_service
import asyncio


@shared_task
def reconcile_pending_mpesa():
    """Every 2 minutes — re-query any pending M-Pesa transactions."""
    db = SessionLocal()
    try:
        pending = db.query(MpesaTransaction).filter(
            MpesaTransaction.status == "pending"
        ).limit(20).all()

        for tx in pending:
            try:
                result = asyncio.run(mpesa_service.query_status(tx.checkout_request_id))
                if result.get("ResultCode") == "0":
                    tx.status = "paid"
                elif result.get("ResultCode") not in (None, "1032"):
                    tx.status = "failed"
            except Exception:
                pass

        db.commit()
    finally:
        db.close()