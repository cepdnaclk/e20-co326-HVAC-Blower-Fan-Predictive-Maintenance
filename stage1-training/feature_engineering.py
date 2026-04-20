"""
HVAC Fan — Feature Engineering Pipeline
=========================================
Reads raw CSV data files from data/ folder, applies sliding window,
extracts 12 time-domain and frequency-domain features per window,
and outputs a combined features CSV.

Usage:
    python feature_engineering.py

Output:
    data/features_all.csv
"""

import os
import glob
import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.stats import kurtosis

# ─── Configuration ───────────────────────────────────────────────────
WINDOW_SIZE = 256       # samples per window (2.56 seconds at 100Hz)
HOP_SIZE = 128          # 50% overlap
SAMPLE_RATE = 100.0     # Hz

# ACS712 5A module calibration
# At 0A, output is VCC/2 (≈2048 at 12-bit). Sensitivity = 185mV/A (for 5A version)
ACS712_ZERO_POINT = 2048    # ADC value at 0 Amps
ACS712_SENSITIVITY = 0.185  # Volts per Amp
ADC_VREF = 3.3
ADC_RESOLUTION = 4095

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

FEATURE_COLUMNS = [
    "vib_rms", "vib_peak", "vib_crest", "vib_kurt",
    "cur_rms", "cur_std",
    "dom_freq", "spec_rms", "spec_cent",
    "band1", "band2", "band3",
    "label"
]


def adc_to_current(adc_raw: np.ndarray) -> np.ndarray:
    """Convert raw ACS712 ADC values to current in Amps."""
    voltage = (adc_raw / ADC_RESOLUTION) * ADC_VREF
    zero_voltage = (ACS712_ZERO_POINT / ADC_RESOLUTION) * ADC_VREF
    current = (voltage - zero_voltage) / ACS712_SENSITIVITY
    return np.abs(current)  # We care about magnitude, not direction


def extract_window_features(ax, ay, az, current, fs=SAMPLE_RATE):
    """Extract 12 features from a single window of sensor data."""

    n = len(ax)

    # ─── Acceleration magnitude ──────────────────────────────────
    accel_mag = np.sqrt(ax**2 + ay**2 + az**2)

    # ─── Time-domain vibration features ──────────────────────────
    # 1. vib_rms: Root Mean Square of acceleration magnitude
    #    Measures the overall "energy" of vibration.
    #    Higher = more vibration = potential fault.
    vib_rms = np.sqrt(np.mean(accel_mag**2))

    # 2. vib_peak: Maximum absolute acceleration
    #    Catches sudden impact spikes (e.g., cracked tooth hitting).
    vib_peak = np.max(np.abs(accel_mag))

    # 3. vib_crest: Peak / RMS ratio (Crest Factor)
    #    High crest factor = sharp spikes in otherwise smooth signal.
    #    Indicates impulsive faults like bearing defects.
    vib_crest = vib_peak / (vib_rms + 1e-9)

    # 4. vib_kurt: Kurtosis (4th statistical moment)
    #    Measures "tailedness" of the distribution.
    #    Normal vibration ≈ 3.0 (Gaussian).
    #    High kurtosis > 5.0 = impulsive events (bearing spalling).
    vib_kurt = float(kurtosis(accel_mag, fisher=True))  # Fisher=True: excess kurtosis

    # ─── Time-domain current features ────────────────────────────
    # 5. cur_rms: RMS current drawn by motor
    #    Higher = motor under more load or jammed.
    cur_rms = np.sqrt(np.mean(current**2))

    # 6. cur_std: Standard deviation of current
    #    Higher = unstable current draw = motor struggling.
    cur_std = np.std(current)

    # ─── Frequency-domain features (FFT of ax) ──────────────────
    # Remove DC component (mean) before FFT
    ax_centered = ax - np.mean(ax)
    fft_vals = np.abs(fft(ax_centered))[:n // 2]
    freqs = fftfreq(n, 1 / fs)[:n // 2]

    # 7. dom_freq: Dominant frequency (loudest vibration frequency)
    #    For a balanced fan, this is typically the rotation speed.
    #    Shifts indicate mechanical changes.
    dom_freq = freqs[np.argmax(fft_vals)] if len(fft_vals) > 0 else 0.0

    # 8. spec_rms: Spectral RMS (overall frequency content energy)
    spec_rms = np.sqrt(np.mean(fft_vals**2))

    # 9. spec_cent: Spectral centroid (frequency "center of mass")
    #    Shifts upward when high-frequency faults appear (bearings).
    total_power = np.sum(fft_vals) + 1e-9
    spec_cent = np.sum(freqs * fft_vals) / total_power

    # 10-12. Band power: Energy in specific frequency bands
    # band1 (0-10Hz):   Imbalance, looseness, structural resonance
    # band2 (10-25Hz):  Misalignment, belt faults
    # band3 (25-50Hz):  Bearing defects, blade-pass frequency
    band1 = np.sum(fft_vals[(freqs >= 0) & (freqs < 10)])
    band2 = np.sum(fft_vals[(freqs >= 10) & (freqs < 25)])
    band3 = np.sum(fft_vals[(freqs >= 25) & (freqs <= 50)])

    return [
        vib_rms, vib_peak, vib_crest, vib_kurt,
        cur_rms, cur_std,
        dom_freq, spec_rms, spec_cent,
        band1, band2, band3
    ]


def process_file(filepath: str) -> pd.DataFrame:
    """Process a single raw CSV file into feature vectors."""

    print(f"  Processing: {os.path.basename(filepath)}")

    df = pd.read_csv(filepath)
    required_cols = ["ax", "ay", "az", "current_raw", "label"]
    for col in required_cols:
        if col not in df.columns:
            print(f"    [SKIP] Missing column: {col}")
            return pd.DataFrame()

    # Get label from data
    label = df["label"].iloc[0]

    # Convert columns to numeric, drop bad rows
    for col in ["ax", "ay", "az", "gx", "gy", "gz", "current_raw"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df.dropna(subset=["ax", "ay", "az", "current_raw"], inplace=True)

    # Convert raw ADC current to Amps
    current_amps = adc_to_current(df["current_raw"].values)

    ax = df["ax"].values
    ay = df["ay"].values
    az = df["az"].values

    print(f"    Samples: {len(df):,} | Label: {label}")

    # Sliding window feature extraction
    features = []
    n_windows = 0
    for start in range(0, len(df) - WINDOW_SIZE, HOP_SIZE):
        end = start + WINDOW_SIZE
        win_ax = ax[start:end]
        win_ay = ay[start:end]
        win_az = az[start:end]
        win_cur = current_amps[start:end]

        feat = extract_window_features(win_ax, win_ay, win_az, win_cur)
        features.append(feat + [label])
        n_windows += 1

    print(f"    Windows: {n_windows} (window={WINDOW_SIZE}, hop={HOP_SIZE})")

    return pd.DataFrame(features, columns=FEATURE_COLUMNS)


def main():
    print("=" * 60)
    print("  HVAC Fan — Feature Engineering Pipeline")
    print("=" * 60)

    # Find all raw CSV files
    pattern = os.path.join(DATA_DIR, "raw_*.csv")
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"\n[ERROR] No raw CSV files found in {DATA_DIR}/")
        print("  Expected files matching: raw_<label>_<timestamp>.csv")
        print("  Run collect_data.py first to collect sensor data.")
        return

    print(f"\nFound {len(files)} raw data file(s):\n")

    # Process all files
    all_features = []
    for f in files:
        df_feat = process_file(f)
        if not df_feat.empty:
            all_features.append(df_feat)

    if not all_features:
        print("\n[ERROR] No valid features extracted from any file.")
        return

    # Combine all features
    combined = pd.concat(all_features, ignore_index=True)
    output_path = os.path.join(DATA_DIR, "features_all.csv")
    combined.to_csv(output_path, index=False)

    # Summary
    print(f"\n{'='*60}")
    print(f"  Feature Engineering Complete!")
    print(f"{'='*60}")
    print(f"  Output:    {output_path}")
    print(f"  Total feature vectors: {len(combined):,}")
    print(f"\n  Per-label breakdown:")
    for label, count in combined["label"].value_counts().items():
        print(f"    {label:15s}: {count:>6,} windows")
    print(f"\n  Feature columns ({len(FEATURE_COLUMNS)-1}):")
    for i, col in enumerate(FEATURE_COLUMNS[:-1], 1):
        print(f"    {i:2d}. {col}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
