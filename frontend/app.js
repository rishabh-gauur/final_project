const API_BASE = 'http://localhost:5000/api';

if ("Notification" in window && Notification.permission !== "granted" && Notification.permission !== "denied") {
    Notification.requestPermission();
}


function toggleAuth(type) {
    if (type === 'signup') {
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('signup-section').style.display = 'block';
    } else {
        document.getElementById('signup-section').style.display = 'none';
        document.getElementById('login-section').style.display = 'block';
    }
}

function logout() {
    localStorage.removeItem('nurse');
    window.location.href = 'index.html';
}

const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const user_id = document.getElementById('login-id').value;
        const password = document.getElementById('login-password').value;
        
        try {
            const res = await fetch(`${API_BASE}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id, password })
            });
            const data = await res.json();
            
            if (res.ok) {
                localStorage.setItem('nurse', JSON.stringify(data.nurse));
                window.location.href = 'dashboard.html';
            } else {
                alert(data.error || 'Login failed');
            }
        } catch (err) {
            alert('Could not connect to server. Ensure backend is running.');
        }
    });
}

const signupForm = document.getElementById('signup-form');
if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('signup-name').value;
        const user_id = document.getElementById('signup-id').value;
        const password = document.getElementById('signup-pass').value;
        const mobile_number = document.getElementById('signup-mobile').value;
        
        try {
            const res = await fetch(`${API_BASE}/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, user_id, password, mobile_number })
            });
            const data = await res.json();
            
            if (res.ok) {
                alert('Account created! You can now log in.');
                toggleAuth('login');
            } else {
                alert(data.error || 'Signup failed');
            }
        } catch (err) {
            alert('Could not connect to server.');
        }
    });
}

const predictForm = document.getElementById('predict-form');
if (predictForm) {
    predictForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const nurse = JSON.parse(localStorage.getItem('nurse'));
        if (!nurse) return;
        
        const patient_data = {
            heart_rate: parseFloat(document.getElementById('hr').value),
            systolic_bp: parseFloat(document.getElementById('sys_bp').value),
            diastolic_bp: parseFloat(document.getElementById('dia_bp').value),
            spo2: parseFloat(document.getElementById('spo2').value),
            temperature: parseFloat(document.getElementById('temp').value)
        };
        
        try {
            const res = await fetch(`${API_BASE}/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nurse_id: nurse.id,
                    patient_data: patient_data
                })
            });
            
            const data = await res.json();
            if (res.ok) {
                document.getElementById('res-prob').innerText = `${(data.risk_probability * 100).toFixed(1)}%`;
                document.getElementById('res-diag').innerText = data.is_high_risk ? 'CRITICAL RISK DETECTED' : 'NORMAL';
                document.getElementById('res-diag').style.color = data.is_high_risk ? 'var(--danger)' : 'var(--success)';
                
                document.getElementById('alert-box').style.display = data.is_high_risk ? 'block' : 'none';
                document.getElementById('safe-box').style.display = data.is_high_risk ? 'none' : 'block';
                
                if (data.is_high_risk && "Notification" in window && Notification.permission === "granted") {
                    new Notification("🚨 URGENT MEDICAL NOTIFICATION", {
                        body: `High risk detected! Probability: ${(data.risk_probability * 100).toFixed(1)}%\nPlease tend to the patient immediately!`,
                        requireInteraction: true
                    });
                }
            } else {
                alert(data.error || 'Prediction failed');
            }
        } catch (err) {
            alert('Could not connect to server.');
        }
    });
}
