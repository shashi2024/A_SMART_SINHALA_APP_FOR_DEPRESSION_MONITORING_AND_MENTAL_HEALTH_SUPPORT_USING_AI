"""
Training script for typing pattern analysis model
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report
import joblib

class TypingModelTrainer:
    """Train typing pattern analysis model"""
    
    def __init__(self):
        self.model = None
        self.model_path = "./models/typing_model.pkl"
    
    def extract_features(self, keystroke_data):
        """Extract features from keystroke data"""
        timings = keystroke_data['timings']
        
        features = [
            np.mean(timings),
            np.std(timings),
            np.min(timings),
            np.max(timings),
            keystroke_data['typing_speed'],
            keystroke_data['pause_duration'],
            keystroke_data['error_rate'],
        ]
        
        return np.array(features)
    
    def prepare_data(self, data_path: str):
        """Prepare training data"""
        df = pd.read_csv(data_path)
        
        features_list = []
        labels = []
        
        for _, row in df.iterrows():
            keystroke_data = {
                'timings': eval(row['keystroke_timings']),
                'typing_speed': row['typing_speed'],
                'pause_duration': row['pause_duration'],
                'error_rate': row['error_rate'],
            }
            
            features = self.extract_features(keystroke_data)
            features_list.append(features)
            labels.append(row['depression_label'])
        
        return np.array(features_list), np.array(labels)
    
    def train(self, X, y):
        """Train the model"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
    
    def save_model(self):
        """Save trained model"""
        os.makedirs("./models", exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"Model saved to {self.model_path}")

if __name__ == "__main__":
    trainer = TypingModelTrainer()
    print("Typing model training script ready.")

