from app.tasks.celery_app import app
from app.tasks import stocktake, reconciliation, alerts

# This ensures tasks are registered
app.autodiscover_tasks(['app.tasks'])

if __name__ == '__main__':
    app.start()