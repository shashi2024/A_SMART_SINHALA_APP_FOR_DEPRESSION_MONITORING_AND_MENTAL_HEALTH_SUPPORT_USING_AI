"""
parse_raw_keystroke_data.py
============================
Parses the 6 raw keystroke CSV files from backend/app/data/keystroke_stress/
into per-repetition feature rows, then applies absolute stress thresholds
from Akanksha et al. (JETIR 2021) to assign stress labels.

Raw data source:
-----------------
Files: backend/app/data/keystroke_stress/100–105__tie5Roanl_keystroke_raw.csv
Each CSV = one participant typing the password .tie5Roanl repeatedly.
Each "Enter" keypress marks the end of one repetition attempt.
Features are computed per repetition (not per session) to maximise
the number of labeled training samples.

Labeling basis — Akanksha et al. (JETIR 2021), Table II & Figure 3:
---------------------------------------------------------------------
The paper reports feature distributions across Neutral vs Stressed conditions.
The absolute thresholds below are derived from the boundary values between their
reported Neutral (Low) and Stressed (High) class distributions:

  hold_mean   > 0.30s  → stress signal  (neutral avg: 0.10-0.15s)
  dd_mean     > 0.55s  → stress signal  (neutral avg: 0.20-0.30s)
  typing_speed< 2.5 cps → stress signal (neutral avg: 4.0-6.0 cps)
  backspace_ratio > 0.08 → stress signal (neutral avg: 0.02-0.04)
  long_pause_dd_ratio > 0.18 → stress signal (neutral avg: 0.02-0.06)

Scoring: each signal above counts +1. Total score → label:
  0 (Low):    score ≤ 1
  1 (Medium): score = 2
  2 (High):   score ≥ 3

Usage:
------
  python ai_models/stress/parse_raw_keystroke_data.py

Output:
-------
  ai_models/stress/data/participant_stress_reps.csv
"""

from __future__ import annotations
import glob
import numpy as np
import pandas as pd
from pathlib import Path

# Raw data lives in the backend data folder
RAW_GLOB = str(
    Path(__file__).resolve().parent.parent.parent
    / "backend" / "app" / "data" / "keystroke_stress" / "*_keystroke_raw.csv"
)
OUT = Path(__file__).parent / "data" / "participant_stress_reps.csv"

# ── Akanksha et al. (JETIR 2021) absolute stress thresholds ─────────────────
THR_HOLD_MEAN        = 0.30   # seconds — dwell time
THR_DD_MEAN          = 0.55   # seconds — inter-key latency
THR_TYPING_SPEED     = 2.50   # chars/second (inverse — below = stressed)
THR_BACKSPACE_RATIO  = 0.08   # proportion
THR_LONG_PAUSE_RATIO = 0.18   # proportion of DD intervals > 1s


def parse_repetitions(session_df: pd.DataFrame,
                       user_id: str,
                       session_id: int) -> list[dict]:
    """
    Split a session's raw keystrokes into individual password repetitions
    (each terminated by an Enter keypress) and compute rep-level features.
    """
    rows: list[dict] = []
    buffer: list = []
    rep_num = 0

    for _, row in session_df.iterrows():
        buffer.append(row)
        if row["Key_Pressed"] == "Key.enter" and len(buffer) > 4:
            rep_df = pd.DataFrame(buffer)

            # Exclude the terminal Enter from timing stats
            typing = rep_df[rep_df["Key_Pressed"] != "Key.enter"]
            is_bsp = rep_df["Key_Pressed"].astype(str).str.contains(
                "backspace", case=False, na=False
            )

            if len(typing) < 5:
                buffer = []
                continue

            hold_vals = pd.to_numeric(typing["Hold_Time"], errors="coerce").dropna()
            dd_vals   = pd.to_numeric(typing["DD"],        errors="coerce").dropna()
            ud_vals   = pd.to_numeric(typing["UD"],        errors="coerce").dropna()
            pt        = pd.to_numeric(rep_df["Press_Time"], errors="coerce").dropna()

            duration  = float(pt.max() - pt.min()) if len(pt) >= 2 else np.nan
            key_count = len(rep_df)
            speed     = key_count / duration if (duration and duration > 0) else np.nan

            rows.append({
                "User_ID":              user_id,
                "Session_ID":           session_id,
                "rep_num":              rep_num,
                "hold_mean":            float(hold_vals.mean()) if len(hold_vals) else np.nan,
                "hold_std":             float(hold_vals.std())  if len(hold_vals) else np.nan,
                "dd_mean":              float(dd_vals.mean())   if len(dd_vals)   else np.nan,
                "dd_std":               float(dd_vals.std())    if len(dd_vals)   else np.nan,
                "ud_mean":              float(ud_vals.mean())   if len(ud_vals)   else np.nan,
                "ud_std":               float(ud_vals.std())    if len(ud_vals)   else np.nan,
                "long_pause_dd_ratio":  float((dd_vals > 1.0).mean()) if len(dd_vals) else np.nan,
                "long_pause_ud_ratio":  float((ud_vals > 1.0).mean()) if len(ud_vals) else np.nan,
                "backspace_ratio":      float(is_bsp.sum() / key_count),
                "typing_speed_cps":     speed,
                "data_source":          "participant_raw_data",
            })
            rep_num += 1
            buffer = []

    return rows


def assign_stress_label(row: pd.Series) -> int:
    """
    Multi-signal stress scoring grounded in Akanksha et al. (JETIR 2021).
    Each criterion maps to one stress signal; sum → 3-tier label.
    """
    score = 0

    if pd.notna(row["hold_mean"]) and row["hold_mean"] > THR_HOLD_MEAN:
        score += 1

    if pd.notna(row["dd_mean"]) and row["dd_mean"] > THR_DD_MEAN:
        score += 1

    if pd.notna(row["typing_speed_cps"]) and row["typing_speed_cps"] < THR_TYPING_SPEED:
        score += 1

    if pd.notna(row["backspace_ratio"]) and row["backspace_ratio"] > THR_BACKSPACE_RATIO:
        score += 1

    if pd.notna(row["long_pause_dd_ratio"]) and row["long_pause_dd_ratio"] > THR_LONG_PAUSE_RATIO:
        score += 1

    if score <= 1:
        return 0   # Low
    elif score == 2:
        return 1   # Medium
    else:
        return 2   # High


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    paths = sorted(glob.glob(RAW_GLOB))
    if not paths:
        raise FileNotFoundError(
            f"No files matched:\n  {RAW_GLOB}\n"
            "Ensure raw CSVs are in backend/app/data/keystroke_stress/"
        )

    print(f"Found {len(paths)} raw CSV files.")

    all_reps: list[dict] = []
    for p in paths:
        try:
            df = pd.read_csv(p, engine="python", on_bad_lines="skip")
        except Exception as e:
            print(f"  Skipping {p}: {e}")
            continue

        for uid in df["User_ID"].dropna().unique():
            for sid in df[df["User_ID"] == uid]["Session_ID"].dropna().unique():
                sess = df[(df["User_ID"] == uid) & (df["Session_ID"] == sid)]
                reps = parse_repetitions(sess, str(uid), int(sid))
                all_reps.extend(reps)
        print(f"  Parsed: {Path(p).name}")

    feat_df = pd.DataFrame(all_reps)

    # Drop rows with too many NaN features
    feat_df = feat_df.dropna(subset=["hold_mean", "dd_mean", "typing_speed_cps"])

    # Apply absolute stress labels
    feat_df["stress_label"] = feat_df.apply(assign_stress_label, axis=1)

    feat_df.to_csv(OUT, index=False)
    print(f"\nSaved {len(feat_df)} repetitions → {OUT}")

    print("\nLabel distribution (Akanksha et al. absolute thresholds):")
    print(feat_df["stress_label"].value_counts().sort_index()
          .rename({0: "Low (0)", 1: "Medium (1)", 2: "High (2)"}).to_string())

    print("\nFeature summary:")
    cols = ["hold_mean", "dd_mean", "typing_speed_cps",
            "backspace_ratio", "long_pause_dd_ratio"]
    print(feat_df[cols].describe().round(4).to_string())


if __name__ == "__main__":
    main()
