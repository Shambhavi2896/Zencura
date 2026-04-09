from celery import Celery
from celery.schedules import crontab
from app import app as flask_app

def make_celery(app):
    celery = Celery(
        app.import_name, 
        backend='redis://127.0.0.1:6379/0',
        broker='redis://127.0.0.1:6379/0'
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery_app = make_celery(flask_app)

# Import tasks explicitly so Celery sees them when booting the worker
import tasks.daily_reminder
import tasks.monthly_report
import tasks.export_csv

celery_app.conf.beat_schedule = {
    'send_daily_reminders': {
        'task': 'tasks.daily_reminder.send_reminders',
        'schedule': crontab(hour=8, minute=0)  # Every morning at 8:00 AM
    },
    'generate_monthly_reports': {
        'task': 'tasks.monthly_report.generate_reports',
        'schedule': crontab(minute=0, hour=0, day_of_month='1')  # 1st of every month
    }
}
