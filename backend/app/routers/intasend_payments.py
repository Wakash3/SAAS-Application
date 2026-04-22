# app/routers/intasend_payments.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from ..services.intasend_service import intasend_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["IntaSend Payments"])

class STKPushRequest(BaseModel):
    phone_number: str
    amount: float
    email: str
    narrative: str = "Payment for Msingi Retail"

class CheckoutRequest(BaseModel):
    amount: float
    email: str
    phone_number: Optional[str] = None
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    currency: str = "KES"

class PaymentStatusRequest(BaseModel):
    invoice_id: str

@router.post("/intasend/stk-push")
async def initiate_stk_push(request: STKPushRequest):
    """Initiate M-Pesa STK Push payment using IntaSend"""
    try:
        response = intasend_service.initiate_mpesa_stk_push(
            phone_number=request.phone_number,
            amount=request.amount,
            email=request.email,
            narrative=request.narrative
        )
        return {
            "success": True,
            "data": response,
            "message": "STK Push sent successfully"
        }
    except Exception as e:
        logger.error(f"STK Push error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/intasend/checkout")
async def create_checkout(request: CheckoutRequest):
    """Create a checkout URL for card payments"""
    try:
        response = intasend_service.checkout(
            amount=request.amount,
            email=request.email,
            phone_number=request.phone_number,
            first_name=request.first_name,
            last_name=request.last_name,
            currency=request.currency
        )
        return {
            "success": True,
            "checkout_url": response.get("redirect_url"),
            "invoice_id": response.get("invoice_id"),
            "data": response
        }
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/intasend/status/{invoice_id}")
async def get_payment_status(invoice_id: str):
    """Check payment status using invoice ID"""
    try:
        response = intasend_service.get_payment_status(invoice_id)
        return {
            "success": True,
            "data": response
        }
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/intasend/webhook")
async def intasend_webhook(request: Request):
    """Webhook endpoint for IntaSend payment notifications"""
    try:
        payload = await request.json()
        logger.info(f"IntaSend webhook received: {payload}")
        
        event_type = payload.get("type")
        data = payload.get("data", {})
        
        if event_type == "payment.success":
            invoice_id = data.get("invoice_id")
            amount = data.get("amount")
            logger.info(f"✅ Payment successful: Invoice {invoice_id}, Amount {amount}")
            
        elif event_type == "payment.failed":
            invoice_id = data.get("invoice_id")
            logger.warning(f"❌ Payment failed: Invoice {invoice_id}")
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return {"status": "received"}