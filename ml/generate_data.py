import pandas as pd
import numpy as np
import os

def generate_data(num_samples=1000):
    np.random.seed(42)
    
    # Healthy cases
    healthy_n = int(num_samples * 0.7)
    healthy_hr = np.random.normal(70, 10, healthy_n)
    healthy_sys_bp = np.random.normal(120, 10, healthy_n)
    healthy_dia_bp = np.random.normal(80, 5, healthy_n)
    healthy_spo2 = np.random.normal(98, 1, healthy_n)
    healthy_temp = np.random.normal(36.5, 0.3, healthy_n)
    
    healthy_df = pd.DataFrame({
        'heart_rate': healthy_hr,
        'systolic_bp': healthy_sys_bp,
        'diastolic_bp': healthy_dia_bp,
        'spo2': healthy_spo2,
        'temperature': healthy_temp,
        'risk_level': 0
    })
    
    # High risk cases
    risk_n = num_samples - healthy_n
    
    hypoxia_n = risk_n // 3
    hypoxia_hr = np.random.normal(110, 15, hypoxia_n)
    hypoxia_sys_bp = np.random.normal(110, 15, hypoxia_n)
    hypoxia_dia_bp = np.random.normal(75, 10, hypoxia_n)
    hypoxia_spo2 = np.random.normal(88, 3, hypoxia_n)
    hypoxia_temp = np.random.normal(37, 0.5, hypoxia_n)
    
    htn_n = risk_n // 3
    htn_hr = np.random.normal(90, 10, htn_n)
    htn_sys_bp = np.random.normal(175, 15, htn_n)
    htn_dia_bp = np.random.normal(110, 10, htn_n)
    htn_spo2 = np.random.normal(97, 2, htn_n)
    htn_temp = np.random.normal(36.8, 0.4, htn_n)
    
    inf_n = risk_n - hypoxia_n - htn_n
    inf_hr = np.random.normal(120, 15, inf_n)
    inf_sys_bp = np.random.normal(95, 10, inf_n)
    inf_dia_bp = np.random.normal(60, 5, inf_n)
    inf_spo2 = np.random.normal(95, 2, inf_n)
    inf_temp = np.random.normal(39.5, 0.5, inf_n)
    
    risk_df = pd.DataFrame({
        'heart_rate': np.concatenate([hypoxia_hr, htn_hr, inf_hr]),
        'systolic_bp': np.concatenate([hypoxia_sys_bp, htn_sys_bp, inf_sys_bp]),
        'diastolic_bp': np.concatenate([hypoxia_dia_bp, htn_dia_bp, inf_dia_bp]),
        'spo2': np.concatenate([hypoxia_spo2, htn_spo2, inf_spo2]),
        'temperature': np.concatenate([hypoxia_temp, htn_temp, inf_temp]),
        'risk_level': 1
    })
    
    df = pd.concat([healthy_df, risk_df]).sample(frac=1).reset_index(drop=True)
    
    df['heart_rate'] = df['heart_rate'].clip(30, 200).round()
    df['systolic_bp'] = df['systolic_bp'].clip(60, 250).round()
    df['diastolic_bp'] = df['diastolic_bp'].clip(40, 150).round()
    df['spo2'] = df['spo2'].clip(50, 100).round()
    df['temperature'] = df['temperature'].clip(34.0, 42.0).round(1)
    
    output_path = os.path.join(os.path.dirname(__file__), 'patient_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated {num_samples} patient records and saved to {output_path}")

if __name__ == '__main__':
    generate_data(1500)
