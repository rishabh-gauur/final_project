import os
from twilio.rest import Client
from plyer import notification
from dotenv import load_dotenv
import requests

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def send_sms_alert(mobile_number, patient_name, ward, bed, patient_data, risk_probability):
    message_body = f"CRITICAL: {patient_name} in {ward} / Bed {bed}! (Risk: {risk_probability:.1%})\nVitals: SpO2={patient_data.get('spo2')}%, HR={patient_data.get('heart_rate')} bpm, BP={patient_data.get('bp')}, Resp={patient_data.get('resp_rate')}\nPlease check patient immediately."

    
    # 1. Fire native Windows Push Notification
    try:
        notification.notify(
            title="URGENT HEALTH ALERT",
            message=message_body,
            app_name="HealthAlert System",
            timeout=10
        )
    except Exception as e:
        print(f"OS notification failed: {e}")

    # 2. Fire Pushover Notification (Replacing SMS)
    pushover_user_key = os.environ.get('PUSHOVER_USER_KEY')
    pushover_app_token = os.environ.get('PUSHOVER_APP_TOKEN')
    
    if not pushover_user_key or not pushover_app_token or pushover_app_token == 'your_app_token_here':
        print("[error] Pushover not fully configured in .env file!")
        return False
        
    try:
        print("Sending Pushover Mobile Notification...")
        resp = requests.post("https://api.pushover.net/1/messages.json", data={
            "token": pushover_app_token,
            "user": pushover_user_key,
            "message": message_body,
            "title": "URGENT HEALTH ALERT"
        })
        if resp.ok:
            print(f"[success] Pushover Mobile Notification sent successfully!")
        else:
            print(f"[error] Failed to send Pushover notification: {resp.text}")
    except Exception as e:
        print(f"[error] Pushover request failed: {e}")

    return True
