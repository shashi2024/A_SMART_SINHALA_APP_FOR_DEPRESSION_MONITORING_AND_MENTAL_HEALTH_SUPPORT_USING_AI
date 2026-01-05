from typing import List, Dict, Any
import numpy as np
import pandas as pd
import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

MODEL_PATH = "keystroke_stress_model.joblib"

bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
feature_cols = bundle["feature_cols"]

app = FastAPI(title="Keystroke Stress Detector")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (OK for local dev)
    allow_credentials=True,
    allow_methods=["*"],  # allow OPTIONS, POST, GET, etc.
    allow_headers=["*"],
)

class KeyEvent(BaseModel):
    key: str
    press_time: float  # seconds (e.g., performance.now()/1000 or time.time())
    release_time: float
    prev_key: str | None = None


class PredictRequest(BaseModel):
    user_id: str = "live_user"
    session_id: int = 999
    events: List[KeyEvent] = Field(..., min_items=10)


def events_to_raw_df(req: PredictRequest) -> pd.DataFrame:
    rows = []
    char_count = 0
    for ev in req.events:
        char_count += 1
        hold = max(0.0, ev.release_time - ev.press_time)
        rows.append({
            "User_ID": req.user_id,
            "Session_ID": req.session_id,
            "Key_Pressed": ev.key,
            "Key_Pressed_Previous": ev.prev_key,
            "Press_Time": ev.press_time,
            "Release_Time": ev.release_time,
            "Hold_Time": hold,
            # We will compute DD/UD from sequential events:
            "DD": np.nan,
            "UD": np.nan,
            "Characters_Count": char_count,
        })
    df = pd.DataFrame(rows)

    # Compute DD (down->down) and UD (up->down)
    df["DD"] = df["Press_Time"].diff()
    df["UD"] = df["Press_Time"] - df["Release_Time"].shift(1)
    return df


def extract_session_features(events: pd.DataFrame) -> pd.DataFrame:
    # Same feature logic as training (keep consistent)
    df = events.copy()
    for col in ["Press_Time", "Release_Time", "Hold_Time", "DD", "UD", "Characters_Count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["is_backspace"] = df["Key_Pressed"].astype(str).str.contains("backspace", case=False, na=False).astype(int)
    df["is_shift"] = df["Key_Pressed"].astype(str).str.contains("shift", case=False, na=False).astype(int)

    pause_thr = 1.0
    df["long_pause_dd"] = (df["DD"] > pause_thr).astype(int)
    df["long_pause_ud"] = (df["UD"] > pause_thr).astype(int)

    gcols = ["User_ID", "Session_ID"]
    g = df.groupby(gcols, dropna=False)

    def safe_mean(x): return float(np.nanmean(x)) if len(x) else np.nan
    def safe_std(x): return float(np.nanstd(x)) if len(x) else np.nan
    def safe_median(x): return float(np.nanmedian(x)) if len(x) else np.nan

    feat = pd.DataFrame({
        "hold_mean": g["Hold_Time"].apply(safe_mean),
        "hold_std": g["Hold_Time"].apply(safe_std),
        "dd_mean": g["DD"].apply(safe_mean),
        "dd_std": g["DD"].apply(safe_std),
        "ud_mean": g["UD"].apply(safe_mean),
        "ud_std": g["UD"].apply(safe_std),
        "dd_median": g["DD"].apply(safe_median),
        "ud_median": g["UD"].apply(safe_median),
        "backspace_count": g["is_backspace"].sum(),
        "shift_count": g["is_shift"].sum(),
        "long_pause_dd_ratio": g["long_pause_dd"].mean(),
        "long_pause_ud_ratio": g["long_pause_ud"].mean(),
    }).reset_index()

    press_min = g["Press_Time"].min().reset_index(name="press_min")
    press_max = g["Press_Time"].max().reset_index(name="press_max")
    char_max = g["Characters_Count"].max().reset_index(name="chars_total")
    feat = feat.merge(press_min, on=gcols, how="left").merge(press_max, on=gcols, how="left").merge(char_max, on=gcols, how="left")

    feat["active_time_s"] = (feat["press_max"] - feat["press_min"]).replace(0, np.nan)
    feat["typing_speed_cps"] = feat["chars_total"] / feat["active_time_s"]
    feat["backspace_ratio"] = feat["backspace_count"] / feat["chars_total"].replace(0, np.nan)

    feat = feat.drop(columns=["press_min", "press_max", "chars_total", "active_time_s"], errors="ignore")
    return feat


@app.post("/predict")
def predict(req: PredictRequest):
    raw_df = events_to_raw_df(req)
    feat_df = extract_session_features(raw_df)

    # Align to training columns
    X = feat_df.reindex(columns=feature_cols)

    # Probability of stress (class 1)
    proba = float(model.predict_proba(X)[0, 1])
    pred = int(proba >= 0.5)

    return {
        "stress_pred": pred,
        "stress_probability": round(proba, 4),
    }
