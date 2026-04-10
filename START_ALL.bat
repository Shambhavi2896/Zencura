@echo off
REM Zencura HMS - One-Click Service Launcher (Windows)
REM This batch file starts all required services

echo.
echo ============================================================
echo  ZENCURA HMS - SERVICE LAUNCHER
echo ============================================================
echo.

REM Get project root
cd /d "%~dp0"
set PROJECT_ROOT=%cd%

echo [INFO] Project Root: %PROJECT_ROOT%
echo [INFO] Starting all services...
echo.

REM Check if Redis is running by trying to connect
echo [1/3] Checking Redis...
python -c "import redis; redis.Redis(host='127.0.0.1', port=6379).ping(); print('[OK] Redis is running')" 2>nul
if %errorlevel% neq 0 (
    echo [!] Redis not found. Starting Redis via WSL...
    start "Redis Server" wsl redis-server
    timeout /t 2 /nobreak
)

echo [2/3] Starting Celery Worker...
start "Celery Worker" cmd /k "cd /d %PROJECT_ROOT% && python -m celery -A backend.core.celery_worker worker --loglevel=info"
timeout /t 2 /nobreak

echo [3/3] Starting Flask App...
start "Flask App - Zencura HMS" cmd /k "cd /d %PROJECT_ROOT% && python app.py"

echo.
echo ============================================================
echo  All services launched!
echo ============================================================
echo.
echo Redis Server: 127.0.0.1:6379
echo Celery Worker: Processing tasks
echo Flask App: http://localhost:5000
echo.
echo Next: Open http://localhost:5000 in your browser
echo.
pause
