#!/usr/bin/env python3
"""
Zencura HMS - Complete Setup & Launcher Script
Starts Redis, Celery Worker, and Flask App
Windows-optimized with multiple terminal support
"""

import subprocess
import sys
import os
import time
import platform

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}→ {text}{Colors.END}")

def check_redis():
    """Check if Redis is accessible"""
    print_info("Checking Redis connection...")
    try:
        import redis
        r = redis.Redis(host='127.0.0.1', port=6379, db=0)
        r.ping()
        print_success("Redis is running on 127.0.0.1:6379")
        return True
    except Exception as e:
        print_error(f"Redis not accessible: {e}")
        print_info("Trying to start Redis in WSL...")
        return False

def start_redis_wsl():
    """Start Redis via WSL"""
    print_info("Starting Redis server via WSL...")
    try:
        subprocess.Popen(["wsl", "redis-server"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        time.sleep(2)
        print_success("Redis started via WSL")
        return True
    except Exception as e:
        print_error(f"Failed to start Redis: {e}")
        return False

def open_terminal_window(title, command):
    """Open a new terminal window on Windows"""
    if platform.system() == "Windows":
        # Create a batch command that opens a new PowerShell window
        ps_command = f'Start-Process powershell -ArgumentList "-NoExit", "-Command", \'{command}\''
        subprocess.Popen(["powershell", "-Command", ps_command])
        print_success(f"Opened terminal: {title}")
    else:
        # For other systems
        subprocess.Popen(command, shell=True)

def main():
    print_header("ZENCURA HMS - SERVICE LAUNCHER")
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    print_info(f"Project Root: {project_root}")
    print_info(f"Python Version: {sys.version.split()[0]}")
    print_info(f"Platform: {platform.system()}")
    
    # Step 1: Check/Start Redis
    print_header("Step 1: Redis Server")
    if not check_redis():
        if not start_redis_wsl():
            print_error("Redis setup aborted. Please start Redis manually:")
            print_info("  wsl redis-server")
            sys.exit(1)
    
    time.sleep(1)
    
    # Step 2: Start Celery Worker
    print_header("Step 2: Celery Worker")
    print_info("Starting Celery worker in new terminal...")
    celery_cmd = f"cd {project_root} && python -m celery -A backend.core.celery_worker worker --loglevel=info"
    open_terminal_window("Celery Worker", celery_cmd)
    time.sleep(2)
    print_success("Celery worker terminal opened")
    
    # Step 3: Start Flask App
    print_header("Step 3: Flask Application")
    print_info("Starting Flask app in new terminal...")
    flask_cmd = f"cd {project_root} && python app.py"
    open_terminal_window("Flask App", flask_cmd)
    time.sleep(1)
    print_success("Flask app terminal opened")
    
    # Summary
    print_header("STARTUP COMPLETE")
    print_success("All services launched!")
    print("\nServices running:")
    print(f"  {Colors.GREEN}✓ Redis Server{Colors.END} - 127.0.0.1:6379")
    print(f"  {Colors.GREEN}✓ Celery Worker{Colors.END} - Processing tasks")
    print(f"  {Colors.GREEN}✓ Flask App{Colors.END} - http://localhost:5000")
    
    print("\nNext steps:")
    print("  1. Open http://localhost:5000 in your browser")
    print("  2. Login with admin credentials")
    print("  3. Go to Admin Dashboard -> Generate Monthly Report")
    print("  4. Watch Celery terminal for task execution")
    print("  5. Check Reports page to see generated HTML")
    
    print("\nTo stop all services:")
    print("  - Close each terminal window individually")
    print("  - Or Ctrl+C in each window")
    print("")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
