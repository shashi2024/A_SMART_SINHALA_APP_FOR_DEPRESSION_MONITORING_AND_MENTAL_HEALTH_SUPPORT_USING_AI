from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.twitter_service import TwitterService
from app.routes.auth import get_current_user

router = APIRouter()
twitter_service = TwitterService()

class TwitterAnalysisRequest(BaseModel):
    text: str

class TwitterBatchAnalysisRequest(BaseModel):
    texts: List[str]

@router.post("/analyze")
async def analyze_twitter_text(
    request: TwitterAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyzes a single piece of text for depression indicators.
    Requires authentication.
    """
    result = await twitter_service.predict_depression(request.text)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.post("/analyze-batch")
async def analyze_twitter_batch(
    request: TwitterBatchAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyzes multiple pieces of text for depression indicators.
    Requires authentication.
    """
    results = await twitter_service.analyze_batch(request.texts)
    return results

class UsernameInput(BaseModel):
    username: str

@router.post("/predict")
async def predict_twitter_user(
    request: UsernameInput,
    current_user: dict = Depends(get_current_user)
):
    """
    Predicts depression level for a specific Twitter user.
    Requires authentication.
    """
    result = await twitter_service.predict_user_depression(request.username)
    if "error" in result and result["error"] in ["Models not loaded"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.get("/status")
async def get_twitter_service_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Returns the status of the Twitter service and models.
    """
    is_ready = twitter_service.model is not None and twitter_service.vectorizer is not None
    return {
        "status": "ready" if is_ready else "not_ready",
        "model_loaded": twitter_service.model is not None,
        "vectorizer_loaded": twitter_service.vectorizer is not None
    }
