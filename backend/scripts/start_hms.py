import subprocess
import sys
import time
import os
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[2]

def print_header(text):
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50 + "\n")

def check_redis():
    print("[*] Checking Redis connection...")
    try:
        import redis
        r = redis.Redis(host="127.0.0.1", port=6379, socket_connect_timeout=1)
        r.ping()
        print("✓ Redis is running")
        return True
    except Exception as e:
        print(f"✗ Redis is not running: {e}")
        print("  Please start Redis before continuing:")
        print("  - Windows: redis-server (if installed)")
        print("  - Linux/Mac: redis-server")
        return False

def start_service(name, command, logfile=None):
    print(f"[*] Starting {name}...")
    try:
        if logfile:
            with open(logfile, "w") as log:
                subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        else:
            subprocess.Popen(command)
        print(f"✓ {name} started")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"✗ Failed to start {name}: {e}")
        return False

def main():
    print_header("ZenCura Hospital Management System - Startup")
    print("Configuration Check:")
    print("- Flask App: http://localhost:5000")
    print("- Database: SQLite (hms.db)")
    print("- Cache: Redis (127.0.0.1:6379)")
    print("- Task Broker: Redis")
    print_header("Step 1: Checking Redis")
    if not check_redis():
        response = input("\nContinue anyway? (y/n): ").lower()
        if response != "y":
            print("Startup cancelled.")
            return False
    log_dir = PROJECT_ROOT / "backend" / "logs"
    log_dir.mkdir(exist_ok=True)
    print_header("Step 2: Starting Flask Application")
    flask_log = log_dir / "flask.log"
    start_service(
        "Flask Development Server",
        [sys.executable, str(PROJECT_ROOT / "app.py")],
        str(flask_log),
    )
    print_header("Step 3: Starting Celery Worker")
    worker_log = log_dir / "celery_worker.log"
    start_service(
        "Celery Worker",
        [
            sys.executable,
            "-m",
            "celery",
            "-A",
            "backend.core.celery_worker.celery_app",
            "worker",
            "--loglevel=info",
        ],
        str(worker_log),
    )
    print_header("Step 4: Starting Celery Beat (Scheduler)")
    beat_log = log_dir / "celery_beat.log"
    start_service(
        "Celery Beat Scheduler",
        [
            sys.executable,
            "-m",
            "celery",
            "-A",
            "backend.core.celery_worker.celery_app",
            "beat",
            "--loglevel=info",
        ],
        str(beat_log),
    )
    print_header("HMS Services Started Successfully!")
    print("Web Application:")
    print("  → http://localhost:5000")
    print("\nMonitoring Tools:")
    print(
        "  → Celery Flower: http://localhost:5555 (optional, requires 'pip install flower')"
    )
    print("\nLog Files:")
    print(f"  → Flask: {flask_log}")
    print(f"  → Celery Worker: {worker_log}")
    print(f"  → Celery Beat: {beat_log}")
    print("\nScheduled Tasks:")
    print("  → Daily Reminders: 08:00 AM (every day)")
    print("  → Monthly Reports: 1st of month at 00:00")
    print("\nTo stop services: Use Ctrl+C or close the terminal windows")
    print("\n" + "=" * 50)
    return True
if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nServices running in background...")
            print("Press Ctrl+C to stop (this window)...")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutdown signal received. Stopping services...")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
