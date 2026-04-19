from celery import shared_task
from ..core.database import SessionLocal
from ..models.product import Product
from ..models.fuel import FuelProduct
from ..models.stocktake import StocktakeSnapshot, StocktakeItem
from ..models.tenant import Tenant
from ..models.branch import Branch
from datetime import date
import uuid


@shared_task
def run_nightly_stocktake():
    """Runs at 6am EAT daily. Auto-generates stocktake for all active tenants."""
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
        for tenant in tenants:
            branches = db.query(Branch).filter(Branch.tenant_id == tenant.id).all()
            for branch in branches:
                _snapshot_branch(db, tenant.id, branch.id)
        db.commit()
    finally:
        db.close()


def _snapshot_branch(db, tenant_id, branch_id):
    snapshot = StocktakeSnapshot(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        branch_id=branch_id,
        snapshot_date=date.today(),
        snapshot_type="auto",
    )
    db.add(snapshot)
    db.flush()

    products = db.query(Product).filter(
        Product.tenant_id == tenant_id,
        Product.branch_id == branch_id,
        Product.is_active == True,
    ).all()

    for p in products:
        db.add(StocktakeItem(
            id=uuid.uuid4(),
            snapshot_id=snapshot.id,
            tenant_id=tenant_id,
            item_type="fmcg",
            product_id=p.id,
            product_name=p.name,
            system_qty=p.current_stock,
            physical_qty=None,
            variance=0,
            variance_value_kes=0,
            status="pending_verify",
        ))

    fuels = db.query(FuelProduct).filter(
        FuelProduct.tenant_id == tenant_id,
        FuelProduct.branch_id == branch_id,
    ).all()

    for f in fuels:
        db.add(StocktakeItem(
            id=uuid.uuid4(),
            snapshot_id=snapshot.id,
            tenant_id=tenant_id,
            item_type="fuel",
            fuel_product_id=f.id,
            product_name=f"{f.fuel_type} Pump {f.pump_number}",
            system_qty=float(f.current_stock_litres),
            physical_qty=None,
            variance=0,
            variance_value_kes=0,
            status="pending_verify",
        ))