from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db_connection
from notifier import send_sms_alert
import joblib
import os
import sqlite3
import pandas as pd

app = Flask(__name__)
CORS(app) # Enable CORS for frontend integration

# Load ML Model
current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, '..', 'ml', 'model.pkl')
try:
    model = joblib.load(model_path)
    print("ML Model loaded successfully.")
except Exception as e:
    print(f"WARNING: Could not load ML model from {model_path}. Make sure to run train_model.py first.")
    print(e)
    model = None

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    user_id = data.get('user_id')
    password = data.get('password') # In production this MUST be hashed
    mobile_number = data.get('mobile_number')
    
    if not all([name, user_id, password, mobile_number]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO nurses (name, user_id, password, mobile_number) VALUES (?, ?, ?, ?)',
            (name, user_id, password, mobile_number)
        )
        conn.commit()
        conn.close()
        return jsonify({'message': 'Signup successful'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'User ID already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('user_id')
    password = data.get('password')
    
    if not user_id or not password:
        return jsonify({'error': 'Missing user_id or password'}), 400
        
    conn = get_db_connection()
    nurse = conn.execute(
        'SELECT * FROM nurses WHERE user_id = ? AND password = ?', 
        (user_id, password)
    ).fetchone()
    conn.close()
    
    if nurse:
        nurse_data = dict(nurse)
        del nurse_data['password'] # Remove password from response
        return jsonify({'message': 'Login successful', 'nurse': nurse_data}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json
    patient_data = data.get('patient_data')
    nurse_id = data.get('nurse_id')
    
    if not patient_data or not nurse_id:
        return jsonify({'error': 'Missing patient_data or nurse_id'}), 400
        
    if model is None:
        return jsonify({'error': 'ML model not loaded on server'}), 500
        
    try:
        # Prepare data for prediction
        df = pd.DataFrame([{
            'heart_rate': patient_data['heart_rate'],
            'systolic_bp': patient_data['systolic_bp'],
            'diastolic_bp': patient_data['diastolic_bp'],
            'spo2': patient_data['spo2'],
            'temperature': patient_data['temperature']
        }])
        
        prediction = model.predict(df)[0]
        probabilities = model.predict_proba(df)[0]
        risk_prob = probabilities[1]
        
        is_high_risk = bool(prediction == 1)
        
        result = {
            'risk_level': int(prediction),
            'risk_probability': float(risk_prob),
            'is_high_risk': is_high_risk,
            'alert_sent': False
        }
        
        if is_high_risk:
            conn = get_db_connection()
            nurse = conn.execute('SELECT mobile_number FROM nurses WHERE id = ?', (nurse_id,)).fetchone()
            conn.close()
            
            if nurse:
                mobile_number = nurse['mobile_number']
                send_sms_alert(mobile_number, patient_data, risk_prob)
                result['alert_sent'] = True
                
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
