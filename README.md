# Zencura HMS - Quick Launch Guide

## 🚀 Start Everything (Easiest)

**Option 1: Python Script** (Recommended)

```powershell
python setup.py
```

**Option 2: Batch File**

```bash
START_ALL.bat
```

## ✅ What Gets Started

The setup script automatically launches:

1. **Redis Server** - Message broker for Celery
   - Auto-detects if already running
   - Starts via WSL if needed
   - Accessible at: `127.0.0.1:6379`

2. **Celery Worker** - Task processor (new terminal)
   - Processes background jobs
   - Monitoring: Watch terminal for task execution logs
   - Command: `python -m celery -A backend.core.celery_worker worker --loglevel=info`

3. **Flask App** - Web application (new terminal)
   - Open: http://localhost:5000
   - Login with: `admin` / `adminpassword`

## 📝 Using the Monthly Report Feature

1. Login to the dashboard
2. Navigate to **Admin Dashboard**
3. Click **"Generate Monthly Report"** button
4. Watch the **Celery Worker terminal** - you'll see:
   ```
   [tasks] . backend.tasks.monthly_report.generate_monthly_report
   [2026-04-10 ...] Task processing...
   [2026-04-10 ...] Report generated: Monthly_Report_March_2026.html
   ```
5. Go to **Reports → Generated Monthly Archives**
6. Your HTML report will appear in the list!

## 🛠️ Manual Service Control

**Start only if needed individually:**

```powershell
# Terminal 1 - Redis (via WSL)
wsl redis-server

# Terminal 2 - Celery Worker
python -m celery -A backend.core.celery_worker worker --loglevel=info

# Terminal 3 - Flask App
python app.py
```

## ❌ Stopping Services

- Close each terminal window
- Or press `Ctrl+C` in each window
- Services stop gracefully

## 🔧 Troubleshooting

**Redis won't start?**

- Restart WSL: `wsl --shutdown`
- Or install Redis natively (see REDIS_SETUP.md)

**Celery showing errors?**

- Check that Redis is running first
- Verify CELERY_BROKER_URL in config.py

**Flask app won't start?**

- Port 5000 already in use?
- Try: `python app.py --port 5001`

**Tasks not executing?**

- Ensure Celery Worker terminal is open and shows "Ready to accept tasks"
- Check Celery terminal for error messages

## 📊 Monitor Task Execution

Watch the **Celery Worker terminal** for real-time task execution:

```
[INFO] Starting new beat schedule...
[INFO] Scheduler: Sending due task send_daily_reminders (tasks.daily_reminder.send_daily_reminders)
[INFO] Task processing complete
```

## 🎯 Test It Now

```bash
python setup.py        # Start everything
# Wait 5 seconds...
# Open http://localhost:5000
# Login → Admin Dashboard → Generate Monthly Report
```

---

**Configuration files:**

- Database: `backend/core/config.py`
- Celery tasks: `backend/tasks/`
- Routes: `backend/routes/`

**Login Credentials**
Admin Login: admin / adminpassword
Test Doctor: doctor1 / doctor123
Test Patient: abc / abc12345
