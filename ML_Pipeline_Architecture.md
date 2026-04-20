# 🏭 HVAC Blower Fan Predictive Maintenance
# ML Pipeline, ESP32 Integration & Full Infrastructure Architecture

> **Project:** CO326 — HVAC Blower Fan Predictive Maintenance (Project #17)
> **System Type:** Industrial Digital Twin | IIoT | Edge AI | TinyML
> **Architecture:** 4-Layer IIoT Stack | Containerized Cloud | Secure MQTT Sparkplug B

---

## 📐 Table of Contents

1. [Full System Overview](#1-full-system-overview)
2. [Technology & Frameworks Master List](#2-technology--frameworks-master-list)
3. [Stage 1 — ML Model Training Pipeline (PC-Side)](#3-stage-1--ml-model-training-pipeline-pc-side)
   - 3.1 Data Collection Strategy
   - 3.2 Feature Engineering
   - 3.3 Model Training (K-Means + Autoencoder)
   - 3.4 Model Validation & Threshold Calibration
   - 3.5 Model Export & Quantization
4. [Stage 2 — ESP32 Edge Integration & Real-Time Inference](#4-stage-2--esp32-edge-integration--real-time-inference)
   - 4.1 Firmware Architecture
   - 4.2 Sensor Acquisition Pipeline
   - 4.3 Feature Extraction Engine
   - 4.4 On-Device Inference Engine
   - 4.5 MQTT Sparkplug B Communication
5. [Docker Container Infrastructure](#5-docker-container-infrastructure)
6. [End-to-End Data Flow (All Stages)](#6-end-to-end-data-flow-all-stages)
7. [Step-by-Step Implementation Guide](#7-step-by-step-implementation-guide)

---

## 1. Full System Overview

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║           HVAC PREDICTIVE MAINTENANCE — FULL SYSTEM ARCHITECTURE                ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                  ║
║  ┌─────────────────────────────────────────────────────────────────────────┐    ║
║  │  STAGE 1: OFFLINE ML TRAINING (PC / Python Environment)                 │    ║
║  │                                                                          │    ║
║  │  [Physical Fan]──►[ESP32 Serial/MQTT]──►[PC CSV Logger]──►[Python ML]   │    ║
║  │                                              │                           │    ║
║  │  Pandas | NumPy | Scikit-learn | TFLite      │                           │    ║
║  │  K-Means + LSTM Autoencoder Training         │                           │    ║
║  │  Model Validation + Confusion Matrix          │                           │    ║
║  │  Export: centroids.h  +  thresholds.h        ◄                           │    ║
║  └─────────────────────────────────────────────────────────────────────────┘    ║
║                               │                                                  ║
║                    [Hardcode centroids into firmware]                            ║
║                               │                                                  ║
║  ┌─────────────────────────────────────────────────────────────────────────┐    ║
║  │  STAGE 2: ONLINE EDGE INFERENCE (ESP32-S3 Firmware)                      │    ║
║  │                                                                          │    ║
║  │  MPU6050──►[DMA/I2C]──►[DSP: RMS/FFT]──►[K-Means Inference]──►MQTT     │    ║
║  │  ACS712───►[ADC/DMA]──►[RMS/Std Dev] ──►[Anomaly Score 0-1]──►TLS      │    ║
║  │                                                                          │    ║
║  │  PlatformIO | FreeRTOS | Arduino Core | ArduinoMqtt | WiFiClientSecure  │    ║
║  └─────────────────────────────────────────────────────────────────────────┘    ║
║                               │ MQTT Sparkplug B (TLS 1.2)                       ║
║                               ▼                                                  ║
║  ┌─────────────────────────────────────────────────────────────────────────┐    ║
║  │  DOCKER CONTAINER STACK (Host PC / Server)                               │    ║
║  │                                                                          │    ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │    ║
║  │  │  Mosquitto   │  │   Node-RED   │  │   InfluxDB   │  │  Grafana   │  │    ║
║  │  │  MQTT Broker │─►│  Middleware  │─►│  Historian   │─►│  SCADA/DT  │  │    ║
║  │  │  Port: 8883  │  │  Port: 1880  │  │  Port: 8086  │  │  Port:3000 │  │    ║
║  │  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘  │    ║
║  │                                                                          │    ║
║  │  ┌──────────────┐  ┌──────────────┐                                     │    ║
║  │  │  Telegraf    │  │  Portainer   │                                     │    ║
║  │  │  Metrics Agg │  │  Container   │                                     │    ║
║  │  │  Port: 9273  │  │  Manager UI  │                                     │    ║
║  │  └──────────────┘  └──────────────┘                                     │    ║
║  └─────────────────────────────────────────────────────────────────────────┘    ║
║                               │                                                  ║
║                               ▼ Bidirectional Control                            ║
║  [Grafana Dashboard] ◄──────────────────────────────► [Physical Fan + Relay]    ║
╚══════════════════════════════════════════════════════════════════════════════════╝
```

---

## 2. Technology & Frameworks Master List

| Layer | Component | Technology/Framework | Version | Role |
|-------|-----------|---------------------|---------|------|
| **Training** | Data Collection | Python `pyserial` / MQTT | 3.x | Read ESP32 serial output to CSV |
| **Training** | Data Manipulation | `pandas`, `numpy` | Latest | Windowing, normalization, feature calc |
| **Training** | ML Model | `scikit-learn` KMeans | 1.x | Unsupervised clustering (normal baseline) |
| **Training** | Deep Learning (optional advanced) | `TensorFlow 2.x` + Keras | 2.x | LSTM Autoencoder for sequence anomaly |
| **Training** | Model Export | `TFLite Converter`, `xxd` | - | Convert to C byte array for ESP32 |
| **Training** | Visualization | `matplotlib`, `seaborn` | Latest | ROC curves, confusion matrix, scatter plots |
| **Training** | Validation | `scipy`, `sklearn.metrics` | Latest | Precision/recall, F1, threshold sweep |
| **Edge Firmware** | IDE | PlatformIO (VS Code extension) | Latest | Build, flash, monitor ESP32 |
| **Edge Firmware** | Framework | Arduino Core for ESP32-S3 | 2.x | Base hardware abstraction |
| **Edge Firmware** | RTOS | FreeRTOS | Built-in | Multi-task: sample / infer / publish |
| **Edge Firmware** | Sensor (Vibration) | MPU6050 I2C Library (`Adafruit_MPU6050`) | Latest | 3-axis accel/gyro at 100Hz |
| **Edge Firmware** | Sensor (Current) | ACS712 + `analogRead()` ADC | Native | 12-bit ADC current sampling |
| **Edge Firmware** | ML Inference | Custom K-Means C++ (hardcoded centroids) | Custom | Euclidean distance anomaly scoring |
| **Edge Firmware** | MQTT Client | `ArduinoMqtt` / `PubSubClient` | Latest | Publish Sparkplug B payloads |
| **Edge Firmware** | TLS/Security | `WiFiClientSecure` | Built-in | Mutual TLS to Mosquitto |
| **Edge Firmware** | Buffering | Custom circular ring buffer | Custom | Store 500 samples during Wi-Fi outage |
| **Container** | MQTT Broker | Eclipse Mosquitto | 2.x | Central message bus with TLS + ACL |
| **Container** | Middleware | Node-RED | 3.x | Flow-based data orchestration + RUL |
| **Container** | Database | InfluxDB | 2.x | Time-series historian (Line Protocol) |
| **Container** | Visualization | Grafana | 10.x | SCADA dashboard + Digital Twin UI |
| **Container** | Metrics | Telegraf | 1.x | System health metrics → InfluxDB |
| **Container** | Management | Portainer CE | Latest | Docker container management UI |
| **Network** | Protocol | MQTT Sparkplug B | v1.0 | Industrial-grade UNS topic structure |
| **Security** | Encryption | TLS 1.2 (self-signed certs) | - | End-to-end encryption ESP32 → Broker |
| **Security** | Auth | Username/Password + Client Cert | - | Broker-level access control |
| **Security** | Availability | LWT (Last Will & Testament) | - | Auto-detect ESP32 disconnect |

---

## 3. Stage 1 — ML Model Training Pipeline (PC-Side)

```
╔══════════════════════════════════════════════════════════════════════╗
║              STAGE 1: COMPLETE ML TRAINING PIPELINE                 ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  STEP 1            STEP 2           STEP 3         STEP 4           ║
║  ─────────         ──────────       ─────────       ──────────────   ║
║  Physical          Raw Data         Feature         Model            ║
║  Data Capture  ──► Collection   ──► Engineering ──► Training         ║
║                                                      │               ║
║  STEP 8            STEP 7           STEP 6         STEP 5           ║
║  ─────────         ──────────       ─────────       ──────────────   ║
║  Flash to          C Header         Model           Validation &     ║
║  ESP32      ◄───  Export      ◄───  Quantize  ◄───  Evaluation       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### 3.1 Step 1 — Physical Data Capture Strategy

**Goal:** Collect labelled, reproducible vibration and current sensor data from the real fan.

**Physical Setup Required:**
```
    12V DC Fan
    ──────────
        │
   ┌────▼─────┐          ┌──────────────┐
   │ Fan Body │◄─mounted─│   MPU6050    │
   │          │          │ (I2C: 0x68)  │
   └──────────┘          └──────┬───────┘
        │                       │ SDA/SCL
   ┌────▼─────┐          ┌──────▼───────┐
   │ Power    │          │   ESP32-S3   │
   │ Feed Line│◄─inline─►│              │
   └──────────┘          │  ACS712 ADC  │
                         │  (GPIO36)    │
                         └──────┬───────┘
                                │ USB Serial / Wi-Fi
                                ▼
                         [ PC — Python Logger ]
```

**Data Collection Sessions (run ALL of these to get labelled dataset):**

| Session | Fan Condition | Duration | Label | Samples (~100Hz) |
|---------|--------------|----------|-------|-----------------|
| S1 | Normal clean operation | 20 min | `normal` | ~120,000 |
| S2 | Normal with 50% speed | 15 min | `normal` | ~90,000 |
| S3 | Slight imbalance (10g weight on 1 blade) | 10 min | `warning` | ~60,000 |
| S4 | Severe imbalance (25g weight on 1 blade) | 10 min | `critical` | ~60,000 |
| S5 | Blade fouling (tape partially blocking blade) | 10 min | `critical` | ~60,000 |
| S6 | Bearing simulated fault (run at very high RPM) | 10 min | `critical` | ~60,000 |

**Python Data Logger Script (`collect_data.py`):**

```python
import serial
import csv
import time
from datetime import datetime

PORT = "COM5"          # Change to your ESP32 COM port
BAUD = 115200
LABEL = "normal"       # Change per session: normal / warning / critical
OUTPUT = f"data_{LABEL}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

HEADER = ["timestamp_ms","ax","ay","az","gx","gy","gz",
          "current_raw","label"]

with serial.Serial(PORT, BAUD, timeout=2) as ser, \
     open(OUTPUT, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(HEADER)
    print(f"[LOGGING] Writing to {OUTPUT} — Label: {LABEL}")
    start = time.time()
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line.startswith("DATA:"):
            # ESP32 sends: DATA:ts,ax,ay,az,gx,gy,gz,current
            parts = line[5:].split(",")
            if len(parts) == 8:
                writer.writerow(parts + [LABEL])
                f.flush()
```

**ESP32 Serial Output Format (printed at 100Hz in firmware):**
```
DATA:1234567,0.012,-0.003,9.812,0.001,-0.002,0.000,512
DATA:1234577,0.015,-0.001,9.810,0.002,-0.001,0.001,514
```

---

### 3.2 Step 2 — Feature Engineering

**Goal:** Convert raw time-domain sensor streams into a compact, ML-ready feature vector using a **sliding window** approach.

```
RAW SENSOR STREAM (100Hz = 100 samples/sec)
────────────────────────────────────────────
  ax: [0.01, 0.02, -0.01, 0.03, 0.01, ...]
  ay: [0.00, 0.01,  0.02, 0.00, 0.01, ...]
  az: [9.81, 9.80,  9.82, 9.81, 9.80, ...]
  I:  [0.52, 0.53,  0.51, 0.52, 0.50, ...]
                    │
            ┌───────▼────────┐
            │  SLIDING WINDOW │
            │  SIZE = 256     │  (2.56 seconds of data)
            │  HOP  = 128     │  (50% overlap)
            └───────┬────────┘
                    │
            ┌───────▼────────────────────────────────┐
            │         FEATURE EXTRACTION             │
            │                                        │
            │  Time Domain:                          │
            │   • vib_rms    = √(mean(ax²+ay²+az²)) │
            │   • vib_peak   = max(|accel_mag|)      │
            │   • vib_crest  = peak / rms            │
            │   • vib_kurtosis = 4th moment / std⁴  │
            │   • current_rms  = √(mean(I²))         │
            │   • current_std  = std(I)              │
            │   • current_thd  = harmonic distortion │
            │                                        │
            │  Frequency Domain (FFT of ax window):  │
            │   • dominant_freq = argmax(|FFT|)      │
            │   • spectral_rms  = RMS of FFT bins    │
            │   • spectral_centroid = weighted freq  │
            │   • band_power_0_50Hz   (imbalance)    │
            │   • band_power_50_200Hz (bearing)      │
            │   • band_power_200_500Hz (blade fault) │
            │                                        │
            │  FEATURE VECTOR SIZE = 13 floats       │
            └───────┬────────────────────────────────┘
                    │
            [Feature Matrix: N_windows × 13]
```

**Python Feature Extraction (`feature_engineering.py`):**

```python
import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.stats import kurtosis

WINDOW = 256   # samples
HOP    = 128   # 50% overlap
FS     = 100   # Hz sampling rate

def extract_features(df: pd.DataFrame, label: str) -> pd.DataFrame:
    features = []
    data = df[['ax','ay','az','current_raw']].values
    
    for start in range(0, len(data) - WINDOW, HOP):
        win = data[start:start+WINDOW]
        ax, ay, az = win[:,0], win[:,1], win[:,2]
        cur = win[:,3] * (3.3/4095) / 0.066  # ACS712 5A: 66mV/A
        
        accel_mag = np.sqrt(ax**2 + ay**2 + az**2)
        
        # Time-domain features
        vib_rms     = np.sqrt(np.mean(accel_mag**2))
        vib_peak    = np.max(np.abs(accel_mag))
        vib_crest   = vib_peak / (vib_rms + 1e-9)
        vib_kurt    = float(kurtosis(accel_mag))
        cur_rms     = np.sqrt(np.mean(cur**2))
        cur_std     = np.std(cur)
        
        # Frequency-domain features (on ax)
        fft_vals    = np.abs(fft(ax - np.mean(ax)))[:WINDOW//2]
        freqs       = fftfreq(WINDOW, 1/FS)[:WINDOW//2]
        dom_freq    = freqs[np.argmax(fft_vals)]
        spec_rms    = np.sqrt(np.mean(fft_vals**2))
        spec_cent   = np.sum(freqs * fft_vals) / (np.sum(fft_vals) + 1e-9)
        band1 = np.sum(fft_vals[(freqs>=0)   & (freqs<50)])
        band2 = np.sum(fft_vals[(freqs>=50)  & (freqs<200)])
        band3 = np.sum(fft_vals[(freqs>=200) & (freqs<=500)])
        
        features.append([
            vib_rms, vib_peak, vib_crest, vib_kurt,
            cur_rms, cur_std,
            dom_freq, spec_rms, spec_cent,
            band1, band2, band3,
            label
        ])
    
    cols = ['vib_rms','vib_peak','vib_crest','vib_kurt',
            'cur_rms','cur_std',
            'dom_freq','spec_rms','spec_cent',
            'band1','band2','band3','label']
    return pd.DataFrame(features, columns=cols)
```

---

### 3.3 Step 3 — Model Training

**Two-Model Approach (for maximum credibility):**

```
┌─────────────────────────────────────────────────────────────────┐
│              DUAL-MODEL TRAINING STRATEGY                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MODEL A: K-Means Clustering (Deploys to ESP32)                │
│  ─────────────────────────────────────────────                 │
│  Input : 12-dim feature vector (per window)                    │
│  Method: Fit on NORMAL data only (K=3 clusters)                │
│  Output: 3 centroids × 12 floats = 36 floats total             │
│  Size  : ~576 bytes — fits easily in ESP32 flash               │
│  Use   : Real-time anomaly scoring on-device                   │
│                                                                 │
│  MODEL B: LSTM Autoencoder (Runs in Node-RED / Python)          │
│  ─────────────────────────────────────────────                 │
│  Input : Sequence of 20 feature windows                        │
│  Method: Encoder→Bottleneck→Decoder trained on NORMAL          │
│  Output: Reconstruction error = anomaly score                  │
│  Use   : Server-side deep anomaly confirmation + RUL           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Model A — K-Means Training (`train_kmeans.py`):**

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import joblib, json

# Load only NORMAL operation data
df_normal = pd.concat([
    pd.read_csv("features_normal_session1.csv"),
    pd.read_csv("features_normal_session2.csv"),
])
X_normal = df_normal.drop(columns=['label']).values

# Normalize features (CRITICAL — save scaler params for C++ deployment)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_normal)

# Save scaler stats → will be hardcoded into ESP32 firmware
scaler_params = {
    "mean_": scaler.mean_.tolist(),
    "scale_": scaler.scale_.tolist()
}
with open("scaler_params.json", "w") as f:
    json.dump(scaler_params, f, indent=2)
print("Scaler params saved.")

# Elbow method to pick optimal K
inertias = []
for k in range(2, 8):
    km = KMeans(n_clusters=k, random_state=42, n_init=20)
    km.fit(X_scaled)
    inertias.append(km.inertia_)
print("Inertias:", inertias)  # Plot and pick elbow

# Train final model with K=3
kmeans = KMeans(n_clusters=3, random_state=42, n_init=50, max_iter=500)
kmeans.fit(X_scaled)

print("Centroids shape:", kmeans.cluster_centers_.shape)  # (3, 12)
print("Silhouette score:", silhouette_score(X_scaled, kmeans.labels_))

# Save model
joblib.dump(kmeans, "kmeans_model.joblib")

# Export centroids as JSON for C++ header generation
centroids_dict = {"centroids": kmeans.cluster_centers_.tolist()}
with open("centroids.json", "w") as f:
    json.dump(centroids_dict, f, indent=2)
print("Centroids exported to centroids.json")
```

**Model B — LSTM Autoencoder Training (`train_autoencoder.py`):**

```python
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
import pandas as pd

SEQ_LEN = 20   # 20 windows = ~5 seconds of context
N_FEAT  = 12

def build_autoencoder():
    inp = layers.Input(shape=(SEQ_LEN, N_FEAT))
    # Encoder
    x = layers.LSTM(64, return_sequences=True)(inp)
    x = layers.LSTM(32, return_sequences=False)(x)
    bottleneck = layers.Dense(16, activation='relu')(x)
    # Decoder
    x = layers.RepeatVector(SEQ_LEN)(bottleneck)
    x = layers.LSTM(32, return_sequences=True)(x)
    x = layers.LSTM(64, return_sequences=True)(x)
    out = layers.TimeDistributed(layers.Dense(N_FEAT))(x)
    return Model(inputs=inp, outputs=out)

# Build sequences from windowed normal data
df = pd.read_csv("features_all.csv")
X_norm = df[df.label == 'normal'].drop(columns=['label']).values
# Normalize
from sklearn.preprocessing import StandardScaler
sc = StandardScaler().fit(X_norm)
X_sc = sc.transform(df.drop(columns=['label']).values)

# Create overlapping sequences
def make_sequences(x, seq_len):
    return np.array([x[i:i+seq_len] for i in range(len(x)-seq_len)])

X_train = make_sequences(sc.transform(df[df.label=='normal']
                          .drop(columns=['label']).values), SEQ_LEN)

model = build_autoencoder()
model.compile(optimizer='adam', loss='mse')
model.summary()

history = model.fit(
    X_train, X_train,
    epochs=50, batch_size=32,
    validation_split=0.1,
    callbacks=[
        tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
        tf.keras.callbacks.ModelCheckpoint("autoencoder_best.h5", save_best_only=True)
    ]
)

# Convert to TFLite for optional server-side deployment
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
with open("autoencoder.tflite", "wb") as f:
    f.write(tflite_model)
print(f"TFLite model: {len(tflite_model)} bytes")
```

---

### 3.4 Step 4 — Validation & Threshold Calibration

```
VALIDATION FLOW
───────────────
  Test Data (all labels) ──► Normalize ──► K-Means distance calc
                                               │
                               ┌───────────────▼────────────────┐
                               │   Sweep threshold from 0 to 1  │
                               │   Calculate at each threshold:  │
                               │    • Precision                  │
                               │    • Recall                     │
                               │    • F1 Score                   │
                               │    • ROC-AUC                    │
                               └───────────────┬────────────────┘
                                               │
                               Pick threshold @ max F1
                                               │
                               ┌───────────────▼────────────────┐
                               │   WARNING  threshold = 0.45    │
                               │   CRITICAL threshold = 0.72    │
                               └────────────────────────────────┘
```

```python
# validate_model.py
import numpy as np, pandas as pd, joblib, json
from sklearn.metrics import (classification_report, confusion_matrix,
                              roc_auc_score, f1_score)
from sklearn.preprocessing import StandardScaler, label_binarize
import matplotlib.pyplot as plt, seaborn as sns

kmeans = joblib.load("kmeans_model.joblib")
with open("scaler_params.json") as f:
    sp = json.load(f)

# Manual scaler using saved params
def scale(X):
    return (X - np.array(sp["mean_"])) / np.array(sp["scale_"])

df_test = pd.read_csv("features_all.csv")
X_test = scale(df_test.drop(columns=['label']).values)
y_true = df_test['label'].values

# Compute distance to nearest centroid (anomaly score)
dists = kmeans.transform(X_test)           # shape (N, K)
min_dist = dists.min(axis=1)              # distance to nearest centroid
max_dist = min_dist.max()
anomaly_scores = min_dist / max_dist       # normalize 0–1

# Threshold sweep
best_f1, best_thr = 0, 0.5
y_bin = (y_true != 'normal').astype(int)
for thr in np.arange(0.1, 0.95, 0.01):
    pred = (anomaly_scores > thr).astype(int)
    f = f1_score(y_bin, pred)
    if f > best_f1:
        best_f1, best_thr = f, thr

print(f"Optimal threshold: {best_thr:.2f}  F1={best_f1:.3f}")

# Final evaluation
y_pred = np.where(anomaly_scores > best_thr, 'anomaly', 'normal')
print(classification_report(y_true, y_pred, target_names=['normal','anomaly']))

# Confusion matrix heatmap
cm = confusion_matrix(y_true, y_pred, labels=['normal','anomaly'])
sns.heatmap(cm, annot=True, fmt='d', xticklabels=['normal','anomaly'],
            yticklabels=['normal','anomaly'])
plt.title("K-Means Anomaly Detection — Confusion Matrix")
plt.savefig("confusion_matrix.png", dpi=150)
print("ROC-AUC:", roc_auc_score(y_bin, anomaly_scores))
```

---

### 3.5 Step 5 — Model Export to C++ Header Files

**Goal:** Convert Python floats into arrays the ESP32 firmware can use at compile time.

```python
# export_to_c_header.py
import json, numpy as np

with open("centroids.json") as f:
    centroids = np.array(json.load(f)["centroids"])  # shape (3, 12)
with open("scaler_params.json") as f:
    sp = json.load(f)

FEAT_NAMES = ['vib_rms','vib_peak','vib_crest','vib_kurt',
              'cur_rms','cur_std','dom_freq','spec_rms',
              'spec_cent','band1','band2','band3']
N_CLUSTERS = centroids.shape[0]
N_FEATURES = centroids.shape[1]

def fmt(arr):
    return ", ".join(f"{v:.8f}f" for v in arr)

header = f"""// AUTO-GENERATED — DO NOT EDIT
// Generated by export_to_c_header.py from trained K-Means model
#pragma once
#include <Arduino.h>

// --- Model Dimensions ---
#define KMEANS_N_CLUSTERS  {N_CLUSTERS}
#define KMEANS_N_FEATURES  {N_FEATURES}
#define ANOMALY_WARN_THR   0.45f
#define ANOMALY_CRIT_THR   0.72f

// --- StandardScaler Parameters ---
const float SCALER_MEAN[{N_FEATURES}] = {{ {fmt(sp['mean_'])} }};
const float SCALER_SCALE[{N_FEATURES}] = {{ {fmt(sp['scale_'])} }};

// --- K-Means Centroids [{N_CLUSTERS} x {N_FEATURES}] ---
const float KMEANS_CENTROIDS[{N_CLUSTERS}][{N_FEATURES}] = {{
"""
for i, c in enumerate(centroids):
    header += f"    {{ {fmt(c)} }},  // Cluster {i}\n"

header += "};\n"

with open("../firmware/src/ml/model_params.h", "w") as f:
    f.write(header)
print("Exported: firmware/src/ml/model_params.h")
```

**Output file `model_params.h` (excerpt):**
```c
#pragma once
#define KMEANS_N_CLUSTERS  3
#define KMEANS_N_FEATURES  12
#define ANOMALY_WARN_THR   0.45f
#define ANOMALY_CRIT_THR   0.72f

const float SCALER_MEAN[12] = {0.98234560f, 1.23400000f, ...};
const float SCALER_SCALE[12] = {0.12345678f, 0.09876543f, ...};

const float KMEANS_CENTROIDS[3][12] = {
    {0.02134567f, 0.98123456f, ...},  // Cluster 0 — normal idle
    {0.03456789f, 1.12345678f, ...},  // Cluster 1 — normal load
    {0.05678901f, 1.34567890f, ...},  // Cluster 2 — normal high-speed
};
```

---

## 4. Stage 2 � ESP32 Edge Integration & Real-Time Inference

```
+----------------------------------------------------------------------+
�       STAGE 2: ESP32-S3 FIRMWARE � COMPLETE RUNTIME PIPELINE        �
�----------------------------------------------------------------------�
�                                                                      �
�  +----------+   I2C @100Hz  +----------------------------------+   �
�  � MPU6050  �--------------?�   FreeRTOS Task 1: SENSOR TASK   �   �
�  � 3-axis   �               �   Priority: HIGH  Stack: 4096B   �   �
�  +----------+               �   � Reads 256-sample window       �   �
�                              �   � xQueueSend(raw_queue)        �   �
�  +----------+   ADC @1kHz   +----------------------------------+   �
�  � ACS712   �--------------?�               �                       �
�  � Current  �               ?               �                       �
�  +----------+  +----------------------------?------------------+   �
�                �   FreeRTOS Task 2: FEATURE TASK                �   �
�                �   Priority: MEDIUM                             �   �
�                �   � RMS, Peak, Crest, Kurtosis                �   �
�                �   � FFT (fix_fft integer implementation)       �   �
�                �   � Normalize with SCALER_MEAN/SCALER_SCALE   �   �
�                �   � xQueueSend(feature_queue)                  �   �
�                +----------------------------------------------+   �
�                                    �                               �
�                +-------------------?--------------------------+   �
�                �   FreeRTOS Task 3: INFERENCE TASK            �   �
�                �   � Euclidean dist to each centroid           �   �
�                �   � anomaly_score = min_dist / MAX_DIST       �   �
�                �   � Apply WARN/CRIT thresholds                �   �
�                �   � Push to ring_buffer if MQTT offline       �   �
�                +----------------------------------------------+   �
�                                    �                               �
�                +-------------------?--------------------------+   �
�                �   FreeRTOS Task 4: MQTT PUBLISH TASK         �   �
�                �   � Build Sparkplug B JSON payload            �   �
�                �   � TLS via WiFiClientSecure                  �   �
�                �   � mqtt.publish(NDATA_TOPIC, payload)        �   �
�                �   � Subscribe NCMD ? relay_set()             �   �
�                +----------------------------------------------+   �
+----------------------------------------------------------------------+
```

### 4.1 Firmware Project Structure

```
firmware/
+-- platformio.ini
+-- certs/
�   +-- ca.crt
�   +-- client.key
+-- src/
    +-- main.cpp               ? Task spawning, setup, loop
    +-- config.h               ? WiFi/MQTT credentials, GPIO pins
    +-- sensors/
    �   +-- vibration.h/cpp    ? MPU6050 I2C driver + 256-sample buffer
    �   +-- current.h/cpp     ? ACS712 ADC + moving average filter
    +-- dsp/
    �   +-- features.h/cpp    ? RMS, peak, crest, kurtosis
    �   +-- fft.h/cpp         ? fix_fft integer FFT
    +-- ml/
    �   +-- model_params.h    ? AUTO-GENERATED from Python export script
    �   +-- scaler.h/cpp      ? StandardScaler apply (subtract mean / divide std)
    �   +-- kmeans.h/cpp      ? Euclidean distance + anomaly scoring
    +-- comms/
    �   +-- wifi_manager.h/cpp ? Connect + exponential backoff reconnect
    �   +-- mqtt_client.h/cpp  ? PubSubClient wrapper + LWT registration
    �   +-- sparkplug.h/cpp    ? Sparkplug B JSON payload builder
    +-- control/
    �   +-- relay.h/cpp        ? Relay GPIO + NCMD command handler
    +-- storage/
        +-- ring_buffer.h/cpp  ? Circular offline buffer using PSRAM
```

**`platformio.ini`:**
```ini
[env:esp32-s3-devkitc-1]
platform  = espressif32
board     = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200
board_build.arduino.memory_type = qio_opi
board_upload.flash_size = 8MB
lib_deps =
    adafruit/Adafruit MPU6050 @ ^2.2.4
    knolleary/PubSubClient @ ^2.8.0
    bblanchon/ArduinoJson @ ^6.21.0
build_flags =
    -DBOARD_HAS_PSRAM
    -DCORE_DEBUG_LEVEL=1
```

### 4.2 K-Means Inference Engine (`ml/kmeans.cpp`)

```cpp
// kmeans.cpp � K-Means anomaly detection inference on ESP32
#include "kmeans.h"
#include "model_params.h"   // AUTO-GENERATED from Python
#include <math.h>

static float feat_scaled[KMEANS_N_FEATURES];

static void apply_scaler(const float *raw, float *scaled) {
    for (int j = 0; j < KMEANS_N_FEATURES; j++) {
        scaled[j] = (raw[j] - SCALER_MEAN[j]) / (SCALER_SCALE[j] + 1e-9f);
    }
}

static float euclidean_dist(const float *a, const float *b, int n) {
    float sum = 0.0f;
    for (int i = 0; i < n; i++) {
        float d = a[i] - b[i];
        sum += d * d;
    }
    return sqrtf(sum);
}

AnomalyResult kmeans_infer(const FeatureVec *fvec) {
    float raw[KMEANS_N_FEATURES] = {
        fvec->vib_rms, fvec->vib_peak, fvec->vib_crest, fvec->vib_kurt,
        fvec->cur_rms, fvec->cur_std,
        fvec->dom_freq, fvec->spec_rms, fvec->spec_cent,
        fvec->band1, fvec->band2, fvec->band3
    };
    apply_scaler(raw, feat_scaled);

    float min_dist = 9999.0f;
    int   nearest  = 0;
    for (int k = 0; k < KMEANS_N_CLUSTERS; k++) {
        float d = euclidean_dist(feat_scaled, KMEANS_CENTROIDS[k], KMEANS_N_FEATURES);
        if (d < min_dist) { min_dist = d; nearest = k; }
    }

    const float MAX_EXPECTED_DIST = 4.5f;
    AnomalyResult res;
    res.score           = fminf(min_dist / MAX_EXPECTED_DIST, 1.0f);
    res.nearest_cluster = nearest;

    if      (res.score >= ANOMALY_CRIT_THR) res.label = LABEL_CRITICAL;
    else if (res.score >= ANOMALY_WARN_THR) res.label = LABEL_WARNING;
    else                                    res.label = LABEL_NORMAL;
    return res;
}
```

---

## 5. Docker Container Infrastructure

### 5.1 Full `docker-compose.yml`

```yaml
version: '3.8'

networks:
  hvac_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24

volumes:
  influxdb_data:
  grafana_data:

services:

  mosquitto:
    image: eclipse-mosquitto:2
    container_name: mosquitto
    restart: unless-stopped
    networks:
      hvac_net:
        ipv4_address: 172.20.0.2
    ports:
      - "1883:1883"
      - "8883:8883"
    volumes:
      - ./mosquitto/config/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - ./mosquitto/config/passwd:/mosquitto/config/passwd
      - ./mosquitto/certs:/mosquitto/certs
      - ./mosquitto/data:/mosquitto/data

  nodered:
    image: nodered/node-red:3-minimal
    container_name: nodered
    restart: unless-stopped
    depends_on: [mosquitto, influxdb]
    networks:
      hvac_net:
        ipv4_address: 172.20.0.3
    ports:
      - "1880:1880"
    environment:
      - NODE_RED_CREDENTIAL_SECRET=${NODE_RED_SECRET}
    volumes:
      - ./nodered/data:/data

  influxdb:
    image: influxdb:2.7
    container_name: influxdb
    restart: unless-stopped
    networks:
      hvac_net:
        ipv4_address: 172.20.0.4
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=${INFLUX_PASS}
      - DOCKER_INFLUXDB_INIT_ORG=hvac_lab
      - DOCKER_INFLUXDB_INIT_BUCKET=hvac_data
      - DOCKER_INFLUXDB_INIT_RETENTION=30d
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUX_TOKEN}
    volumes:
      - influxdb_data:/var/lib/influxdb2

  grafana:
    image: grafana/grafana-oss:10.2.0
    container_name: grafana
    restart: unless-stopped
    depends_on: [influxdb]
    networks:
      hvac_net:
        ipv4_address: 172.20.0.5
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASS}
      - GF_INSTALL_PLUGINS=grafana-mqtt-datasource,natel-discrete-panel,marcusolsson-dynamictext-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning

  telegraf:
    image: telegraf:1.29
    container_name: telegraf
    restart: unless-stopped
    depends_on: [influxdb]
    networks:
      hvac_net:
        ipv4_address: 172.20.0.6
    volumes:
      - ./telegraf/telegraf.conf:/etc/telegraf/telegraf.conf:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro

  portainer:
    image: portainer/portainer-ce:latest
    container_name: portainer
    restart: unless-stopped
    networks:
      hvac_net:
        ipv4_address: 172.20.0.7
    ports:
      - "9000:9000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./portainer/data:/data
```

---

## 6. End-to-End Data Flow (All Stages)

### 6.1 Uplink Data Flow � Sensor to Dashboard

```
TIME     LOCATION            DATA STATE
------   -----------------   -------------------------------------------------
T+0ms    MPU6050 (I2C)       Raw 16-bit integers: ax=1024, ay=-32, az=16001
         ACS712 (ADC)        Raw 12-bit ADC: 512 counts ? 0.52A
                               �
T+2ms    ESP32 DSP Core      256-sample window accumulated
         features.cpp         Feature vector computed:
                              [vib_rms=0.981, vib_peak=1.24, crest=1.26,
                               kurt=3.12, cur_rms=0.52, cur_std=0.02,
                               dom_freq=12.5, band1=124, band2=45, band3=12]
                               �
T+3ms    ESP32 ML Core       Scaled by SCALER_MEAN / SCALER_SCALE
         kmeans.cpp           Dist: centroid[0]=0.31, [1]=0.44, [2]=2.11
                              anomaly_score = 0.31/4.5 = 0.07  label="normal"
                               �
T+5ms    ESP32 MQTT Task     JSON Sparkplug B payload built + TLS encrypted
         mqtt_client.cpp      Published to 192.168.1.X:8883
                               �
T+8ms    Mosquitto           Received: spBv1.0/buildingA/NDATA/area1/hvac_fan01
         Container            QoS 1 ACK sent back. Fanned out to subscribers.
                               �
T+9ms    Node-RED            MQTT In ? Sparkplug B Decoder ? Validate
         Container            ? InfluxDB write (Line Protocol):
                              "hvac_sensor,device=hvac_fan01 vib_rms=0.981,
                               anomaly_score=0.07 1713620229000000000"
                               �
T+10ms   InfluxDB            Point stored in bucket "hvac_data"
         Container            Measurement: hvac_sensor, ns precision timestamp
                               �
T+60s    Node-RED RUL Flow   Queries last 1hr vib_rms from InfluxDB
         Container            Linear regression: slope=0.0002, R�=0.87
                              RUL = (3.0 - 0.981) / 0.0002 = 2.8 hours
                              Written back to InfluxDB + published to MQTT
                               �
T+~2s    Grafana             Flux query on 5-second refresh interval
         Dashboard            Gauges, time-series, RUL, Digital Twin updated
```

### 6.2 Downlink Control Flow � Dashboard to Physical Fan

```
[User clicks "FAN OFF" in Grafana]
           �  HTTP POST to Node-RED webhook :1880
           ?
[Node-RED] Validates command ? Builds NCMD Sparkplug B payload
           �  MQTT publish to:
           �  spBv1.0/buildingA/NCMD/area1/hvac_fan01
           ?
[Mosquitto] Routes to ESP32 subscriber
           ?
[ESP32]    mqtt_command_callback() ? relay_set(false) ? GPIO LOW
           �  Fan power cuts immediately
           �  Publishes confirmation NDATA: {fan_state: false}
           ?
[Grafana]  Fan State indicator ? RED. Digital Twin fan stops spinning.
```

### 6.3 Fault Injection Demo � What Happens During Anomaly

```
PHYSICAL: 25g weight attached to fan blade
------------------------------------------------------------------

  Feature Changes vs Normal Baseline:
    vib_rms:  0.98 ? 2.41  (+146%)   ? strong imbalance
    vib_peak: 1.24 ? 3.87  (+212%)
    vib_kurt: 3.12 ? 6.84            ? impulse events
    band1:    124  ? 412             ? low-freq imbalance band power up
    cur_std:  0.02 ? 0.09            ? motor working harder

  K-Means Result:
    min_dist = 2.98 (was 0.31)
    anomaly_score = 2.98/4.5 = 0.66  ? ABOVE WARNING threshold 0.45
    label = "warning"

  Node-RED Alert Flow:
    Score 0.66 > 0.45 ? Email alert sent
    MQTT published to alert topic

  Grafana:
    Anomaly Score gauge ? YELLOW zone
    Alert banner: "WARNING: Imbalance detected on hvac_fan01"

  [Add more weight ? score > 0.72 ? CRITICAL ? RED alert]
```

---

## 7. Step-by-Step Implementation Guide

### Phase 1: PC & Docker Setup (Day 1)
```
? Install Docker Desktop (WSL2 backend on Windows)
? Install VS Code + PlatformIO extension
? pip install pandas numpy scikit-learn matplotlib scipy tensorflow pyserial joblib seaborn
? Create folder structure: mosquitto/{config,certs,data,log}, nodered/data, influxdb/, grafana/
? Generate TLS certs with openssl (see Section 5.3 commands)
? Create mosquitto.conf (TLS + password auth)
? Run: mosquitto_passwd -c ./mosquitto/config/passwd esp32_device
? Add INFLUX_TOKEN, GRAFANA_PASS, NODE_RED_SECRET to .env file
? Run: docker compose up -d
? Verify: docker compose ps  (all 6 containers healthy)
? Open InfluxDB at http://localhost:8086 ? create org=hvac_lab, bucket=hvac_data
```

### Phase 2: Hardware Wiring (Day 2)
```
ESP32-S3 Pin Connections:
  MPU6050 VCC ? 3V3       MPU6050 SDA ? GPIO 8
  MPU6050 GND ? GND       MPU6050 SCL ? GPIO 9
  ACS712  VCC ? 5V        ACS712  OUT ? GPIO 36 (ADC)
  ACS712  GND ? GND
  Relay   IN  ? GPIO 4    Relay   VCC ? 5V
  Fan Circuit: 12V+ ? ACS712 IN+ ? ACS712 IN- ? Relay COM ? Relay NO ? Fan+ ? Fan- ? 12V-
```

### Phase 3: Data Collection & Model Training (Day 3-4)
```
? Flash ESP32 with data-collection firmware (Serial print mode)
? Session S1 (normal, 20min):  python collect_data.py  [set LABEL=normal]
? Session S2 (normal 50% speed): repeat with slower RPM
? Session S3 (warning):  attach 10g weight, python collect_data.py [LABEL=warning]
? Session S4 (critical): attach 25g weight, [LABEL=critical]
? python feature_engineering.py  ? generates features_*.csv files
? python train_kmeans.py          ? generates centroids.json + scaler_params.json
? python train_autoencoder.py     ? generates autoencoder.tflite
? python validate_model.py        ? prints confusion matrix + F1 + ROC-AUC
? python export_to_c_header.py    ? generates firmware/src/ml/model_params.h
? Note down ANOMALY_WARN_THR and ANOMALY_CRIT_THR values
```

### Phase 4: Flash Production Firmware (Day 4-5)
```
? Update firmware/src/config.h: WiFi SSID/Pass, MQTT broker IP, credentials
? PlatformIO Build ? verify zero errors
? PlatformIO Upload ? flash to ESP32-S3
? Serial Monitor ? verify:
    [OK] MPU6050 initialized
    [MQTT] Connected + LWT registered
    [PUB] NDATA published  (every ~2.56 seconds)
? docker logs mosquitto ? see ESP32 CONNECT event
? InfluxDB Data Explorer ? verify hvac_sensor measurement receiving points
```

### Phase 5: Node-RED Flows (Day 5)
```
? Open http://localhost:1880 ? Palette Manager ? Install:
    node-red-contrib-influxdb
    node-red-contrib-sparkplug-b
    node-red-node-email
? Build Flow 1: [MQTT In] ? [Sparkplug Decoder] ? [Validate] ? [InfluxDB Out]
? Build Flow 2: [Inject 60s] ? [InfluxDB Query] ? [LinReg Function] ? [InfluxDB Write]
? Build Flow 3: [HTTP In /relay] ? [Validate] ? [Build NCMD] ? [MQTT Out]
? Build Flow 4: [MQTT In] ? [Check score>0.45] ? [Email] + [Dashboard msg]
? Deploy all flows ? verify data flowing through
```

### Phase 6: Grafana Dashboards (Day 5-6)
```
? Add InfluxDB datasource: URL=http://influxdb:8086, Org=hvac_lab, Token=<token>
? Create dashboard "HVAC Fan Monitor" with panels:
    Panel 1: Vibration RMS Gauge  (thresholds: green<1.5 yellow<2.5 red)
    Panel 2: Anomaly Score Gauge  (0�1, green<0.45 yellow<0.72 red)
    Panel 3: Current RMS Time Series (30-min window)
    Panel 4: Spectral Band Power (band1/band2/band3 stacked area)
    Panel 5: RUL Estimate (Stat panel, hours remaining)
    Panel 6: Digital Twin (Dynamic Text SVG fan animation)
    Panel 7: Health Index Bar (100% - anomaly_score*100)
    Panel 8: Relay ON/OFF Button (webhook ? Node-RED /relay)
? Set 5-second auto-refresh
? Test Fault Injection: attach weight ? see anomaly score spike in real time
? Test Bidirectional Control: click relay button ? fan physically responds
```

---

> **Result:** A production-grade IIoT system demonstrating:
> - **TinyML inference** at 2.56-second cycles on ESP32-S3 (sub-50ms latency)
> - **Dual-model anomaly detection** (K-Means edge + LSTM server-side)
> - **6-container Docker stack** with full observability and management
> - **TLS-encrypted Sparkplug B** MQTT pipeline
> - **Remaining Useful Life prediction** with R� confidence score
> - **Bidirectional Digital Twin** control (Grafana ? Relay ? Fan)
> - **Offline resilience** via PSRAM circular ring buffer
> - **Production security**: TLS 1.2, ACL, LWT, credential management
