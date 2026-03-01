"""
Keystroke stress analysis service
Mirrors the pattern of typing_analysis.py and voice_analysis.py

Model path: backend/models/keystroke_stress/keystroke_stress_model.joblib
Training:   ai_models/stress/train_keystroke_stress_model.py
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

# ── Model loading (lazy, loaded once) ────────────────────────────────────────
_MODEL_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "models" / "keystroke_stress" / "keystroke_stress_model.joblib"
)

_model        = None
_feature_cols = None


def _load_model():
    global _model, _feature_cols
    if _model is not None:
        return
    try:
        import joblib
        bundle        = joblib.load(_MODEL_PATH)
        _model        = bundle["model"]
        _feature_cols = bundle["feature_cols"]
        print(f"[stress_analysis] Model loaded from {_MODEL_PATH}")
    except Exception as e:
        print(f"[stress_analysis] WARNING: Could not load model: {e}")
        _model        = None
        _feature_cols = None


# ── Feature constants ─────────────────────────────────────────────────────────
FEATURE_COLS = [
    "hold_mean", "hold_std",
    "dd_mean",   "dd_std",
    "ud_mean",   "ud_std",
    "long_pause_dd_ratio",
    "long_pause_ud_ratio",
    "backspace_ratio",
    "typing_speed_cps",
]

PAUSE_THRESHOLD_S  = 1.0
STRESS_LEVEL_MAP   = {0: "low", 1: "medium", 2: "high"}


# ── Feature extraction ────────────────────────────────────────────────────────

def _extract_features(events: List[Any]) -> pd.DataFrame:
    """Extract timing features from a list of KeystrokeEvent objects or dicts."""
    if not events:
        return pd.DataFrame([{col: 0.0 for col in FEATURE_COLS}])

    first = events[0]
    if hasattr(first, "model_dump"):
        rows = [e.model_dump() for e in events]
    elif hasattr(first, "dict"):
        rows = [e.dict() for e in events]
    elif isinstance(first, dict):
        rows = events
    else:
        raise TypeError(f"Unsupported event type: {type(first)}")

    df = pd.DataFrame(rows).rename(columns={
        "press_time":   "Press_Time",
        "release_time": "Release_Time",
        "key":          "Key",
    })

    for col in ["Press_Time", "Release_Time"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Press_Time", "Release_Time"]).reset_index(drop=True)
    if df.empty:
        return pd.DataFrame([{col: 0.0 for col in FEATURE_COLS}])

    df = df.sort_values("Press_Time").reset_index(drop=True)

    df["Hold"] = (df["Release_Time"] - df["Press_Time"]).clip(lower=0)
    df["DD"]   = df["Press_Time"].diff()
    df["UD"]   = df["Press_Time"] - df["Release_Time"].shift(1)

    is_backspace = df.get("is_backspace", pd.Series(False, index=df.index))
    is_backspace = is_backspace.fillna(False).astype(bool)

    total     = len(df)
    bsp_ratio = int(is_backspace.sum()) / total if total > 0 else 0.0
    duration  = float(df["Press_Time"].iloc[-1] - df["Press_Time"].iloc[0])
    speed     = total / duration if duration > 0 else 0.0

    dd_valid = df["DD"].dropna()
    ud_valid = df["UD"].dropna()

    features = {
        "hold_mean":           float(df["Hold"].mean()),
        "hold_std":            float(df["Hold"].std(ddof=0)),
        "dd_mean":             float(dd_valid.mean())     if len(dd_valid) else 0.0,
        "dd_std":              float(dd_valid.std(ddof=0)) if len(dd_valid) else 0.0,
        "ud_mean":             float(ud_valid.mean())     if len(ud_valid) else 0.0,
        "ud_std":              float(ud_valid.std(ddof=0)) if len(ud_valid) else 0.0,
        "long_pause_dd_ratio": float((dd_valid > PAUSE_THRESHOLD_S).mean()) if len(dd_valid) else 0.0,
        "long_pause_ud_ratio": float((ud_valid > PAUSE_THRESHOLD_S).mean()) if len(ud_valid) else 0.0,
        "backspace_ratio":     bsp_ratio,
        "typing_speed_cps":    speed,
    }

    return pd.DataFrame([features])


# ── Service class ─────────────────────────────────────────────────────────────

class StressAnalysisService:
    """
    Keystroke stress analysis service.
    Follows the same class-based pattern as TypingAnalysisService.
    """

    MIN_KEYSTROKES = 8

    def __init__(self):
        _load_model()

    @property
    def model_loaded(self) -> bool:
        return _model is not None

    def predict(self, events: List[Any]) -> Dict[str, Any]:
        """
        Run stress prediction on a list of keystroke events.

        Returns a dict with:
          stress_pred         int   0/1/2
          stress_level        str   low/medium/high
          stress_probabilities dict
          feature_snapshot    dict  (5 key features)
          warning             str | None
        """
        if not self.model_loaded:
            # Graceful degradation if model file is missing
            return {
                "stress_pred": 0,
                "stress_level": "low",
                "stress_probabilities": {"low": 1.0, "medium": 0.0, "high": 0.0},
                "feature_snapshot": {},
                "warning": "Model not loaded — install model file and restart.",
            }

        features_df = _extract_features(events)
        X = features_df.reindex(columns=_feature_cols, fill_value=0.0)

        stress_pred = int(_model.predict(X)[0])
        proba       = _model.predict_proba(X)[0]
        classes     = _model.classes_.tolist()

        stress_probabilities = {
            STRESS_LEVEL_MAP[cls]: round(float(prob), 4)
            for cls, prob in zip(classes, proba)
        }

        feature_snapshot = {
            col: round(float(features_df[col].iloc[0]), 4)
            for col in ["hold_mean", "dd_mean", "typing_speed_cps",
                        "backspace_ratio", "long_pause_dd_ratio"]
        }

        warning = None
        if len(events) < 20:
            warning = "Short session — result may be less accurate."

        return {
            "stress_pred":          stress_pred,
            "stress_level":         STRESS_LEVEL_MAP[stress_pred],
            "stress_probabilities": stress_probabilities,
            "feature_snapshot":     feature_snapshot,
            "warning":              warning,
        }
