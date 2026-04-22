# app/routers/webhooks.py
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.config import settings
import logging
import json
import hmac
import hashlib

# REMOVE THIS LINE:
# import stripe

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Webhooks"])

# Remove any Stripe webhook handlers
# If you have Stripe webhook endpoints, comment them out or remove them

@router.post("/clerk")
async def clerk_webhook(request: Request, db: Session = Depends(get_db)):
    """Clerk webhook handler for user events"""
    try:
        payload = await request.body()
        headers = request.headers
        
        # Verify webhook signature
        svix_id = headers.get("svix-id")
        svix_timestamp = headers.get("svix-timestamp")
        svix_signature = headers.get("svix-signature")
        
        if not svix_id or not svix_signature:
            logger.warning("Missing webhook headers")
            raise HTTPException(status_code=400, detail="Missing webhook headers")
        
        # Verify the webhook using Clerk's secret
        secret = settings.CLERK_WEBHOOK_SECRET
        
        # TODO: Implement signature verification
        # For now, just log the webhook
        
        data = json.loads(payload)
        event_type = data.get("type")
        
        logger.info(f"Clerk webhook received: {event_type}")
        
        if event_type == "user.created":
            user_data = data.get("data", {})
            logger.info(f"New user created: {user_data.get('id')}")
            # TODO: Create user in your database
            
        elif event_type == "user.updated":
            user_data = data.get("data", {})
            logger.info(f"User updated: {user_data.get('id')}")
            # TODO: Update user in your database
            
        elif event_type == "user.deleted":
            user_data = data.get("data", {})
            logger.info(f"User deleted: {user_data.get('id')}")
            # TODO: Delete user from your database
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/intasend")
async def intasend_webhook(request: Request):
    """IntaSend webhook handler for payment events"""
    try:
        payload = await request.json()
        logger.info(f"IntaSend webhook received: {payload}")
        
        event_type = payload.get("type")
        data = payload.get("data", {})
        
        if event_type == "payment.success":
            invoice_id = data.get("invoice_id")
            amount = data.get("amount")
            logger.info(f"✅ Payment successful: Invoice {invoice_id}, Amount {amount}")
            # TODO: Update your database here
            
        elif event_type == "payment.failed":
            invoice_id = data.get("invoice_id")
            logger.warning(f"❌ Payment failed: Invoice {invoice_id}")
            # TODO: Update database to mark payment as failed
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"IntaSend webhook error: {str(e)}")
        return {"status": "received"}


# If you have a Stripe webhook endpoint, remove it or comment it out
# @router.post("/stripe")
# async def stripe_webhook(request: Request):
#     # This is no longer needed since you're using IntaSend
#     pass