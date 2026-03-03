import numpy as np

def analyze_stress(rr_intervals):
    """
    Analyze HRV from RR intervals (ms)
    
    Parameters:
        rr_intervals: list of RR intervals in milliseconds
        
    Returns:
        dict with stress level + metrics
    """

    if len(rr_intervals) < 5:
        return {"stress_level": "insufficient_data"}

    rr = np.array(rr_intervals)

    # Remove outliers (basic cleaning)
    rr = rr[(rr > 300) & (rr < 2000)]

    # Mean HR
    mean_rr = np.mean(rr)
    mean_hr = 60000 / mean_rr

    # SDNN
    sdnn = np.std(rr)

    # RMSSD
    diff_rr = np.diff(rr)
    rmssd = np.sqrt(np.mean(diff_rr**2))

    # pNN50
    nn50 = np.sum(np.abs(diff_rr) > 50)
    pnn50 = (nn50 / len(diff_rr)) * 100

    # Stress classification
    if rmssd > 50:
        stress_level = "Relaxed"
    elif 30 <= rmssd <= 50:
        stress_level = "Normal"
    elif 15 <= rmssd < 30:
        stress_level = "Elevated Stress"
    else:
        stress_level = "High Stress"

    return {
        "stress_level": stress_level,
        "metrics": {
            "mean_hr_bpm": round(mean_hr, 2),
            "mean_rr_ms": round(mean_rr, 2),
            "sdnn": round(sdnn, 2),
            "rmssd": round(rmssd, 2),
            "pnn50_percent": round(pnn50, 2)
        }
    }
