"""
Keystroke stress detection routes — Using Firestore session storage
Follows the same pattern as typing.py and voice.py
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Literal, Optional
from datetime import datetime

from app.routes.auth import get_current_user
from app.services.stress_analysis import StressAnalysisService
from app.services.firestore_service import FirestoreService

router = APIRouter()
firestore_service = FirestoreService()
stress_service = StressAnalysisService()

# ── Request / Response Models ─────────────────────────────────────────────────

class KeystrokeEvent(BaseModel):
    key: str
    press_time: float
    release_time: float
    is_backspace: Optional[bool] = False


class KeystrokeRequest(BaseModel):
    events: List[KeystrokeEvent]
    session_id: Optional[str] = None


class StressResponse(BaseModel):
    session_id: str
    stress_pred: int
    stress_level: Literal["low", "medium", "high"]
    stress_probabilities: Dict[str, float]
    feature_snapshot: Dict[str, float]
    depression_score: float          # normalised 0-1 for dashboard compatibility
    risk_level: str                  # mirrors voice/typing risk_level field
    warning: Optional[str] = None


# ── Health Check ──────────────────────────────────────────────────────────────

@router.get("/health")
async def stress_health():
    """Health check — confirms model is loaded"""
    return {
        "status": "ok",
        "model_loaded": stress_service.model_loaded,
        "service": "Keystroke Stress Detection",
    }


# ── Predict ───────────────────────────────────────────────────────────────────

@router.post("/analyze", response_model=StressResponse)
async def analyze_stress(
    request: KeystrokeRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Analyse keystroke timing patterns and return stress level.

    Requires minimum 8 keystroke events.
    Stress levels: 0 = low, 1 = medium, 2 = high.
    """
    user_id = current_user.get("id")

    if not request.events:
        raise HTTPException(status_code=400, detail="No keystroke events provided.")

    if len(request.events) < stress_service.MIN_KEYSTROKES:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Too few keystrokes ({len(request.events)}). "
                f"Need at least {stress_service.MIN_KEYSTROKES}."
            ),
        )

    # Get or create session (mirrors typing.py pattern)
    if request.session_id:
        session = firestore_service.get_session_by_id(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found.")
    else:
        session_id = firestore_service.create_session({
            "user_id": user_id,
            "session_type": "stress",
        })
        session = firestore_service.get_session_by_id(session_id)

    # Run prediction
    result = stress_service.predict(request.events)

    # Map stress pred to depression_score and risk_level for dashboard compatibility
    # stress 0→low, 1→medium, 2→high  →  depression_score 0.1, 0.5, 0.9
    STRESS_TO_DEPRESSION = {0: 0.1, 1: 0.5, 2: 0.9}
    STRESS_TO_RISK       = {0: "low", 1: "moderate", 2: "high"}

    depression_score = STRESS_TO_DEPRESSION[result["stress_pred"]]
    risk_level       = STRESS_TO_RISK[result["stress_pred"]]

    # Persist analysis to Firestore (mirrors typing_analysis storage)
    firestore_service.update_session(session["id"], {
        "stress_pred": result["stress_pred"],
        "stress_level": result["stress_level"],
        "depression_score": depression_score,
        "risk_level": risk_level,
        "last_message_time": datetime.utcnow().isoformat(),
    })

    return StressResponse(
        session_id=session["id"],
        stress_pred=result["stress_pred"],
        stress_level=result["stress_level"],
        stress_probabilities=result["stress_probabilities"],
        feature_snapshot=result["feature_snapshot"],
        depression_score=depression_score,
        risk_level=risk_level,
        warning=result.get("warning"),
    )


# ── History ───────────────────────────────────────────────────────────────────

@router.get("/history")
async def get_stress_history(
    current_user: dict = Depends(get_current_user),
):
    """Get user's keystroke stress analysis history (mirrors typing /history)"""
    user_id = current_user.get("id")
    sessions = firestore_service.get_user_sessions(user_id, session_type="stress")

    return [
        {
            "id": s.get("id"),
            "session_id": s.get("id"),
            "stress_pred": s.get("stress_pred"),
            "stress_level": s.get("stress_level"),
            "depression_score": s.get("depression_score"),
            "risk_level": s.get("risk_level"),
            "created_at": s.get("start_time"),
        }
        for s in sessions
    ]
