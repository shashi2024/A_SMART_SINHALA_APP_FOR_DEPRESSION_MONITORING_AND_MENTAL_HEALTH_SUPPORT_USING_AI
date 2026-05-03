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
        # Path where trained ML models are stored
        self.model_path = settings.TWITTER_MODEL_PATH

        # File paths for model and vectorizer
        self.model_file = os.path.join(self.model_path, "sgd_depression_model_epoch.pkl")
        self.vectorizer_file = os.path.join(self.model_path, "tfidf_vectorizer_epoch.pkl")

        # Placeholders for loaded ML objects
        self.model = None
        self.vectorizer = None

        # Load models when service is initialized
        self._load_models()

    def _load_models(self):
        """
        Loads the SGD model and TF-IDF vectorizer from disk.
        This runs once during service initialization.
        """
        try:
            # Check if both required files exist before loading
            if os.path.exists(self.model_file) and os.path.exists(self.vectorizer_file):

                # Load trained ML model
                self.model = joblib.load(self.model_file)

                # Load TF-IDF vectorizer
                self.vectorizer = joblib.load(self.vectorizer_file)

                print(f"✅ Twitter models loaded successfully from {self.model_path}")
            else:
                # Warning if model files are missing
                print(f"⚠️ Warning: Twitter model files not found in {self.model_path}")
                print(f"   Model exists: {os.path.exists(self.model_file)}")
                print(f"   Vectorizer exists: {os.path.exists(self.vectorizer_file)}")

        except Exception as e:
            # Print full traceback for debugging model loading issues
            import traceback
            print(f"❌ Error loading Twitter models: {e}")
            traceback.print_exc()

    async def predict_depression(self, text: str) -> Dict[str, Any]:
        """
        Predicts depression level from a single text input (tweet).

        Steps:
        1. Check if model is loaded
        2. Transform text using TF-IDF
        3. Predict using trained ML model
        4. Return score + label
        """

        # If models are not loaded, return error response
        if not self.model or not self.vectorizer:
            return {
                "error": "Models not loaded",
                "score": 0.0,
                "label": "unknown"
            }

        try:
            # Convert text into numerical feature vector
            text_vectorized = self.vectorizer.transform([text])

            # Predict class (0 = not depressed, 1 = depressed)
            prediction = self.model.predict(text_vectorized)[0]

            score = 0.0

            # If model supports probability prediction
            if hasattr(self.model, "predict_proba"):
                probabilities = self.model.predict_proba(text_vectorized)[0]
                score = float(probabilities[1])  # probability of "depressed" class

            # If model uses decision function instead of probabilities
            elif hasattr(self.model, "decision_function"):
                decision = self.model.decision_function(text_vectorized)[0]

                import numpy as np
                score = float(1 / (1 + np.exp(-decision)))  # sigmoid normalization

            else:
                # Fallback: simple binary mapping
                score = 1.0 if prediction == 1 else 0.0

            return {
                "score": score,
                "is_depressed": bool(prediction == 1),
                "label": "depressed" if prediction == 1 else "not depressed"
            }

        except Exception as e:
            # Handle prediction errors
            print(f"❌ Error during Twitter prediction: {e}")
            return {
                "error": str(e),
                "score": 0.0,
                "label": "error"
            }

    async def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """
        Analyzes multiple texts one by one and returns results list.
        """
        results = []

        # Loop through all texts and predict individually
        for text in texts:
            results.append(await self.predict_depression(text))

        return results

    def clean_text(self, text: str) -> str:
        """
        Cleans tweet text by:
        - Lowercasing
        - Removing URLs
        - Removing special characters
        - Removing extra spaces
        """
        text = text.lower()

        import re
        text = re.sub(r"http\S+", "", text)        # remove URLs
        text = re.sub(r"[^a-z\s]", "", text)       # keep only letters
        text = re.sub(r"\s+", " ", text).strip()   # normalize spaces

        return text

    def get_user_posts(self, username: str):
        """
        Fetch tweets of a user using X (Twitter) API v2.
        """

        import requests

        try:
            # Bearer token for API authentication
            token = settings.X_BEARER_TOKEN

            if not token:
                raise ValueError("Missing bearer token. Set X_BEARER_TOKEN in the environment.")

            # Remove @ if user provides it
            clean_username = username.replace("@", "")

            # Step 1: Get user ID from username
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

            # Step 2: Fetch user tweets
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

            # Log API errors if any
            if "errors" in response_json:
                print(f"Twitter API returned errors: {response_json['errors']}")

            # Return tweet data list
            return response_json.get("data")

        except requests.exceptions.ConnectionError:
            print("Connection Reset: Check internet/VPN or API permissions.")
        except requests.exceptions.HTTPError as exc:
            error_body = exc.response.json() if exc.response is not None else str(exc)
            print("API Error:", error_body)
        except Exception as exc:
            print("API Error:", str(exc))

        return None

    async def predict_user_depression(self, username: str) -> Dict[str, Any]:
        """
        Predicts overall depression level of a user based on their tweets.
        """

        import numpy as np

        # Ensure models are loaded
        if not self.model or not self.vectorizer:
            return {"error": "Models not loaded"}

        # Fetch tweets from API
        tweets = self.get_user_posts(username)

        # If no tweets found
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

        # Clean tweet texts
        cleaned_tweets = [self.clean_text(tweet.get("text", "")) for tweet in tweets]
        cleaned_tweets = [text for text in cleaned_tweets if text]

        # If no valid text remains after cleaning
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

        # Convert tweets into feature vectors
        X = self.vectorizer.transform(cleaned_tweets)

        # Predict all tweets
        predictions = self.model.predict(X)

        # Count results
        total_tweets = len(cleaned_tweets)
        depressed_tweets = int(np.sum(predictions == 1))
        not_depressed_tweets = int(np.sum(predictions == 0))

        # Calculate percentages
        depressed_percent = (depressed_tweets / total_tweets) * 100
        not_depressed_percent = (not_depressed_tweets / total_tweets) * 100

        # Return final aggregated result
        return {
            "total_tweets": total_tweets,
            "depressed_tweets": depressed_tweets,
            "not_depressed_tweets": not_depressed_tweets,
            "depressed_percent": f"{depressed_percent:.2f}%",
            "not_depressed_percent": f"{not_depressed_percent:.2f}%",
            "cleaned_tweets": cleaned_tweets,
        }
        