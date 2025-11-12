"""
Training script for voice analysis model
"""

import numpy as np
import librosa
import os
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report
import joblib

class VoiceModelTrainer:
    """Train voice analysis model for emotion and depression detection"""
    
    def __init__(self):
        self.model = None
        self.model_path = "./models/voice_model.pkl"
    
    def extract_features(self, audio_path: str):
        """Extract features from audio file"""
        y, sr = librosa.load(audio_path, sr=22050)
        
        # Extract features
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        pitch = librosa.piptrack(y=y, sr=sr)
        energy = librosa.feature.rms(y=y)
        
        # Aggregate features
        features = np.concatenate([
            np.mean(mfccs, axis=1),
            [np.mean(pitch[0])],
            [np.mean(energy)]
        ])
        
        return features
    
    def prepare_data(self, data_dir: str):
        """Prepare training data from audio files"""
        features_list = []
        labels = []
        
        # Load audio files and labels
        # Adjust based on your data structure
        for file in os.listdir(data_dir):
            if file.endswith('.wav') or file.endswith('.mp3'):
                audio_path = os.path.join(data_dir, file)
                features = self.extract_features(audio_path)
                features_list.append(features)
                
                # Extract label from filename or metadata
                # Adjust based on your labeling system
                label = 0  # Placeholder
                labels.append(label)
        
        return np.array(features_list), np.array(labels)
    
    def train(self, X, y):
        """Train the model"""
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.model = SVC(kernel='rbf', probability=True)
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
    trainer = VoiceModelTrainer()
    print("Voice model training script ready.")

