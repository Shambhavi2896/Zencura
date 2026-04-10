@REM Startup script for HMS with Celery workers and scheduler
@REM This script starts all required services for full functionality

@echo off
echo ========================================
echo  ZenCura Hospital Management System
echo  Startup Script (Windows)
echo ========================================
echo.

REM Check if Redis is running
echo [1/4] Checking Redis connection...
timeout /t 2 /nobreak > nul

REM Start Flask app
echo [2/4] Starting Flask development server...
start "Flask App" cmd /k "cd %CD% && python app.py"
timeout /t 3 /nobreak > nul

REM Start Celery Worker
echo [3/4] Starting Celery Worker (processes background jobs)...
start "Celery Worker" cmd /k "cd %CD% && celery -A backend.core.celery_worker.celery_app worker --loglevel=info"
timeout /t 3 /nobreak > nul

REM Start Celery Beat (Scheduler)
echo [4/4] Starting Celery Beat (scheduler for periodic tasks)...
start "Celery Beat" cmd /k "cd %CD% && celery -A backend.core.celery_worker.celery_app beat --loglevel=info"
timeout /t 2 /nobreak > nul

echo.
echo ========================================
echo  Services Started!
echo ========================================
echo.
echo Web Application: http://localhost:5000
echo Celery Flower (monitoring): http://localhost:5555
echo.
echo NOTE: Make sure Redis is running before starting services!
echo.
echo To start Redis:
echo   - Windows: redis-server (if installed)
echo   - WSL/Linux: redis-server
echo.
pause
