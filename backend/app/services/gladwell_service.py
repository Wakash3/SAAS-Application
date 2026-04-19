from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from ..models.sale import Sale
from ..models.product import Product
from ..models.fuel import FuelProduct
from ..models.stocktake import StocktakeSnapshot, StocktakeItem
import json


class GladwellService:
    def build_prompt(self, page: str, tenant_id: str, branch_id: str, db: Session) -> str:
        data = self._get_data(page, tenant_id, branch_id, db)
        return f"""You are Gladwell, an AI Retail Analyst inside Msingi.
You help Kenyan retail and petroleum business owners make smart decisions.
Always use KES for currency. Be concise, specific, and actionable.
Only use the data provided — never invent numbers.
Date: {datetime.now().strftime('%A %d %B %Y')}
Page: {page}

LIVE BUSINESS DATA:
{json.dumps(data, indent=2, default=str)}"""

    def _get_data(self, page, tenant_id, branch_id, db):
        today = datetime.now().date()
        if page == "overview":
            return self._overview_data(tenant_id, today, db)
        elif page == "fuel":
            return self._fuel_data(tenant_id, branch_id, db)
        elif page == "inventory":
            return self._inventory_data(tenant_id, branch_id, db)
        elif page == "pos":
            return self._pos_data(tenant_id, branch_id, db)
        elif page == "stocktake":
            return self._stocktake_data(tenant_id, branch_id, today, db)
        return {}

    def _overview_data(self, tenant_id, today, db):
        total = db.query(func.sum(Sale.total_amount)).filter(
            Sale.tenant_id == tenant_id,
            Sale.payment_status == "paid",
        ).scalar() or 0
        today_sales = db.query(func.sum(Sale.total_amount)).filter(
            Sale.tenant_id == tenant_id,
            Sale.payment_status == "paid",
            func.date(Sale.created_at) == today,
        ).scalar() or 0
        tx_count = db.query(func.count(Sale.id)).filter(
            Sale.tenant_id == tenant_id,
            func.date(Sale.created_at) == today,
        ).scalar() or 0
        return {
            "total_revenue_kes": float(total),
            "today_revenue_kes": float(today_sales),
            "today_transaction_count": tx_count,
        }

    def _fuel_data(self, tenant_id, branch_id, db):
        fuels = db.query(FuelProduct).filter(
            FuelProduct.tenant_id == tenant_id,
            FuelProduct.branch_id == branch_id,
        ).all()
        return {
            "pumps": [
                {
                    "type": f.fuel_type,
                    "pump": f.pump_number,
                    "stock_L": float(f.current_stock_litres),
                    "capacity_L": float(f.tank_capacity_litres) if f.tank_capacity_litres else 0,
                    "price_per_L": float(f.price_per_litre),
                    "value_KES": round(float(f.current_stock_litres) * float(f.price_per_litre)),
                    "pct_full": round(
                        float(f.current_stock_litres) / float(f.tank_capacity_litres) * 100, 1
                    ) if f.tank_capacity_litres else 0,
                    "needs_reorder": float(f.current_stock_litres) <= float(f.reorder_level_litres),
                }
                for f in fuels
            ]
        }

    def _inventory_data(self, tenant_id, branch_id, db):
        low = db.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.branch_id == branch_id,
            Product.current_stock <= Product.reorder_level,
        ).all()
        return {
            "low_stock_items": [
                {"name": p.name, "stock": p.current_stock, "reorder_at": p.reorder_level}
                for p in low
            ]
        }

    def _pos_data(self, tenant_id, branch_id, db):
        prods = db.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.branch_id == branch_id,
            Product.is_active == True,
            Product.current_stock > 0,
        ).limit(60).all()
        return {
            "products": [
                {"name": p.name, "sku": p.sku, "price": float(p.selling_price), "stock": p.current_stock}
                for p in prods
            ]
        }

    def _stocktake_data(self, tenant_id, branch_id, today, db):
        latest = (
            db.query(StocktakeSnapshot)
            .filter(
                StocktakeSnapshot.tenant_id == tenant_id,
                StocktakeSnapshot.branch_id == branch_id,
            )
            .order_by(StocktakeSnapshot.snapshot_date.desc())
            .first()
        )
        if not latest:
            return {"message": "No stocktake snapshots yet"}
        items = db.query(StocktakeItem).filter(
            StocktakeItem.snapshot_id == latest.id,
            StocktakeItem.status != "ok",
        ).all()
        return {
            "date": str(latest.snapshot_date),
            "variances": [
                {
                    "product": i.product_name,
                    "variance": float(i.variance) if i.variance else 0,
                    "value_KES": float(i.variance_value_kes) if i.variance_value_kes else 0,
                    "status": i.status,
                }
                for i in items
            ],
        }


gladwell_service = GladwellService()