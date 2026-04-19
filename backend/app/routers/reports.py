from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..core.database import get_db
from ..core.tenant import get_current_tenant
from ..models.sale import Sale

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary")
def sales_summary(
    branch_id: str,
    days: int = 7,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    since = datetime.utcnow() - timedelta(days=days)
    total = db.query(func.sum(Sale.total_amount)).filter(
        Sale.tenant_id == tenant_id,
        Sale.branch_id == branch_id,
        Sale.payment_status == "paid",
        Sale.created_at >= since,
    ).scalar() or 0

    by_method = (
        db.query(Sale.payment_method, func.sum(Sale.total_amount))
        .filter(
            Sale.tenant_id == tenant_id,
            Sale.branch_id == branch_id,
            Sale.payment_status == "paid",
            Sale.created_at >= since,
        )
        .group_by(Sale.payment_method)
        .all()
    )

    return {
        "period_days": days,
        "total_revenue_kes": float(total),
        "by_payment_method": {m: float(v) for m, v in by_method},
    }