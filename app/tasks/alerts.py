from .celery_app import app

@app.task
def check_low_stock():
    """Check for low stock alerts"""
    print("Checking low stock...")
    return {"status": "completed", "task": "low-stock-alerts"}