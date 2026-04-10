import requests
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Get token
login_resp = requests.post('http://127.0.0.1:5000/api/login', json={
    'username': 'admin',
    'password': 'adminpassword'
})

if login_resp.status_code == 200:
    data = login_resp.json()
    print(f"Login response: {json.dumps(data, indent=2)}")
    
    # Try both token and access_token keys
    token = data.get('access_token') or data.get('token')
    print(f"\n✓ Auth token obtained: {token[:20]}...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test reports dashboard summary
    resp = requests.get('http://127.0.0.1:5000/api/reports/dashboard-summary', headers=headers)
    print(f"\nReports dashboard-summary: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"Error: {resp.text}")
    
    # Test appointment analytics
    resp = requests.get('http://127.0.0.1:5000/api/reports/analytics/appointments?days=30', headers=headers)
    print(f"\nReports analytics/appointments: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Keys: {list(data.keys())}")
        print(f"Sample data: {json.dumps({k: str(type(v)) for k, v in data.items()}, indent=2)}")
    else:
        print(f"Error: {resp.text}")
        
    # Test payments
    resp = requests.get('http://127.0.0.1:5000/api/payments', headers=headers)
    print(f"\nPayments endpoint: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Payments count: {len(data)}")
        if len(data) > 0:
            print(f"First payment: {json.dumps(data[0], indent=2)}")
    else:
        print(f"Error: {resp.text}")
else:
    print(f"Login failed: {login_resp.status_code}")
    print(login_resp.text)
