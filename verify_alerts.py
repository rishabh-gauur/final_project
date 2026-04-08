import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from notifier import send_mobile_push
    print("[ok] Notifier module (New Broadcast Mode) imported successfully.")
except ImportError as e:
    print(f"[error] Failed to import notifier: {e}")
    sys.exit(1)

def test_alert():
    print("\n--- Starting Automatic Broadcast Test ---")
    
    # Mock data
    dummy_name = "SIMULATED CRITICAL PATIENT"
    dummy_ward = "Ward A"
    dummy_bed = "A1"
    dummy_vitals = {
        'spo2': 82,
        'heart_rate': 145,
        'bp': '170/110',
        'resp_rate': 32
    }
    dummy_prob = 0.98

    print(f"Broadcasting urgent push alert for {dummy_name}...")
    
    # Check environment variables
    pushover_user = os.environ.get('PUSHOVER_USER_KEY')
    pushover_app = os.environ.get('PUSHOVER_APP_TOKEN')
    
    if not pushover_user or not pushover_app:
        print("[warning] PUSHOVER credentials not found in environment!")
        print("NOTE: On Render, you MUST set these in the dashboard Environment Variables.")
    
    success, msg = send_mobile_push(dummy_name, dummy_ward, dummy_bed, dummy_vitals, dummy_prob)
    
    if success:
        print(f"\n[success] {msg}")
        print("Note: You should have also seen a Windows Notification box on this laptop.")
        print("Check all devices logged into your Pushover ID.")
    else:
        print(f"\n[fail] Alert failed: {msg}")
        print("Check your .env file keys locally, and Environment Variables on Render.")

if __name__ == "__main__":
    test_alert()
