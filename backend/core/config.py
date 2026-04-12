from datetime import timedelta
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
INSTANCE_DIR = BASE_DIR / "backend" / "instance"

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{INSTANCE_DIR / 'hms.db'}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET_KEY", "dev-jwt-secret-key-change-in-production"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    CACHE_DEFAULT_TIMEOUT = 300
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0"
    )
    CELERY_TASK_SERIALIZER = "json"
    CELERY_RESULT_SERIALIZER = "json"
    CELERY_ACCEPT_CONTENT = ["json"]
    CELERY_TIMEZONE = "Asia/Kolkata"
    CELERY_ENABLE_UTC = False
    CELERY_IMPORTS = [
        "backend.tasks.daily_reminder",
        "backend.tasks.monthly_report",
        "backend.tasks.export_csv",
        "backend.tasks.send_appointment_confirmation",
    ]
    from celery.schedules import crontab
    CELERY_BEAT_SCHEDULE = {
        "send-daily-reminders": {
            "task": "backend.tasks.daily_reminder.send_daily_reminders",
            "schedule": crontab(hour=1, minute=30),
        },
        "generate-monthly-report": {
            "task": "backend.tasks.monthly_report.generate_monthly_report",
            "schedule": crontab(day_of_month=1, hour=1, minute=30),
        },
    }
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "shambhaviv116@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "uzbcsehlscuvphjm")
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER", "Zencura Hospital <shambhaviv116@gmail.com>"
    )
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{INSTANCE_DIR / 'hms.db'}")

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost/hms"
    )

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    config_map = {
        "production": ProductionConfig,
        "testing": TestingConfig,
        "development": DevelopmentConfig,
    }
    return config_map.get(env, DevelopmentConfig)
