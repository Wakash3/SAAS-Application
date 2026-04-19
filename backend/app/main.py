from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from .core.config import settings
from .routers import auth, chat, products, fuel, sales, inventory, stocktake, payments, erp, reports, webhooks

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

for r in [auth, chat, products, fuel, sales, inventory, stocktake, payments, erp, reports, webhooks]:
    app.include_router(r.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}