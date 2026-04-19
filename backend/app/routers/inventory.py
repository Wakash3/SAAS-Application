from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..core.database import get_db
from ..core.tenant import get_current_tenant
from ..models.product import Product
from ..models.fuel import FuelProduct

router = APIRouter(prefix="/inventory", tags=["inventory"])


class DeliveryIn(BaseModel):
    branch_id: str
    product_id: str
    quantity: int
    item_type: str = "fmcg"  # 'fmcg' or 'fuel'


@router.get("/summary")
def inventory_summary(
    branch_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    products = db.query(Product).filter(
        Product.tenant_id == tenant_id,
        Product.branch_id == branch_id,
        Product.is_active == True,
    ).all()
    fuels = db.query(FuelProduct).filter(
        FuelProduct.tenant_id == tenant_id,
        FuelProduct.branch_id == branch_id,
    ).all()

    return {
        "fmcg": [
            {
                "id": str(p.id),
                "name": p.name,
                "stock": p.current_stock,
                "reorder_level": p.reorder_level,
                "low": p.current_stock <= p.reorder_level,
                "value_kes": float(p.current_stock * p.selling_price),
            }
            for p in products
        ],
        "fuel": [
            {
                "id": str(f.id),
                "type": f.fuel_type,
                "pump": f.pump_number,
                "stock_L": float(f.current_stock_litres),
                "value_kes": float(f.current_stock_litres * f.price_per_litre),
                "low": float(f.current_stock_litres) <= float(f.reorder_level_litres),
            }
            for f in fuels
        ],
    }


@router.post("/delivery")
def record_delivery(
    payload: DeliveryIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    if payload.item_type == "fmcg":
        p = db.query(Product).filter(
            Product.id == payload.product_id,
            Product.tenant_id == tenant_id,
        ).first()
        if p:
            p.current_stock += payload.quantity
            db.commit()
            return {"new_stock": p.current_stock}
    elif payload.item_type == "fuel":
        f = db.query(FuelProduct).filter(
            FuelProduct.id == payload.product_id,
            FuelProduct.tenant_id == tenant_id,
        ).first()
        if f:
            f.current_stock_litres += payload.quantity
            db.commit()
            return {"new_stock_litres": float(f.current_stock_litres)}
    return {"error": "Not found"}