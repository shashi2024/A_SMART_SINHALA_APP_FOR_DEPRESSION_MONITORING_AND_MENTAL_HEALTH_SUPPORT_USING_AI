import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

LABELED = "labeled_sessions.csv"
MODEL_OUT = "keystroke_stress_model.joblib"

def main():
    df = pd.read_csv(LABELED)

    # Features for model (exclude ids + label/score)
    drop_cols = {"User_ID", "Session_ID", "stress_label", "stress_score"}
    feature_cols = [c for c in df.columns if c not in drop_cols]

    X = df[feature_cols]
    y = df["stress_label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y if y.nunique() > 1 else None
    )

    model = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=2000, class_weight="balanced")),
    ])

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    print(classification_report(y_test, preds, digits=4))

    joblib.dump({"model": model, "feature_cols": feature_cols}, MODEL_OUT)
    print(f"Saved model: {MODEL_OUT}")

if __name__ == "__main__":
    main()
