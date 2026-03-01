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

    def clean_text(self, text: str) -> str:
        text = text.lower()
        import re
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"[^a-z\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def get_user_posts(self, username: str):
        import requests
        try:
            token = settings.X_BEARER_TOKEN
            if not token:
                raise ValueError("Missing bearer token. Set X_BEARER_TOKEN in the environment.")

            clean_username = username.replace("@", "")

            user_response = requests.get(
                f"https://api.x.com/2/users/by/username/{clean_username}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            user_response.raise_for_status()

            user_data = user_response.json().get("data")
            if not user_data:
                raise ValueError("User not found or API access restricted.")

            user_id = user_data.get("id")
            print(f"User ID for @{clean_username} is {user_id}")

            tweets_response = requests.get(
                f"https://api.x.com/2/users/{user_id}/tweets",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "tweet.fields": "created_at,text,public_metrics",
                    "max_results": 50,
                },
                timeout=30,
            )
            tweets_response.raise_for_status()
            
            response_json = tweets_response.json()
            if "errors" in response_json:
                print(f"Twitter API returned errors: {response_json['errors']}")
            
            # API returns 'data' array if tweets exist
            return response_json.get("data")

        except requests.exceptions.ConnectionError:
            print("Connection Reset: Check your internet/VPN or verify your API Tier permissions.")
        except requests.exceptions.HTTPError as exc:
            error_body = exc.response.json() if exc.response is not None else str(exc)
            print("API Error:", error_body)
        except Exception as exc:
            print("API Error:", str(exc))

        return None

    async def predict_user_depression(self, username: str) -> Dict[str, Any]:
        """
        Fetches tweets for a user and predicts overall depression level.
        """
        import numpy as np
        if not self.model or not self.vectorizer:
            return {"error": "Models not loaded"}
            
        tweets = self.get_user_posts(username)
        if not tweets:
            return {
                "error": "No tweets found or API access restricted.",
                "total_tweets": 0,
                "depressed_tweets": 0,
                "not_depressed_tweets": 0,
                "depressed_percent": "0.00%",
                "not_depressed_percent": "0.00%",
                "cleaned_tweets": [],
            }

        cleaned_tweets = [self.clean_text(tweet.get("text", "")) for tweet in tweets]
        cleaned_tweets = [text for text in cleaned_tweets if text]
        if not cleaned_tweets:
            return {
                "error": "No valid tweet text found.",
                "total_tweets": 0,
                "depressed_tweets": 0,
                "not_depressed_tweets": 0,
                "depressed_percent": "0.00%",
                "not_depressed_percent": "0.00%",
                "cleaned_tweets": [],
            }

        X = self.vectorizer.transform(cleaned_tweets)
        predictions = self.model.predict(X)

        total_tweets = len(cleaned_tweets)
        depressed_tweets = int(np.sum(predictions == 1))
        not_depressed_tweets = int(np.sum(predictions == 0))

        depressed_percent = (depressed_tweets / total_tweets) * 100
        not_depressed_percent = (not_depressed_tweets / total_tweets) * 100

        return {
            "total_tweets": total_tweets,
            "depressed_tweets": depressed_tweets,
            "not_depressed_tweets": not_depressed_tweets,
            "depressed_percent": f"{depressed_percent:.2f}%",
            "not_depressed_percent": f"{not_depressed_percent:.2f}%",
            "cleaned_tweets": cleaned_tweets,
        }
