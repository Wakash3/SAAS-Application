from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict
from ..core.database import get_db
from ..core.tenant import get_current_tenant
from ..models.stocktake import StocktakeSnapshot, StocktakeItem
from ..models.product import Product
from ..models.fuel import FuelProduct

router = APIRouter(prefix="/stocktake", tags=["stocktake"])


class ReconcileRequest(BaseModel):
    snapshot_id: str
    physical_counts: Dict[str, float]  # {item_id: physical_qty}


@router.get("/latest")
def latest_snapshot(
    branch_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    snap = (
        db.query(StocktakeSnapshot)
        .filter(
            StocktakeSnapshot.tenant_id == tenant_id,
            StocktakeSnapshot.branch_id == branch_id,
        )
        .order_by(StocktakeSnapshot.snapshot_date.desc())
        .first()
    )
    if not snap:
        return {"snapshot": None}

    items = db.query(StocktakeItem).filter(StocktakeItem.snapshot_id == snap.id).all()
    return {
        "snapshot": {
            "id": str(snap.id),
            "date": str(snap.snapshot_date),
            "type": snap.snapshot_type,
        },
        "items": [
            {
                "id": str(i.id),
                "product_name": i.product_name,
                "item_type": i.item_type,
                "system_qty": float(i.system_qty) if i.system_qty else 0,
                "physical_qty": float(i.physical_qty) if i.physical_qty else None,
                "variance": float(i.variance) if i.variance else 0,
                "variance_value_kes": float(i.variance_value_kes) if i.variance_value_kes else 0,
                "status": i.status,
            }
            for i in items
        ],
    }


@router.post("/reconcile")
def reconcile(
    payload: ReconcileRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    for item_id, physical_qty in payload.physical_counts.items():
        item = db.query(StocktakeItem).filter(StocktakeItem.id == item_id).first()
        if not item:
            continue
        item.physical_qty = physical_qty
        item.variance = physical_qty - float(item.system_qty)

        if item.item_type == "fmcg" and item.product_id:
            prod = db.query(Product).filter(Product.id == item.product_id).first()
            price = float(prod.selling_price) if prod else 0
        elif item.item_type == "fuel" and item.fuel_product_id:
            fuel = db.query(FuelProduct).filter(FuelProduct.id == item.fuel_product_id).first()
            price = float(fuel.price_per_litre) if fuel else 0
        else:
            price = 0

        item.variance_value_kes = item.variance * price
        item.status = (
            "surplus" if item.variance > 0
            else "shortage" if item.variance < -0.5
            else "ok"
        )

    db.commit()
    return {"reconciled": len(payload.physical_counts)}