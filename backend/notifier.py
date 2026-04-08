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
        error_msg = "!!! [CRITICAL CONFIG ERROR] Pushover keys (User Key or App Token) are missing from Render Dashboard! Mobile push will NOT work until you add them."
        print("\n" + "!"*80)
        print(f"{error_msg}")
        print("!"*80 + "\n")
        return False, error_msg

    try:
        print(f"DEBUG: Attempting Pushover Broadcast to Account ID for patient {patient_name}...")
        resp = requests.post("https://api.pushover.net/1/messages.json", data={
            "token": pushover_app_token,
            "user": pushover_user_key,
            "message": message_body,
            "title": "URGENT HEALTH ALERT",
            "priority": 1
        })
        if resp.ok:
            print(f"[success] Pushover Mobile Push sent perfectly to your account!")
            return True, "Alert sent to your Pushover App!"
        else:
            error_msg = f"!!! [API REJECTED] Pushover returned an error: {resp.text}. Check if your keys are valid."
            print(f"\n{error_msg}\n")
            return False, error_msg
    except Exception as e:
        error_msg = f"!!! [NETWORK ERROR] Failed to reach Pushover API: {str(e)}"
        print(f"\n{error_msg}\n")
        return False, error_msg

    return False, "Unknown Error"
