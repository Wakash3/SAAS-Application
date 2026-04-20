from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from .core.config import settings
from .routers import auth, chat, products, fuel, sales, inventory, stocktake, payments, erp, reports, webhooks
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.2,
        environment="production" if not settings.DEBUG else "development",
    )

app = FastAPI(
    title="Msingi Retail API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://retail-intelligence-system-sigma.vercel.app",
        "https://app.msingi.co.ke",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
for r in [auth, chat, products, fuel, sales, inventory, stocktake, payments, erp, reports, webhooks]:
    app.include_router(r.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}


# ==================== M-PESA CALLBACK ENDPOINT ====================
# IMPORTANT: URL must NOT contain "mpesa" or "safaricom" in the path
# This endpoint receives payment confirmations from Safaricom

@app.post("/api/v1/payments/callback")
async def mpesa_callback(request: Request):
    """
    M-Pesa STK Push Callback Endpoint
    Receives payment confirmation from Safaricom after customer completes STK Push
    
    Response must be immediate (within 5 seconds) to prevent retries
    """
    
    # Log the raw request for debugging
    logger.info("=" * 60)
    logger.info("M-PESA CALLBACK RECEIVED")
    logger.info("=" * 60)
    
    try:
        # Parse the incoming JSON
        callback_data = await request.json()
        logger.info(f"Callback Body: {json.dumps(callback_data, indent=2)}")
        
        # Extract the important parts
        body = callback_data.get('Body', {})
        stk_callback = body.get('stkCallback', {})
        
        # Get result code and description
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        merchant_request_id = stk_callback.get('MerchantRequestID')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        
        logger.info(f"Result Code: {result_code}")
        logger.info(f"Result Description: {result_desc}")
        logger.info(f"Checkout Request ID: {checkout_request_id}")
        
        if result_code == 0:
            # Payment was successful
            callback_metadata = stk_callback.get('CallbackMetadata', {})
            items = callback_metadata.get('Item', [])
            
            # Convert items array to dictionary for easier access
            transaction_data = {}
            for item in items:
                transaction_data[item['Name']] = item.get('Value')
            
            # Extract transaction details
            amount = transaction_data.get('Amount')
            mpesa_receipt = transaction_data.get('MpesaReceiptNumber')
            transaction_date = transaction_data.get('TransactionDate')
            phone_number = transaction_data.get('PhoneNumber')
            
            logger.info(f"✅ PAYMENT SUCCESSFUL")
            logger.info(f"   Receipt: {mpesa_receipt}")
            logger.info(f"   Amount: {amount}")
            logger.info(f"   Phone: {phone_number}")
            logger.info(f"   Date: {transaction_date}")
            
            # TODO: Update your database here
            # 1. Find the pending order using checkout_request_id
            # 2. Mark it as paid
            # 3. Update user's premium status if applicable
            # 4. Save mpesa_receipt for reference
            
            # Example database update (implement based on your models):
            """
            from .models import Transaction
            
            transaction = await Transaction.objects.get(checkout_request_id=checkout_request_id)
            transaction.status = "completed"
            transaction.mpesa_receipt = mpesa_receipt
            transaction.amount_paid = amount
            transaction.paid_at = datetime.now()
            await transaction.save()
            """
            
        else:
            # Payment failed, cancelled, or timed out
            logger.warning(f"❌ PAYMENT FAILED")
            logger.warning(f"   Result Code: {result_code}")
            logger.warning(f"   Result Description: {result_desc}")
            
            # Map common error codes
            error_messages = {
                1032: "Transaction cancelled by user",
                1037: "Transaction timeout - customer took too long",
                2001: "Insufficient funds",
                1001: "Invalid phone number",
                1006: "Invalid amount",
            }
            
            user_friendly_message = error_messages.get(result_code, result_desc)
            logger.warning(f"   User Friendly Message: {user_friendly_message}")
            
            # TODO: Update database to mark transaction as failed
            """
            from .models import Transaction
            
            transaction = await Transaction.objects.get(checkout_request_id=checkout_request_id)
            transaction.status = "failed"
            transaction.failure_reason = user_friendly_message
            transaction.failure_code = result_code
            await transaction.save()
            """
        
        # Respond with success to acknowledge receipt
        # This prevents Safaricom from retrying the callback
        return {
            "ResultCode": 0,
            "ResultDesc": "Success"
        }
        
    except Exception as e:
        # Log the error but still return success to prevent retries
        logger.error(f"ERROR processing callback: {str(e)}", exc_info=True)
        
        # Even on error, return success to prevent endless retries
        # The error will be fixed in the next deployment
        return {
            "ResultCode": 0,
            "ResultDesc": "Success"
        }


# ==================== M-PESA DEBUGGING ENDPOINT ====================
# Only available in DEBUG mode for testing callbacks locally

if settings.DEBUG:
    @app.post("/api/v1/payments/callback/debug")
    async def mpesa_callback_debug(request: Request):
        """
        Debug endpoint to simulate callbacks locally
        Only available when DEBUG=true
        """
        debug_data = await request.json()
        logger.info(f"🔧 DEBUG CALLBACK RECEIVED: {json.dumps(debug_data, indent=2)}")
        
        return {
            "ResultCode": 0,
            "ResultDesc": "Debug callback received",
            "simulated": True
        }


# ==================== HEALTH CHECK FOR CALLBACK ====================
# Simple endpoint to verify callback URL is reachable

@app.get("/api/v1/payments/callback/health")
async def callback_health():
    """
    Health check for the callback endpoint
    Use this to verify your callback URL is correctly configured
    """
    return {
        "status": "healthy",
        "callback_url_configured": True,
        "expected_format": "https://YOUR-RAILWAY-URL/api/v1/payments/callback",
        "note": "URL must NOT contain 'mpesa' or 'safaricom' in the path"
    }