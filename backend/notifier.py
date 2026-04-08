import os
from dotenv import load_dotenv
import requests

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def send_mobile_push(patient_name, ward, bed, patient_data, risk_probability):
    message_body = f"CRITICAL: {patient_name} in {ward} / Bed {bed}! (Risk: {risk_probability:.1%})\nVitals: SpO2={patient_data.get('spo2')}%, HR={patient_data.get('heart_rate')} bpm, BP={patient_data.get('bp')}, Resp={patient_data.get('resp_rate')}\nPlease check patient immediately."

    # 1. Fire Local Desktop Notification (Only if running on Windows/Laptop)
    try:
        from plyer import notification
        notification.notify(
            title="URGENT PATIENT ALERT",
            message=message_body,
            app_name="HealthMonitor",
            timeout=10
        )
    except Exception:
        # Expected to fail on Render/Linux, so we just pass silently
        pass

    # 2. Fire Pushover Notification (Direct to Account ID)
    pushover_user_key = os.environ.get('PUSHOVER_USER_KEY')
    pushover_app_token = os.environ.get('PUSHOVER_APP_TOKEN')
    
    if not pushover_user_key or not pushover_app_token:
        error_msg = "Pushover keys missing from Environment Variables (Check Render Dashboard!)"
        print(f"[error] {error_msg}")
        return False, error_msg

    try:
        print(f"Broadcasting Pushover Alert for {patient_name}...")
        resp = requests.post("https://api.pushover.net/1/messages.json", data={
            "token": pushover_app_token,
            "user": pushover_user_key,
            "message": message_body,
            "title": "URGENT HEALTH ALERT",
            "priority": 1
        })
        if resp.ok:
            print(f"[success] Pushover Mobile Push sent successfully!")
            return True, "Alert sent to your Pushover App!"
        else:
            return False, f"Pushover Rejected: {resp.text}"
    except Exception as e:
        return False, f"Connection Failure: {str(e)}"

    return False, "Unknown Error"
