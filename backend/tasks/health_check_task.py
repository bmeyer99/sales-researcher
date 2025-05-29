from backend.celery_app import celery_app

@celery_app.task
def health_check_task(x, y):
    """
    A simple task to check Celery worker health.
    """
    print(f"Health check task received: {x} + {y}")
    return x + y