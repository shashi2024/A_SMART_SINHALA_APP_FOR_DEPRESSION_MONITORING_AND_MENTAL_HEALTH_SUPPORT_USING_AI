from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.twitter_service import TwitterService
from app.routes.auth import get_current_user

# Create API router for Twitter-related endpoints
router = APIRouter()

# Initialize Twitter service (loads ML model + vectorizer internally)
twitter_service = TwitterService()

# Request model for single text analysis
class TwitterAnalysisRequest(BaseModel):
    text: str
    

# Request model for batch text analysis
class TwitterBatchAnalysisRequest(BaseModel):
    texts: List[str]

# ---------------------------------------------
# Analyze single Twitter text for depression
# ---------------------------------------------
@router.post("/analyze")
async def analyze_twitter_text(
    request: TwitterAnalysisRequest,
    current_user: dict = Depends(get_current_user)  # Authentication required
):
    """
    Analyzes a single piece of text for depression indicators.
    Requires authentication.
    """
    # Call service layer to predict depression
    result = await twitter_service.predict_depression(request.text)

    # Handle service error response
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


# ---------------------------------------------
# Analyze multiple Twitter texts (batch)
# ---------------------------------------------
@router.post("/analyze-batch")
async def analyze_twitter_batch(
    request: TwitterBatchAnalysisRequest,
    current_user: dict = Depends(get_current_user)  # Authentication required
):
    """
    Analyzes multiple pieces of text for depression indicators.
    Requires authentication.
    """
    # Call batch processing function in service layer
    results = await twitter_service.analyze_batch(request.texts)
    return results


# Request model for Twitter username-based prediction
class UsernameInput(BaseModel):
    username: str


# ---------------------------------------------
# Predict depression level from Twitter username
# ---------------------------------------------
@router.post("/predict")
async def predict_twitter_user(
    request: UsernameInput,
    current_user: dict = Depends(get_current_user)  # Authentication required
):
    """
    Predicts depression level for a specific Twitter user.
    Requires authentication.
    """
    # Call service to fetch tweets + analyze user behavior
    result = await twitter_service.predict_user_depression(request.username)

    # Handle case where ML models are not loaded properly
    if "error" in result and result["error"] in ["Models not loaded"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return result


# ---------------------------------------------
# Check service/model loading status
# ---------------------------------------------
@router.get("/status")
async def get_twitter_service_status(
    current_user: dict = Depends(get_current_user)  # Authentication required
):
    """
    Returns the status of the Twitter service and models.
    Useful for debugging and deployment checks.
    """

    # Check whether ML model and vectorizer are loaded properly
    is_ready = twitter_service.model is not None and twitter_service.vectorizer is not None

    return {
        "status": "ready" if is_ready else "not_ready",
        "model_loaded": twitter_service.model is not None,
        "vectorizer_loaded": twitter_service.vectorizer is not None
    }
    