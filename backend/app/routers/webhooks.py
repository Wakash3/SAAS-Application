from fastapi import APIRouter, Request, HTTPException, Header
from sqlalchemy.orm import Session
from fastapi import Depends
from svix.webhooks import Webhook, WebhookVerificationError
import uuid
import stripe
from ..core.database import get_db
from ..core.config import settings
from ..models.tenant import Tenant
from ..models.branch import Branch

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/clerk")
async def clerk_webhook(request: Request, svix_signature: str = Header(None), db: Session = Depends(get_db)):
    body = await request.body()
    headers = dict(request.headers)

    try:
        wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
        evt = wh.verify(body, headers)
    except WebhookVerificationError:
        raise HTTPException(400, "Invalid webhook signature")

    event_type = evt.get("type")

    if event_type == "organization.created":
        org = evt["data"]
        existing = db.query(Tenant).filter(Tenant.id == org["id"]).first()
        if not existing:
            tenant = Tenant(
                id=org["id"],
                name=org["name"],
                slug=org.get("slug") or org["id"][:20],
                plan="starter",
                is_active=True,
            )
            db.add(tenant)
            # Auto-create first branch
            branch = Branch(
                id=uuid.uuid4(),
                tenant_id=org["id"],
                name=f"{org['name']} - Main Branch",
                has_fuel_station=False,
            )
            db.add(branch)
            db.commit()

    return {"received": True}


@router.post("/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), db: Session = Depends(get_db)):
    body = await request.body()
    try:
        event = stripe.Webhook.construct_event(body, stripe_signature, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(400, "Invalid Stripe signature")

    if event["type"] in ("customer.subscription.created", "customer.subscription.updated"):
        sub = event["data"]["object"]
        customer_id = sub["customer"]
        plan = "growth" if sub.get("items", {}).get("data", [{}])[0].get("price", {}).get("nickname") == "Growth" else "starter"
        tenant = db.query(Tenant).filter(Tenant.stripe_customer_id == customer_id).first()
        if tenant:
            tenant.plan = plan
            db.commit()

    elif event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        tenant = db.query(Tenant).filter(Tenant.stripe_customer_id == sub["customer"]).first()
        if tenant:
            tenant.plan = "starter"
            db.commit()

    return {"received": True}