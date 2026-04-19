from celery import shared_task
from ..core.database import SessionLocal
from ..models.product import Product
from ..models.fuel import FuelProduct
from ..models.tenant import Tenant
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_low_stock():
    """8am daily — log low stock alerts (extend to send WhatsApp/email)."""
    db = SessionLocal()
    try:
        tenants = db.query(Tenant).filter(Tenant.is_active == True).all()
        for tenant in tenants:
            low_products = db.query(Product).filter(
                Product.tenant_id == tenant.id,
                Product.current_stock <= Product.reorder_level,
                Product.is_active == True,
            ).all()
            low_fuel = db.query(FuelProduct).filter(
                FuelProduct.tenant_id == tenant.id,
                FuelProduct.current_stock_litres <= FuelProduct.reorder_level_litres,
            ).all()

            if low_products or low_fuel:
                logger.warning(
                    f"[ALERT] Tenant {tenant.name}: "
                    f"{len(low_products)} FMCG items low, "
                    f"{len(low_fuel)} fuel tanks low"
                )
                # TODO: send WhatsApp via Twilio or Africa's Talking
    finally:
        db.close()