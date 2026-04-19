from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
from ..core.database import get_db
from ..core.tenant import get_current_tenant
from ..models.fuel import FuelProduct

router = APIRouter(prefix="/fuel", tags=["fuel"])


class FuelCreate(BaseModel):
    branch_id: str
    fuel_type: str
    pump_number: int
    price_per_litre: float
    tank_capacity_litres: float
    current_stock_litres: float = 0
    reorder_level_litres: float = 200


class DipStickReading(BaseModel):
    fuel_product_id: str
    physical_litres: float


@router.get("/")
def list_fuel(
    branch_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    return db.query(FuelProduct).filter(
        FuelProduct.tenant_id == tenant_id,
        FuelProduct.branch_id == branch_id,
    ).all()


@router.post("/")
def create_fuel_product(
    payload: FuelCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    fp = FuelProduct(id=uuid.uuid4(), tenant_id=tenant_id, **payload.dict())
    db.add(fp)
    db.commit()
    db.refresh(fp)
    return fp


@router.post("/dipstick")
def record_dipstick(
    payload: DipStickReading,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    fp = db.query(FuelProduct).filter(
        FuelProduct.id == payload.fuel_product_id,
        FuelProduct.tenant_id == tenant_id,
    ).first()
    if not fp:
        raise HTTPException(404, "Fuel product not found")

    system_stock = float(fp.current_stock_litres)
    physical = payload.physical_litres
    variance = physical - system_stock

    return {
        "system_litres": system_stock,
        "physical_litres": physical,
        "variance_litres": round(variance, 2),
        "variance_kes": round(variance * float(fp.price_per_litre), 2),
        "status": "surplus" if variance > 0 else "shortage" if variance < -50 else "ok",
    }