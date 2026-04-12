import os
import logging
from celery import Celery
from celery.schedules import crontab
logger = logging.getLogger(__name__)
_app = None

def get_app():
    global _app
    if _app is None:
        from app import create_app
        _app = create_app()
    return _app

def make_celery(app=None):
    if app is None:
        app = get_app()
    celery = Celery(
        app.import_name,
        broker=os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0"),
        backend=os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0"),
    )
    celery.conf.update(app.config)
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    celery.Task = ContextTask
    return celery
celery_app = make_celery()
try:
    import backend.tasks.daily_reminder
    import backend.tasks.monthly_report
    import backend.tasks.export_csv
except ImportError as e:
    logger.warning(f"Task import failed: {e}")
