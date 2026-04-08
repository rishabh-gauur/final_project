// Shared Notification Engine for Hospital Monitoring System
// This script handles polling the API for new anomaly alerts and displaying them as Toast "Dialogue Boxes"

(function() {
    // Configuration
    // If we are on Render, use relative path. Otherwise, use the fallback Render URL.
    const API_BASE = window.location.hostname.includes('onrender.com') ? '' : 'https://final-project-jjw5.onrender.com';
    const POLL_INTERVAL = 4000; // 4 seconds
    let lastNotificationId = null;

    // Inject Toast HTML if not present
    function injectToastUI() {
        if (document.getElementById('notificationToast')) return;
        
        const toastHtml = `
            <div id="notificationToast" style="position: fixed; top: 20px; right: 20px; background-color: #ef4444; color: white; padding: 1.25rem; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); display: none; z-index: 9999; max-width: 380px; border-left: 6px solid #7f1d1d; font-family: 'Inter', sans-serif; animation: slideIn 0.3s ease-out;">
                <div style="display: flex; align-items: flex-start; gap: 12px;">
                    <div style="font-size: 1.5rem;">⚠️</div>
                    <div>
                        <h4 style="margin:0 0 0.25rem 0; font-weight: 800; letter-spacing: 0.02em; text-transform: uppercase; font-size: 0.9rem;">Urgent Patient Alert</h4>
                        <p id="notificationText" style="margin:0; font-size: 0.95rem; line-height: 1.5; font-weight: 500;"></p>
                    </div>
                </div>
                <button onclick="this.parentElement.style.display='none'" style="position: absolute; top: 8px; right: 8px; background: none; border: none; color: white; opacity: 0.7; cursor: pointer; font-size: 1.2rem;">&times;</button>
            </div>
            <style>
                @keyframes slideIn { from { transform: translateX(110%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
            </style>
        `;
        document.body.insertAdjacentHTML('beforeend', toastHtml);
    }

    async function fetchNotifications() {
        const nurseStr = localStorage.getItem('nurse');
        if (!nurseStr) return;
        
        try {
            const user = JSON.parse(nurseStr);
            const res = await fetch(`${API_BASE}/api/notifications/${user.id}`);
            const data = await res.json();
            
            if (data.success && data.notifications.length > 0) {
                const latest = data.notifications[0];
                const uniqueId = `${latest.ward}-${latest.bed}-${latest.timestamp}`;
                
                if (uniqueId !== lastNotificationId) {
                    lastNotificationId = uniqueId;
                    showToast(latest);
                }
            }
        } catch (e) {
            console.warn('Notification poll failed:', e);
        }
    }

    function showToast(n) {
        const toast = document.getElementById('notificationToast');
        const text = document.getElementById('notificationText');
        
        text.innerHTML = `<strong>${n.patient_name}</strong> in ${n.ward} / Bed ${n.bed}<br/>${n.message}`;
        toast.style.display = 'block';
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            toast.style.display = 'none';
        }, 10000);
    }

    // Initialize
    window.addEventListener('DOMContentLoaded', () => {
        injectToastUI();
        // Start polling
        setInterval(fetchNotifications, POLL_INTERVAL);
        fetchNotifications(); // Initial check
    });
})();
