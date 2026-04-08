from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db_connection
import database
from live_simulation import start_simulation, LIVE_DATA_FILE, NOTIFICATIONS_FILE
import joblib
import os
import json
import pandas as pd

import os
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('login.html')

@app.route('/<path:path>')
def serve_file(path):
    return app.send_static_file(path)

# Start Live Patient Simulator
start_simulation()

current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, '..', 'ml', 'model.pkl')
try:
    model = joblib.load(model_path)
except:
    model = None

@app.route('/api/signup', methods=['POST'])
@app.route('/api/admin/register', methods=['POST']) # Handle both
def signup():
    data = request.json
    name = data.get('name')
    username = data.get('username') or data.get('user_id')
    password = data.get('password')
    mobile = data.get('mobile_number') or data.get('phone') or ''
    email = data.get('email') or ''
    
    role = 'admin' if request.path == '/api/admin/register' else 'staff'
    
    if not name or not username or not password:
        return jsonify({'message': 'Missing required fields', 'success': False}), 400
        
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO users (name, username, email, mobile_number, password, role) VALUES (?, ?, ?, ?, ?, ?)',
            (name, username, email, mobile, password, role)
        )
        conn.commit()
        conn.close()
        
        # Determine redirect
        redirect_url = 'admin-login.html' if role == 'admin' else 'login.html'
        return jsonify({'success': True, 'redirect': redirect_url}), 201
    except Exception as e:
        return jsonify({'message': 'Username may already exist', 'error': str(e), 'success': False}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('user_id') or data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT id, name, username, role FROM users WHERE username = ? AND password = ?', 
        (username, password)
    ).fetchone()
    conn.close()
    
    if user:
        user_data = dict(user)
        redirect_url = 'admin-dashboard.html' if user['role'] == 'admin' else 'dashboard.html'
        return jsonify({'success': True, 'redirect': redirect_url, 'nurse': user_data}), 200
    else:
        return jsonify({'message': 'Invalid credentials', 'error': 'Invalid credentials', 'success': False}), 401

@app.route('/api/admin/staff', methods=['GET'])
def get_staff():
    conn = get_db_connection()
    staff = conn.execute("SELECT id, name, username FROM users WHERE role='staff'").fetchall()
    
    result = []
    for s in staff:
        s_dict = dict(s)
        allocs = conn.execute("SELECT id, ward_number, bed_number FROM allocations WHERE user_id=?", (s['id'],)).fetchall()
        s_dict['allocations'] = [dict(a) for a in allocs]
        result.append(s_dict)
        
    conn.close()
    return jsonify({'success': True, 'staff': result})

@app.route('/api/staff/<int:id>', methods=['GET'])
def get_single_staff(id):
    conn = get_db_connection()
    user = conn.execute("SELECT id, name, username FROM users WHERE id=?", (id,)).fetchone()
    if not user:
        return jsonify({'success': False})
        
    s_dict = dict(user)
    allocs = conn.execute("SELECT id, ward_number, bed_number FROM allocations WHERE user_id=?", (id,)).fetchall()
    s_dict['allocations'] = [dict(a) for a in allocs]
    conn.close()
    return jsonify({'success': True, 'data': s_dict})

@app.route('/api/admin/staff/<int:id>', methods=['DELETE'])
def delete_staff(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/allocate', methods=['POST'])
def allocate():
    data = request.json
    staff_id = data.get('staffId')
    ward = data.get('ward_number')
    bed = data.get('bed_number')
    
    conn = get_db_connection()
    # Check if bed already allocated
    existing = conn.execute("SELECT * FROM allocations WHERE ward_number=? AND bed_number=?", (ward, bed)).fetchone()
    if existing:
        conn.close()
        return jsonify({'success': False, 'message': f'Bed {bed} in {ward} is already assigned.'})
        
    conn.execute("INSERT INTO allocations (user_id, ward_number, bed_number) VALUES (?, ?, ?)", (staff_id, ward, bed))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/allocate/<int:id>', methods=['DELETE'])
def remove_allocation(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM allocations WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/ward/<ward_name>', methods=['GET'])
def get_ward_info(ward_name):
    # Load live data
    if not os.path.exists(LIVE_DATA_FILE):
        return jsonify({'success': False, 'message': 'Live data unavailable'})
        
    with open(LIVE_DATA_FILE, 'r') as f:
        wards_data = json.load(f)
        
    if ward_name not in wards_data:
        return jsonify({'success': False, 'message': 'Ward not found'})
        
    ward_obj = wards_data[ward_name]
    
    conn = get_db_connection()
    
    beds_array = []
    filled = 0
    empty = 0
    
    for bed_no, patient in ward_obj.items():
        # Get allocations
        allocs = conn.execute("SELECT u.name FROM allocations a JOIN users u ON a.user_id = u.id WHERE a.ward_number=? AND a.bed_number=?", (ward_name, bed_no)).fetchall()
        staff_names = [a['name'] for a in allocs]
        
        if patient:
            filled += 1
            beds_array.append({
                'bed_number': bed_no,
                'patient': patient,
                'staff': staff_names
            })
        else:
            empty += 1
            beds_array.append({
                'bed_number': bed_no,
                'patient': None,
                'staff': staff_names
            })
            
    conn.close()
    
    return jsonify({
        'success': True,
        'total_beds': 10,
        'filled_beds': filled,
        'empty_beds': empty,
        'beds': beds_array
    })

@app.route('/api/patient/<ward>/<bed>', methods=['GET'])
def get_patient_report(ward, bed):
    if not os.path.exists(LIVE_DATA_FILE):
        return jsonify({'success': False, 'message': 'Live data unavailable'})
    with open(LIVE_DATA_FILE, 'r') as f:
        data = json.load(f)
        
    patient = data.get(ward, {}).get(bed)
    if not patient:
         return jsonify({'success': False, 'message': 'No patient found'})
         
    return jsonify({'success': True, 'patient': patient})

@app.route('/api/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    # Get beds assigned to this user
    conn = get_db_connection()
    allocs = conn.execute("SELECT ward_number, bed_number FROM allocations WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    
    assigned_beds = [ (a['ward_number'], a['bed_number']) for a in allocs ]
    
    if not os.path.exists(NOTIFICATIONS_FILE):
        return jsonify({'success': True, 'notifications': []})
        
    with open(NOTIFICATIONS_FILE, 'r') as f:
        nots = json.load(f)
        
    # Filter notifications for assigned beds
    user_nots = [n for n in nots if (n['ward'], n['bed']) in assigned_beds]
    return jsonify({'success': True, 'notifications': user_nots[:10]})

@app.route('/api/predict', methods=['POST'])
def manual_predict():
    data = request.json['patient_data']
    if model is None: return jsonify({'error': 'No model loaded'}), 500
    df = pd.DataFrame([data])
    pred = model.predict(df)[0]
    prob = model.predict_proba(df)[0][1]
    return jsonify({
        'is_high_risk': bool(pred == 1),
        'risk_probability': float(prob),
        'alert_sent': bool(pred == 1)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
