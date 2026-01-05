import glob
import numpy as np
import pandas as pd

RAW_GLOB = "data/*_keystroke_raw.csv"
OUT_LABELED = "labeled_sessions.csv"

PAUSE_THRESHOLD_S = 1.0   # long pause threshold (tune if needed)
LABEL_TOP_QUANTILE = 0.70 # top 30% stress_score => stress_label=1


def load_raw() -> pd.DataFrame:
    paths = sorted(glob.glob(RAW_GLOB))
    if not paths:
        raise FileNotFoundError(f"No files matched {RAW_GLOB}. Put raw csv files into app/data/")

    dfs = []
    for p in paths:
        df = pd.read_csv(p, engine="python", on_bad_lines="skip")
        dfs.append(df)
    raw = pd.concat(dfs, ignore_index=True)

    # Normalize key columns
    raw["User_ID"] = raw["User_ID"].astype(str).str.strip()
    raw["Session_ID"] = pd.to_numeric(raw["Session_ID"], errors="coerce").astype("Int64")

    # Numeric columns
    for c in ["Press_Time", "Release_Time", "Hold_Time", "DD", "UD", "Characters_Count"]:
        raw[c] = pd.to_numeric(raw.get(c), errors="coerce")

    raw = raw.dropna(subset=["User_ID", "Session_ID"])
    return raw


def extract_session_features(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    # backspace flags
    df["Key_Pressed"] = df["Key_Pressed"].astype(str)
    df["is_backspace"] = df["Key_Pressed"].str.contains("backspace", case=False, na=False).astype(int)

    # pause flags (based on DD / UD)
    df["long_pause_dd"] = (df["DD"] > PAUSE_THRESHOLD_S).astype(int)
    df["long_pause_ud"] = (df["UD"] > PAUSE_THRESHOLD_S).astype(int)

    gcols = ["User_ID", "Session_ID"]
    g = df.groupby(gcols, dropna=False)

    feat = g.agg(
        dwell_mean=("Hold_Time", "mean"),
        dwell_std=("Hold_Time", "std"),
        dd_mean=("DD", "mean"),
        dd_std=("DD", "std"),
        ud_mean=("UD", "mean"),
        ud_std=("UD", "std"),
        backspace_count=("is_backspace", "sum"),
        long_pause_dd_ratio=("long_pause_dd", "mean"),
        long_pause_ud_ratio=("long_pause_ud", "mean"),
        press_min=("Press_Time", "min"),
        press_max=("Press_Time", "max"),
        chars_total=("Characters_Count", "max"),
    ).reset_index()

    # typing speed (chars/sec)
    feat["active_time_s"] = (feat["press_max"] - feat["press_min"]).replace(0, np.nan)
    feat["typing_speed_cps"] = feat["chars_total"] / feat["active_time_s"]

    # ratios
    feat["backspace_ratio"] = feat["backspace_count"] / feat["chars_total"].replace(0, np.nan)

    # cleanup
    feat = feat.drop(columns=["press_min", "press_max", "chars_total", "active_time_s"], errors="ignore")

    return feat


def add_user_zscores(feat: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = feat.copy()
    for c in cols:
        out[f"z_{c}"] = out.groupby("User_ID")[c].transform(
            lambda x: (x - x.mean()) / (x.std(ddof=0) + 1e-6)
        )
    return out


def main():
    raw = load_raw()
    feat = extract_session_features(raw)

    # Z-score per user (prevents "slow typist = stressed" bias)
    cols_for_score = [
        "dwell_mean",
        "dd_mean",
        "ud_mean",
        "long_pause_dd_ratio",
        "long_pause_ud_ratio",
        "backspace_ratio",
        "typing_speed_cps",
    ]
    feat = add_user_zscores(feat, cols_for_score)

    # Stress score inspired by keystroke-stress research:
    # timing delays and errors increase; speed decreases
    feat["stress_score"] = (
        feat["z_dwell_mean"]
        + feat["z_dd_mean"]
        + feat["z_ud_mean"]
        + feat["z_long_pause_dd_ratio"]
        + feat["z_long_pause_ud_ratio"]
        + feat["z_backspace_ratio"]
        - feat["z_typing_speed_cps"]
    )

    # Convert stress_score -> stress_label using top quantile
    thr = feat["stress_score"].quantile(LABEL_TOP_QUANTILE)
    feat["stress_label"] = (feat["stress_score"] > thr).astype(int)

    feat.to_csv(OUT_LABELED, index=False)
    print(f"Saved: {OUT_LABELED}")
    print("Label distribution:")
    print(feat["stress_label"].value_counts(dropna=False))
    print("\nPreview:")
    print(feat[["User_ID", "Session_ID", "stress_score", "stress_label"]].head(10))


if __name__ == "__main__":
    main()
