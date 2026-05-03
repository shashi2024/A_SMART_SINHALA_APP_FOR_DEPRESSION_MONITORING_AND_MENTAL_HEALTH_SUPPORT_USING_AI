import requests
import json
import time

base_url = 'http://127.0.0.1:8000/api'
user_id = 'VYhYDBJ9T7Oqpe29aCUk'

# Mock Data
accelerometer_data = json.dumps([
    {"x": 0.1, "y": 0.2, "z": 9.8, "timestamp": "2026-05-03T12:00:00Z"},
    {"x": 0.2, "y": 0.3, "z": 9.7, "timestamp": "2026-05-03T12:00:01Z"}
])
rr_intervals = json.dumps([800, 810, 790, 805])

print("1. Sending mock biofeedback assessment...")
# We use files but we can just send empty files or skip them if the endpoint handles them as optional or handles errors gracefully
try:
    # Biofeedback endpoint expects Form data and files
    data = {
        'accelerometer_data': accelerometer_data,
        'rr_intervals': rr_intervals
    }
    
    response = requests.post(f"{base_url}/analyze/biofeedback?user_id={user_id}", data=data)
    print("Response Status:", response.status_code)
    
    res_data = response.json()
    if res_data.get('status') == 'success':
        print("[OK] Assessment successfully processed!")
    else:
        print("[FAILED] Response:", res_data)
        
except Exception as e:
    print("[ERROR] Failed to send assessment:", e)

# Wait a second for firestore sync
time.sleep(2)

print("\n2. Checking Admin Profile endpoint for the saved data...")
try:
    admin_response = requests.get(f"{base_url}/admin/users/{user_id}/profile")
    if admin_response.status_code == 200:
        profile = admin_response.json()
        bio_history = profile.get('biofeedback', [])
        print(f"Found {len(bio_history)} biofeedback records for user in Admin Panel!")
        
        if len(bio_history) > 0:
            print("Latest record timestamp:", bio_history[0].get('timestamp'))
            print("Latest record created_at:", bio_history[0].get('created_at'))
            print("Latest record final_assessment:", bio_history[0].get('final_assessment'))
    else:
        print("Admin endpoint returned:", admin_response.status_code, admin_response.text)
except Exception as e:
    print("[ERROR] Failed to check admin profile:", e)

