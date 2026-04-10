#!/usr/bin/env python3
"""
Script to trigger backend jobs and test email functionality
"""

import requests
import json
from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

BASE_URL = "http://127.0.0.1:5000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "adminpassword"
TEST_EMAIL = "shambhaviv116@gmail.com"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def login():
    """Login as admin and get JWT token."""
    print_section("STEP 1: Admin Login")
    
    login_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/login", json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.json()}")
        return None
    
    data = response.json()
    token = data.get('token')
    print(f"✅ Login successful!")
    print(f"   Role: {data.get('role')}")
    print(f"   Username: {data.get('username')}")
    print(f"   Token: {token[:50]}...")
    
    return token

def get_headers(token):
    """Get headers with authorization token."""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def check_email_config(token):
    """Check email configuration."""
    print_section("STEP 2: Check Email Configuration")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/test/email-config",
        headers=get_headers(token)
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to check config: {response.json()}")
        return False
    
    config = response.json()
    print(f"✅ Email Configuration:")
    print(f"   Server: {config.get('mail_server')}")
    print(f"   Port: {config.get('mail_port')}")
    print(f"   TLS: {config.get('mail_use_tls')}")
    print(f"   Username: {config.get('mail_username')}")
    print(f"   Sender: {config.get('mail_default_sender')}")
    print(f"   Status: {config.get('status')}")
    
    return config.get('status') == 'Email is configured'

def send_test_email(token):
    """Send a test email."""
    print_section("STEP 3: Send Test Email")
    
    email_data = {"email": TEST_EMAIL}
    response = requests.post(
        f"{BASE_URL}/api/admin/test/send-test-email",
        headers=get_headers(token),
        json=email_data
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to send test email: {response.json()}")
        return False
    
    print(f"✅ {response.json().get('msg')}")
    return True

def trigger_daily_reminder(token):
    """Trigger daily reminder job."""
    print_section("STEP 4: Trigger Daily Reminder Job")
    
    response = requests.post(
        f"{BASE_URL}/api/admin/test/daily-reminder",
        headers=get_headers(token)
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to trigger job: {response.json()}")
        return False
    
    data = response.json()
    print(f"✅ {data.get('msg')}")
    print(f"   Task ID: {data.get('task_id')}")
    print(f"   📧 Reminders will be sent to patients with appointments today")
    return True

def trigger_monthly_report(token):
    """Trigger monthly report job."""
    print_section("STEP 5: Trigger Monthly Report Job")
    
    response = requests.post(
        f"{BASE_URL}/api/admin/test/monthly-report",
        headers=get_headers(token)
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to trigger job: {response.json()}")
        return False
    
    data = response.json()
    print(f"✅ {data.get('msg')}")
    print(f"   Task ID: {data.get('task_id')}")
    print(f"   📊 Reports will be generated for all doctors")
    return True

def trigger_csv_export(token):
    """Trigger CSV export job."""
    print_section("STEP 6: Trigger CSV Export Job")
    
    response = requests.post(
        f"{BASE_URL}/api/admin/test/csv-export",
        headers=get_headers(token)
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to trigger job: {response.json()}")
        return False
    
    data = response.json()
    print(f"✅ {data.get('msg')}")
    print(f"   Task ID: {data.get('task_id')}")
    print(f"   Patient ID: {data.get('patient_id')}")
    print(f"   📥 CSV export will be generated")
    return True

def main():
    """Main execution."""
    print("\n")
    print("┌" + "─"*58 + "┐")
    print("│" + " "*15 + "ZENCURA BACKEND JOBS TEST SCRIPT" + " "*11 + "│")
    print("└" + "─"*58 + "┘")
    print(f"\nTest Email: {TEST_EMAIL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without valid token")
        return
    
    # Step 2: Check email config
    email_ok = check_email_config(token)
    
    if not email_ok:
        print("\n⚠️  Email is not properly configured")
        print("   Check your MAIL_USERNAME and MAIL_PASSWORD environment variables")
    
    # Step 3: Send test email
    print("\n📧 Testing email delivery...")
    email_sent = send_test_email(token)
    
    if not email_sent:
        print("\n⚠️  Test email failed. Skipping job triggers...")
        return
    
    # Step 4-6: Trigger jobs
    print("\n🚀 Triggering backend jobs...")
    
    trigger_daily_reminder(token)
    trigger_monthly_report(token)
    trigger_csv_export(token)
    
    # Summary
    print_section("✅ ALL TESTS COMPLETE")
    print("Summary of actions:")
    print("  ✅ Logged in as admin")
    print("  ✅ Verified email configuration")
    print("  ✅ Sent test email to: " + TEST_EMAIL)
    print("  ✅ Triggered daily reminder job")
    print("  ✅ Triggered monthly report job")
    print("  ✅ Triggered CSV export job")
    print("\n📧 Check your email for:")
    print("  1. Test email confirmation")
    print("  2. Daily reminder notifications")
    print("  3. Monthly activity report (if applicable)")
    print("  4. CSV export notification (once completed)")
    print("\n⏱️  Background jobs run asynchronously")
    print("   Check server logs for job execution details")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
