from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from ..core.database import get_db
from ..core.tenant import get_current_tenant
from ..models.sale import Sale, SaleItem
from ..models.product import Product
from ..models.fuel import FuelProduct

router = APIRouter(prefix="/sales", tags=["sales"])


class SaleItemIn(BaseModel):
    item_type: str  # 'fmcg' or 'fuel'
    product_id: Optional[str] = None
    fuel_product_id: Optional[str] = None
    description: Optional[str] = None
    quantity: float
    unit_price: float
    meter_start: Optional[float] = None
    meter_end: Optional[float] = None


class SaleCreate(BaseModel):
    branch_id: str
    cashier_id: str
    sale_type: str = "mixed"
    payment_method: str
    items: List[SaleItemIn]


@router.post("/")
def create_sale(
    payload: SaleCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    total = sum(i.quantity * i.unit_price for i in payload.items)
    sale_number = f"MSN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4].upper()}"

    sale = Sale(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        branch_id=payload.branch_id,
        sale_number=sale_number,
        cashier_id=payload.cashier_id,
        sale_type=payload.sale_type,
        subtotal=total,
        total_amount=total,
        payment_method=payload.payment_method,
        payment_status="pending" if payload.payment_method == "mpesa" else "paid",
    )
    db.add(sale)
    db.flush()

    for item in payload.items:
        si = SaleItem(
            id=uuid.uuid4(),
            sale_id=sale.id,
            tenant_id=tenant_id,
            item_type=item.item_type,
            product_id=item.product_id,
            fuel_product_id=item.fuel_product_id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.quantity * item.unit_price,
            meter_start=item.meter_start,
            meter_end=item.meter_end,
        )
        db.add(si)

        # Decrement stock
        if item.item_type == "fmcg" and item.product_id:
            p = db.query(Product).filter(Product.id == item.product_id).first()
            if p:
                p.current_stock -= int(item.quantity)

        if item.item_type == "fuel" and item.fuel_product_id:
            f = db.query(FuelProduct).filter(FuelProduct.id == item.fuel_product_id).first()
            if f:
                f.current_stock_litres -= item.quantity

    db.commit()
    return {"id": str(sale.id), "sale_number": sale_number, "total": total}


@router.get("/")
def list_sales(
    branch_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    return (
        db.query(Sale)
        .filter(Sale.tenant_id == tenant_id, Sale.branch_id == branch_id)
        .order_by(Sale.created_at.desc())
        .limit(50)
        .all()
    )