import os
from twilio.rest import Client
from plyer import notification
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def send_sms_alert(mobile_number, patient_data, risk_probability):
    message_body = f"URGENT: High health risk detected! (Probability: {risk_probability:.1%})\nPatient Stats: SpO2={patient_data.get('spo2')}%, HR={patient_data.get('heart_rate')} bpm, BP={patient_data.get('systolic_bp')}/{patient_data.get('diastolic_bp')}\nPlease check patient immediately."
    
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

    # 2. Fire actual Telegram Push Notification
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    if bot_token and bot_token != 'your_bot_token_here':
        import requests
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message_body
            }
            resp = requests.post(url, json=payload)
            if resp.status_code == 200:
                print("[success] Real Push Notification sent via Telegram!")
            else:
                print(f"[error] Failed to send Telegram: {resp.text}")
        except Exception as e:
            print(f"[error] Telegram request failed: {e}")
    else:
        print("\n" + "="*55)
        print("[MOCK TELEGRAM NOTIFICATION DISPATCHED] (Telegram not configured)")
        print(f"To: {mobile_number} / Telegram Chat")
        print(message_body)
        print("="*55 + "\n")
            
    return True
