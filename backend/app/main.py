from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from .core.config import settings
from .routers import (
    auth, chat, products, fuel, sales,
    inventory, stocktake, payments, erp,
    reports, webhooks
)
from .health import router as health_router
import logging
import json

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)

# Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.2,
        environment="production" if not settings.DEBUG else "development",
    )
    logger.info("✅ Sentry initialized")

app = FastAPI(
    title="Msingi Retail API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://saas-application-u2pt.vercel.app",
        "https://retail-intelligence-system-sigma.vercel.app",
        "https://app.msingi.co.ke",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
# Include health router first (no prefix for health check)
app.include_router(health_router, tags=["health"])

# Include all other routers with /api/v1 prefix
for r in [auth, chat, products, fuel, sales,
          inventory, stocktake, payments, erp,
          reports, webhooks]:
    app.include_router(r.router, prefix="/api/v1")
    logger.debug(f"✅ Router loaded: {r.__name__}")


# ── Startup / Shutdown ────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    from .core.database import init_db
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    from .core.database import close_db
    try:
        close_db()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")


# ── Root Endpoints ────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "name": "Msingi Retail API",
        "version": "1.0.0",
        "docs_url": "/docs" if settings.DEBUG else "disabled",
        "health": "/health"
    }


# ── M-Pesa Callback ───────────────────────────────────────────
@app.post("/api/v1/payments/callback")
async def mpesa_callback(request: Request):
    logger.info("=" * 60)
    logger.info("M-PESA CALLBACK RECEIVED")
    logger.info("=" * 60)

    try:
        callback_data = await request.json()
        logger.info(f"Callback Body: {json.dumps(callback_data, indent=2)}")

        stk_callback = callback_data.get("Body", {}).get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")
        checkout_request_id = stk_callback.get("CheckoutRequestID")

        logger.info(f"Result Code: {result_code}")
        logger.info(f"Result Description: {result_desc}")
        logger.info(f"Checkout Request ID: {checkout_request_id}")

        if result_code == 0:
            items = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            transaction_data = {item["Name"]: item.get("Value") for item in items}
            logger.info(f"✅ PAYMENT SUCCESSFUL")
            logger.info(f"   Receipt: {transaction_data.get('MpesaReceiptNumber')}")
            logger.info(f"   Amount: {transaction_data.get('Amount')}")
            logger.info(f"   Phone: {transaction_data.get('PhoneNumber')}")
        else:
            logger.warning(f"❌ PAYMENT FAILED: {result_code} - {result_desc}")

        return {"ResultCode": 0, "ResultDesc": "Success"}

    except Exception as e:
        logger.error(f"ERROR processing callback: {str(e)}", exc_info=True)
        return {"ResultCode": 0, "ResultDesc": "Success"}


# ── Debug Endpoints (only in DEBUG mode) ──────────────────────
if settings.DEBUG:
    @app.post("/api/v1/payments/callback/debug")
    async def mpesa_callback_debug(request: Request):
        debug_data = await request.json()
        logger.info(f"🔧 DEBUG CALLBACK: {json.dumps(debug_data, indent=2)}")
        return {"ResultCode": 0, "ResultDesc": "Debug received", "simulated": True}

    @app.get("/api/v1/payments/callback/health")
    async def callback_health():
        return {
            "status": "healthy",
            "callback_url": f"{settings.MPESA_CALLBACK_URL}",
        }

    @app.get("/api/v1/database/health")
    async def database_health():
        from .core.database import SessionLocal
        from sqlalchemy import text
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            return {"status": "healthy", "message": "Database connection successful"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}