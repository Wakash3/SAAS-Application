from .celery_app import app

@app.task
def run_nightly_stocktake():
    """Run nightly stocktake snapshot"""
    print("Running nightly stocktake...")
    return {"status": "completed", "task": "nightly-stocktake"}