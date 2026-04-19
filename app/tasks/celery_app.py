from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Use memory broker for Windows development
app = Celery(
    "msingi",
    broker="memory://",  # In-memory broker - no Redis required
    backend="cache+memory://",  # In-memory backend - no Redis required
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
app.conf.task_always_eager = False  # Run tasks asynchronously
app.conf.worker_pool_restarts = True

# Auto-discover tasks
app.autodiscover_tasks(['app.tasks'])