from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from ..core.database import get_db
from ..core.tenant import get_current_tenant
from ..models.product import Product

router = APIRouter(prefix="/products", tags=["products"])


class ProductCreate(BaseModel):
    branch_id: str
    name: str
    sku: Optional[str] = None
    barcode: Optional[str] = None
    category: Optional[str] = None
    buying_price: Optional[float] = None
    selling_price: float
    current_stock: int = 0
    reorder_level: int = 10
    unit: str = "piece"


@router.get("/")
def list_products(
    branch_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    return db.query(Product).filter(
        Product.tenant_id == tenant_id,
        Product.branch_id == branch_id,
        Product.is_active == True,
    ).all()


@router.post("/")
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    product = Product(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        **payload.dict(),
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/{product_id}/stock")
def update_stock(
    product_id: str,
    adjustment: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    p = db.query(Product).filter(
        Product.id == product_id, Product.tenant_id == tenant_id
    ).first()
    if not p:
        raise HTTPException(404, "Product not found")
    p.current_stock += adjustment
    db.commit()
    return {"id": str(p.id), "new_stock": p.current_stock}