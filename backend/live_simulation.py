import json
import time
import random
import os
import threading
import pandas as pd
import joblib
from datetime import datetime
from database import get_db_connection
from notifier import send_sms_alert

DIR_PATH = os.path.dirname(__file__)
LIVE_DATA_FILE = os.path.join(DIR_PATH, 'live_patients.json')
NOTIFICATIONS_FILE = os.path.join(DIR_PATH, 'notifications.json')

MODEL_PATH = os.path.join(DIR_PATH, '..', 'ml', 'model.pkl')

# Initialize 2 wards, 10 beds each
wards = {
    'Ward A': {f'A{i}': None for i in range(1, 11)},
    'Ward B': {f'B{i}': None for i in range(1, 11)}
}

# Pre-populate some beds with patients
patient_counter = 1
for w in wards:
    for b in wards[w]:
        if random.random() > 0.3: # 70% occupancy
            wards[w][b] = {
                'id': f'PT-{patient_counter:04d}',
                'name': f'Patient {patient_counter}',
                'vitals': {
                    'bp': random.randint(110, 130),
                    'heart_rate': random.randint(70, 90),
                    'spo2': random.randint(96, 100),
                    'temperature': round(random.uniform(36.5, 37.2), 1),
                    'resp_rate': random.randint(12, 18),
                    'map': random.randint(75, 95),
                    'ecg': random.randint(90, 100)
                },
                'status': 'Stable',
                'risk_probability': 0.0,
                'last_sms_sent': 0.0
            }
            patient_counter += 1

def load_model():
    try:
        return joblib.load(MODEL_PATH)
    except:
        return None

def simulate_loop():
    model = load_model()
    
    while True:
        notifications = []
        for w in wards:
            for b in wards[w]:
                p = wards[w][b]
                if p:
                    # Random walk vitals
                    v = p['vitals']
                    v['bp'] += random.choice([-2, -1, 0, 1, 2])
                    v['heart_rate'] += random.choice([-2, -1, 0, 1, 2])
                    v['spo2'] += random.choice([-1, 0, 0, 1])
                    v['temperature'] = round(v['temperature'] + random.uniform(-0.1, 0.1), 1)
                    v['resp_rate'] += random.choice([-1, 0, 1])
                    v['map'] += random.choice([-2, -1, 0, 1, 2])
                    v['ecg'] += random.choice([-1, 0, 1])
                    
                    # Rarely introduce an anomaly jump
                    if random.random() < 0.10:
                        v['heart_rate'] += random.randint(20, 40)
                        v['spo2'] -= random.randint(5, 15)

                    # Bound checking
                    v['bp'] = max(40, min(250, v['bp']))
                    v['heart_rate'] = max(30, min(200, v['heart_rate']))
                    v['spo2'] = max(50, min(100, v['spo2']))
                    v['resp_rate'] = max(8, min(45, v['resp_rate']))
                    v['map'] = max(40, min(160, v['map']))
                    v['ecg'] = max(0, min(100, v['ecg']))

                    # Predict Risk
                    if model:
                        df = pd.DataFrame([v])
                        pred = model.predict(df)[0]
                        prob = model.predict_proba(df)[0][1]
                        p['risk_probability'] = float(prob)
                        
                        if pred == 1:
                            p['status'] = 'Critical'
                            
                            # Log to notifications array
                            notifications.append({
                                'ward': w,
                                'bed': b,
                                'patient_name': p['name'],
                                'message': f"Critical Vitals Detected: HR {v['heart_rate']}, SpO2 {v['spo2']}%",
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            # Check if SMS should be sent (throttle 60 seconds per patient)
                            now_time = time.time()
                            if (now_time - p.get('last_sms_sent', 0)) > 60:
                                p['last_sms_sent'] = now_time
                                try:
                                    from notifier import send_mobile_push
                                    # Automated Broadcast: Send directly to your account ID
                                    t = threading.Thread(
                                        target=send_mobile_push, 
                                        args=(p['name'], w, b, v, prob)
                                    )
                                    t.daemon = True
                                    t.start()
                                except Exception as e:
                                    print(f"Error triggering Push Alert: {e}")
                                    
                        else:
                            p['status'] = 'Stable' if prob < 0.3 else 'Observation'

        # Save Live Data
        with open(LIVE_DATA_FILE, 'w') as f:
            json.dump(wards, f)
            
        # Append Notifications (keep last 100)
        existing_nots = []
        if os.path.exists(NOTIFICATIONS_FILE):
            try:
                with open(NOTIFICATIONS_FILE, 'r') as f:
                    existing_nots = json.load(f)
            except: pass
        
        all_nots = notifications + existing_nots
        all_nots = all_nots[:100]
        
        with open(NOTIFICATIONS_FILE, 'w') as f:
            json.dump(all_nots, f)

        time.sleep(3)

def start_simulation():
    t = threading.Thread(target=simulate_loop, daemon=True)
    t.start()
    print("Live Patient Simulation Started...")

if __name__ == '__main__':
    start_simulation()
    while True:
        time.sleep(1)
