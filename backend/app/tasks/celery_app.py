from celery import Celery
from celery.schedules import crontab
from ..core.config import settings

app = Celery(
    "msingi",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.REDIS_URL,
)

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