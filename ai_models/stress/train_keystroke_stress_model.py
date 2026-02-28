"""
train_keystroke_stress_model.py
================================
Merges the CMU baseline (LOW stress) and participant raw data (labeled via
Akanksha et al. thresholds), then trains a Random Forest classifier.

Pipeline:
  1. Load data/cmu_baseline_reps.csv      (stress_label = 0, relaxed typing)
  2. Load data/participant_stress_reps.csv (stress_label = 0/1/2, threshold-labeled)
  3. Merge → data/combined_labeled.csv
  4. Train: SimpleImputer → StandardScaler → RandomForestClassifier
  5. Save → backend/models/keystroke_stress/keystroke_stress_model.joblib

Model rationale — Akanksha et al. (JETIR 2021):
  Random Forest was found to be the best-performing classifier for
  multi-class cognitive stress classification via keystroke dynamics,
  outperforming SVM, k-NN, and Naive Bayes in their benchmark.
  n_estimators=200 and class_weight='balanced' follow their recommendation.

Usage:
------
  # Run from project root:
  python ai_models/stress/generate_cmu_baseline_dataset.py
  python ai_models/stress/parse_raw_keystroke_data.py
  python ai_models/stress/train_keystroke_stress_model.py

Output:
-------
  backend/models/keystroke_stress/keystroke_stress_model.joblib
"""

from __future__ import annotations
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_DIR   = Path(__file__).parent
CMU_CSV    = BASE_DIR / "data" / "cmu_baseline_reps.csv"
YOUR_CSV   = BASE_DIR / "data" / "participant_stress_reps.csv"
MERGED     = BASE_DIR / "data" / "combined_labeled.csv"

# Output model goes into backend/models/ — same pattern as team's other models
MODEL_OUT  = (
    Path(__file__).resolve().parent.parent.parent
    / "backend" / "models" / "keystroke_stress" / "keystroke_stress_model.joblib"
)

FEATURE_COLS = [
    "hold_mean", "hold_std",
    "dd_mean",   "dd_std",
    "ud_mean",   "ud_std",
    "long_pause_dd_ratio",
    "long_pause_ud_ratio",
    "backspace_ratio",
    "typing_speed_cps",
]

STRESS_LEVEL_MAP = {0: "Low", 1: "Medium", 2: "High"}


def load_and_merge() -> pd.DataFrame:
    if not CMU_CSV.exists():
        raise FileNotFoundError(
            f"Missing {CMU_CSV}\n"
            "Run generate_cmu_baseline_dataset.py first."
        )
    if not YOUR_CSV.exists():
        raise FileNotFoundError(
            f"Missing {YOUR_CSV}\n"
            "Run parse_raw_keystroke_data.py first."
        )

    cmu  = pd.read_csv(CMU_CSV)
    your = pd.read_csv(YOUR_CSV)

    print(f"CMU baseline rows  : {len(cmu):>6,}  (all label=0 / Low)")
    print(f"Participant rows   : {len(your):>6,}")
    print(f"  Label dist       : {your['stress_label'].value_counts().sort_index().to_dict()}")

    combined = pd.concat([cmu, your], ignore_index=True, sort=False)
    MERGED.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(MERGED, index=False)
    print(f"\nMerged dataset     : {len(combined):>6,} rows → {MERGED}")
    print(f"Combined label dist: {combined['stress_label'].value_counts().sort_index().to_dict()}")
    return combined


def train(df: pd.DataFrame) -> None:
    X = df[FEATURE_COLS]
    y = df["stress_label"].astype(int)

    if y.nunique() < 3:
        raise ValueError(
            f"Only {y.nunique()} classes found — need all 3 (Low/Medium/High).\n"
            "Re-check labeling thresholds in parse_raw_keystroke_data.py."
        )

    # ── 5-fold cross-validation ─────────────────────────────────────────────
    pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipe, X, y, cv=cv, scoring="f1_macro", n_jobs=-1)
    print(f"\n5-Fold CV macro-F1: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # ── Hold-out test set evaluation ────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)

    print("\n=== Hold-out Test Classification Report ===")
    print(classification_report(
        y_test, preds,
        target_names=["Low", "Medium", "High"],
        digits=4,
    ))

    print("Confusion Matrix (rows=actual, cols=predicted):")
    cm = confusion_matrix(y_test, preds)
    cm_df = pd.DataFrame(cm,
                         index=["Actual Low", "Actual Med", "Actual High"],
                         columns=["Pred Low", "Pred Med", "Pred High"])
    print(cm_df.to_string())

    # ── Feature importance ──────────────────────────────────────────────────
    importances = pipe.named_steps["clf"].feature_importances_
    imp_df = pd.DataFrame({"feature": FEATURE_COLS, "importance": importances})
    imp_df = imp_df.sort_values("importance", ascending=False)
    print("\nFeature Importances (Random Forest):")
    for _, row in imp_df.iterrows():
        bar = "█" * int(row["importance"] * 50)
        print(f"  {row['feature']:<26} {row['importance']:.4f}  {bar}")

    # ── Retrain on full dataset before saving ───────────────────────────────
    pipe.fit(X, y)
    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": pipe, "feature_cols": FEATURE_COLS}, MODEL_OUT)
    print(f"\nModel saved → {MODEL_OUT}")


def main() -> None:
    combined = load_and_merge()
    train(combined)


if __name__ == "__main__":
    main()
