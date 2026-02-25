import os
import joblib
import pandas as pd
from typing import Dict, Any, List
from app.config import settings

class TwitterService:
    """
    Service for detecting depression from Twitter data (text)
    using pre-trained SGD model and TF-IDF vectorizer.
    """
    
    def __init__(self):
        self.model_path = settings.TWITTER_MODEL_PATH
        self.model_file = os.path.join(self.model_path, "sgd_depression_model_epoch.pkl")
        self.vectorizer_file = os.path.join(self.model_path, "tfidf_vectorizer_epoch.pkl")
        
        self.model = None
        self.vectorizer = None
        
        # Load models on initialization
        self._load_models()
        
    def _load_models(self):
        """Loads the SGD model and TF-IDF vectorizer from disk."""
        try:
            if os.path.exists(self.model_file) and os.path.exists(self.vectorizer_file):
                self.model = joblib.load(self.model_file)
                self.vectorizer = joblib.load(self.vectorizer_file)
                print(f"✅ Twitter models loaded successfully from {self.model_path}")
            else:
                print(f"⚠️ Warning: Twitter model files not found in {self.model_path}")
                print(f"   Model exists: {os.path.exists(self.model_file)}")
                print(f"   Vectorizer exists: {os.path.exists(self.vectorizer_file)}")
        except Exception as e:
            import traceback
            print(f"❌ Error loading Twitter models: {e}")
            traceback.print_exc()

    async def predict_depression(self, text: str) -> Dict[str, Any]:
        """
        Predicts depression level from a given piece of text.
        
        Args:
            text (str): The text (tweet) to analyze.
            
        Returns:
            Dict[str, Any]: Prediction result containing score and label.
        """
        if not self.model or not self.vectorizer:
            return {
                "error": "Models not loaded",
                "score": 0.0,
                "label": "unknown"
            }
        
        try:
            # Transform the text using the loaded vectorizer
            text_vectorized = self.vectorizer.transform([text])
            
            # Get prediction (assuming binary classification 0: not depressed, 1: depressed)
            prediction = self.model.predict(text_vectorized)[0]
            
            # If the model supports probability estimates, get those as well
            score = 0.0
            if hasattr(self.model, "predict_proba"):
                probabilities = self.model.predict_proba(text_vectorized)[0]
                # Assuming index 1 is 'depressed'
                score = float(probabilities[1])
            elif hasattr(self.model, "decision_function"):
                # For models like SGDClassifier that might not have predict_proba by default
                decision = self.model.decision_function(text_vectorized)[0]
                # Map decision function to a 0-1 score (sigmoid-like)
                import numpy as np
                score = float(1 / (1 + np.exp(-decision)))
            else:
                # Fallback to binary prediction
                score = 1.0 if prediction == 1 else 0.0

            return {
                "score": score,
                "is_depressed": bool(prediction == 1),
                "label": "depressed" if prediction == 1 else "not depressed"
            }
        except Exception as e:
            print(f"❌ Error during Twitter prediction: {e}")
            return {
                "error": str(e),
                "score": 0.0,
                "label": "error"
            }

    async def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyzes a batch of texts."""
        results = []
        for text in texts:
            results.append(await self.predict_depression(text))
        return results
