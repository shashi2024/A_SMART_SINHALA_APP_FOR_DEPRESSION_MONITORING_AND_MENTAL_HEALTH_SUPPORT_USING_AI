import numpy as np
import pandas as pd
import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

MODEL_PATH = "keystroke_stress_model.joblib"

bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
feature_cols = bundle["feature_cols"]

app = FastAPI(title="Keystroke Stress API")

# CORS for browser chat.html
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class KeyEvent(BaseModel):
    key: str
    press_time: float
    release_time: float
    prev_key: Optional[str] = None

class PredictRequest(BaseModel):
    events: List[KeyEvent] = Field(..., min_items=10)

PAUSE_THRESHOLD_S = 1.0

def extract_features_from_events(events: List[KeyEvent]) -> pd.DataFrame:
    rows = []
    for i, ev in enumerate(events):
        hold = max(0.0, ev.release_time - ev.press_time)
        rows.append({
            "Key_Pressed": ev.key,
            "Press_Time": ev.press_time,
            "Release_Time": ev.release_time,
            "Hold_Time": hold,
        })

    df = pd.DataFrame(rows)
    df["DD"] = df["Press_Time"].diff()
    df["UD"] = df["Press_Time"] - df["Release_Time"].shift(1)

    df["is_backspace"] = df["Key_Pressed"].astype(str).str.contains("backspace", case=False, na=False).astype(int)
    df["long_pause_dd"] = (df["DD"] > PAUSE_THRESHOLD_S).astype(int)
    df["long_pause_ud"] = (df["UD"] > PAUSE_THRESHOLD_S).astype(int)

    press_min = df["Press_Time"].min()
    press_max = df["Press_Time"].max()
    active_time = (press_max - press_min) if (press_max - press_min) > 0 else np.nan

    chars_total = len(df)

    feat = {
        "dwell_mean": df["Hold_Time"].mean(),
        "dwell_std": df["Hold_Time"].std(),
        "dd_mean": df["DD"].mean(),
        "dd_std": df["DD"].std(),
        "ud_mean": df["UD"].mean(),
        "ud_std": df["UD"].std(),
        "backspace_count": df["is_backspace"].sum(),
        "long_pause_dd_ratio": df["long_pause_dd"].mean(),
        "long_pause_ud_ratio": df["long_pause_ud"].mean(),
        "typing_speed_cps": chars_total / active_time,
        "backspace_ratio": df["is_backspace"].mean(),
    }

    return pd.DataFrame([feat])

@app.post("/predict")
def predict(req: PredictRequest):
    X = extract_features_from_events(req.events)

    # Align columns to training features (missing cols become NaN -> imputer handles)
    X = X.reindex(columns=feature_cols)

    proba = float(model.predict_proba(X)[0, 1])
    pred = int(proba >= 0.5)

    return {
        "stress_pred": pred,
        "stress_probability": round(proba, 4)
    }
