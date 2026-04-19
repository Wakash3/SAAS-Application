from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.tenant import get_current_tenant
from ..models.tenant import Tenant
from ..models.branch import Branch

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def get_me(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant),
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    branches = db.query(Branch).filter(Branch.tenant_id == tenant_id).all()
    return {
        "tenant_id": tenant_id,
        "tenant": {"name": tenant.name, "plan": tenant.plan} if tenant else None,
        "branches": [{"id": str(b.id), "name": b.name, "has_fuel": b.has_fuel_station} for b in branches],
    }