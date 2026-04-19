from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import httpx
from ..core.database import get_db
from ..core.tenant import get_current_tenant
from ..models.sale import Sale

router = APIRouter(prefix="/erp", tags=["erp"])


class ERPWebhookConfig(BaseModel):
    webhook_url: str
    secret: Optional[str] = None


@router.post("/sync/webhook")
async def sync_via_webhook(
    config: ERPWebhookConfig,
    branch_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    """Push last 10 sales to an ERP webhook."""
    sales = (
        db.query(Sale)
        .filter(Sale.tenant_id == tenant_id, Sale.branch_id == branch_id, Sale.payment_status == "paid")
        .order_by(Sale.created_at.desc())
        .limit(10)
        .all()
    )
    payload = [
        {
            "sale_number": s.sale_number,
            "total": float(s.total_amount),
            "method": s.payment_method,
            "date": str(s.created_at),
        }
        for s in sales
    ]
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(config.webhook_url, json={"sales": payload})
    return {"synced": len(payload), "status": r.status_code}