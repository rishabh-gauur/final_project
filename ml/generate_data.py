import pandas as pd
import numpy as np
import os

def generate_data(num_samples=2000):
    np.random.seed(42)
    
    # Healthy cases
    healthy_n = int(num_samples * 0.7)
    df_healthy = pd.DataFrame({
        'bp': np.random.normal(120, 10, healthy_n).clip(90, 130).round(),
        'heart_rate': np.random.normal(75, 10, healthy_n).clip(60, 95).round(),
        'spo2': np.random.normal(98, 1, healthy_n).clip(95, 100).round(),
        'temperature': np.random.normal(36.8, 0.3, healthy_n).clip(36.1, 37.5).round(1),
        'resp_rate': np.random.normal(16, 2, healthy_n).clip(12, 20).round(),
        'map': np.random.normal(85, 5, healthy_n).clip(70, 100).round(),
        'ecg': np.random.normal(95, 3, healthy_n).clip(90, 100).round(),
        'risk_level': 0
    })
    
    # High risk cases
    risk_n = num_samples - healthy_n
    
    # Hypoxia
    hypoxia_n = risk_n // 3
    df_hypoxia = pd.DataFrame({
        'bp': np.random.normal(110, 15, hypoxia_n).clip(80, 130).round(),
        'heart_rate': np.random.normal(110, 15, hypoxia_n).clip(100, 140).round(),
        'spo2': np.random.normal(88, 3, hypoxia_n).clip(70, 92).round(),
        'temperature': np.random.normal(37, 0.5, hypoxia_n).round(1),
        'resp_rate': np.random.normal(25, 3, hypoxia_n).clip(22, 35).round(),
        'map': np.random.normal(70, 8, hypoxia_n).clip(50, 80).round(),
        'ecg': np.random.normal(80, 5, hypoxia_n).clip(50, 85).round(),
        'risk_level': 1
    })
    
    # Hypertension / Tachycardia
    htn_n = risk_n // 3
    df_htn = pd.DataFrame({
        'bp': np.random.normal(175, 15, htn_n).clip(140, 220).round(),
        'heart_rate': np.random.normal(95, 10, htn_n).clip(80, 120).round(),
        'spo2': np.random.normal(97, 2, htn_n).clip(90, 100).round(),
        'temperature': np.random.normal(36.8, 0.4, htn_n).round(1),
        'resp_rate': np.random.normal(18, 2, htn_n).clip(14, 24).round(),
        'map': np.random.normal(120, 10, htn_n).clip(110, 150).round(),
        'ecg': np.random.normal(85, 5, htn_n).clip(70, 90).round(),
        'risk_level': 1
    })
    
    # Severe Infection / Sepsis
    inf_n = risk_n - hypoxia_n - htn_n
    df_inf = pd.DataFrame({
        'bp': np.random.normal(90, 10, inf_n).clip(60, 100).round(),
        'heart_rate': np.random.normal(125, 15, inf_n).clip(110, 160).round(),
        'spo2': np.random.normal(94, 2, inf_n).clip(85, 96).round(),
        'temperature': np.random.normal(39.5, 0.5, inf_n).clip(38.5, 42.0).round(1),
        'resp_rate': np.random.normal(26, 4, inf_n).clip(22, 40).round(),
        'map': np.random.normal(60, 5, inf_n).clip(45, 65).round(),
        'ecg': np.random.normal(70, 10, inf_n).clip(40, 80).round(),
        'risk_level': 1
    })
    
    df = pd.concat([df_healthy, df_hypoxia, df_htn, df_inf]).sample(frac=1).reset_index(drop=True)
    output_path = os.path.join(os.path.dirname(__file__), 'patient_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated {num_samples} patient records with 7 features and saved to {output_path}")

if __name__ == '__main__':
    generate_data(2500)
