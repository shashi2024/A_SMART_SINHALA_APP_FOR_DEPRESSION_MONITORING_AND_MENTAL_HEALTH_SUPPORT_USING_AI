import numpy as np
from scipy.fft import rfft, rfftfreq

def analyze_activity(accelerometer_data, sampling_rate=20):
    """
    Analyze 60-second accelerometer window.
    
    Parameters:
        accelerometer_data: list of dicts with x,y,z
        sampling_rate: samples per second (default 20Hz)
        
    Returns:
        dict with activity + metrics
    """

    if len(accelerometer_data) < sampling_rate * 5:
        return {"activity": "insufficient_data"}

    # Extract arrays
    x = np.array([d["x"] for d in accelerometer_data])
    y = np.array([d["y"] for d in accelerometer_data])
    z = np.array([d["z"] for d in accelerometer_data])

    # Magnitude (remove gravity effect approx)
    magnitude = np.sqrt(x**2 + y**2 + z**2)
    magnitude = magnitude - np.mean(magnitude)

    # Statistical features
    mean_mag = np.mean(magnitude)
    std_mag = np.std(magnitude)
    variance_mag = np.var(magnitude)
    energy = np.sum(magnitude**2) / len(magnitude)

    # Zero Crossing Rate
    zero_crossings = np.where(np.diff(np.sign(magnitude)))[0]
    zcr = len(zero_crossings) / len(magnitude)

    # FFT for dominant frequency
    yf = np.abs(rfft(magnitude))
    xf = rfftfreq(len(magnitude), 1 / sampling_rate)
    dominant_freq = xf[np.argmax(yf[1:]) + 1]  # skip zero freq

    # Activity classification logic
    if std_mag < 0.2 and energy < 0.5:
        activity = "Sitting"
    elif std_mag < 0.5 and dominant_freq < 0.5:
        activity = "Standing"
    elif 0.5 <= dominant_freq <= 3:
        activity = "Walking"
    elif dominant_freq > 3:
        activity = "Running"
    else:
        activity = "Unknown"

    return {
        "activity": activity,
        "metrics": {
            "mean": round(mean_mag, 4),
            "std": round(std_mag, 4),
            "variance": round(variance_mag, 4),
            "energy": round(energy, 4),
            "dominant_frequency": round(dominant_freq, 2),
            "zero_cross_rate": round(zcr, 4)
        }
    }
