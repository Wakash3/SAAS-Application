from celery import Celery
from celery.schedules import crontab
from ..core.config import settings

# Add SSL cert reqs to Redis URL for Upstash compatibility
def _fix_redis_url(url: str) -> str:
    if url and url.startswith("rediss://") and "ssl_cert_reqs" not in url:
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}ssl_cert_reqs=CERT_NONE"
    return url

broker_url = _fix_redis_url(settings.CELERY_BROKER_URL)
backend_url = _fix_redis_url(settings.REDIS_URL)

app = Celery(
    "msingi",
    broker=broker_url,
    backend=backend_url,
)

# SSL configuration for Upstash Redis
app.conf.broker_use_ssl = {"ssl_cert_reqs": "CERT_NONE"}
app.conf.redis_backend_use_ssl = {"ssl_cert_reqs": "CERT_NONE"}

app.conf.beat_schedule = {
    "nightly-stocktake": {
        "task": "app.tasks.stocktake.run_nightly_stocktake",
        "schedule": crontab(hour=6, minute=0),  # 6am EAT daily
    },
    "reconcile-mpesa": {
        "task": "app.tasks.reconciliation.reconcile_pending_mpesa",
        "schedule": 120.0,  # every 2 minutes
    },
    "low-stock-alerts": {
        "task": "app.tasks.alerts.check_low_stock",
        "schedule": crontab(hour=8, minute=0),  # 8am daily
    },
}

app.conf.timezone = "Africa/Nairobi"
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]