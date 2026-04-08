import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

def train():
    current_dir = os.path.dirname(__file__)
    data_path = os.path.join(current_dir, 'patient_data.csv')
    model_path = os.path.join(current_dir, 'model.pkl')

    print("Loading data...")
    if not os.path.exists(data_path):
        import generate_data
        generate_data.generate_data()

    df = pd.read_csv(data_path)
    
    X = df.drop('risk_level', axis=1)
    y = df['risk_level']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training RandomForestClassifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    # Save the model
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    train()
