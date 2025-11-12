"""
Training script for depression detection model
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

class DepressionModelTrainer:
    """Train depression detection model"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = "./models/depression_model.pkl"
        self.scaler_path = "./models/scaler.pkl"
    
    def prepare_data(self, data_path: str):
        """Prepare training data"""
        # Load dataset (example structure)
        # In production, load from your actual dataset
        df = pd.read_csv(data_path)
        
        # Feature extraction
        # This is a placeholder - adjust based on your actual features
        features = [
            'text_sentiment',
            'voice_pitch',
            'voice_energy',
            'typing_speed',
            'pause_duration',
            'error_rate'
        ]
        
        X = df[features]
        y = df['depression_label']  # 0: no depression, 1: depression
        
        return X, y
    
    def train(self, X, y):
        """Train the model"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model Accuracy: {accuracy:.2f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return accuracy
    
    def save_model(self):
        """Save trained model"""
        os.makedirs("./models", exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        print(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model"""
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        print("Model loaded successfully")
    
    def predict(self, features):
        """Predict depression score"""
        if self.model is None:
            self.load_model()
        
        features_scaled = self.scaler.transform([features])
        prediction = self.model.predict_proba(features_scaled)[0]
        
        return {
            'depression_score': float(prediction[1]),
            'confidence': float(max(prediction))
        }

if __name__ == "__main__":
    trainer = DepressionModelTrainer()
    
    # Example usage (replace with actual data path)
    # X, y = trainer.prepare_data("data/training_data.csv")
    # trainer.train(X, y)
    # trainer.save_model()
    
    print("Model training script ready. Provide training data to train the model.")

