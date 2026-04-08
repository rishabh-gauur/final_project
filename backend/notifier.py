import os
from dotenv import load_dotenv
import requests

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def send_mobile_push(patient_name, ward, bed, patient_data, risk_probability):
    message_body = f"CRITICAL: {patient_name} in {ward} / Bed {bed}! (Risk: {risk_probability:.1%})\nVitals: SpO2={patient_data.get('spo2')}%, HR={patient_data.get('heart_rate')} bpm, BP={patient_data.get('bp')}, Resp={patient_data.get('resp_rate')}\nPlease check patient immediately."

    # 1. Fire Pushover Notification (Direct to Account ID)
    pushover_user_key = os.environ.get('PUSHOVER_USER_KEY')
    pushover_app_token = os.environ.get('PUSHOVER_APP_TOKEN')
    
    if not pushover_user_key or not pushover_app_token or pushover_app_token == 'your_app_token_here':
        print("[error] Pushover not fully configured in .env or Render variables!")
        return False
        
    try:
        print(f"Broadcasting Mobile Push Alert for {patient_name}...")
        resp = requests.post("https://api.pushover.net/1/messages.json", data={
            "token": pushover_app_token,
            "user": pushover_user_key,
            "message": message_body,
            "title": "URGENT HEALTH ALERT",
            "priority": 1  # High priority bypasses quiet hours
        })
        if resp.ok:
            print(f"[success] Mobile Push Alert sent to your devices!")
            return True
        else:
            print(f"[error] API response: {resp.text}")
    except Exception as e:
        print(f"[error] Request failed: {e}")

    return False
