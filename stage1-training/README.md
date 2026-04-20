# 🧠 Stage 1 — ML Training Pipeline

> **Goal:** Collect sensor data from a real HVAC fan, extract features, train anomaly detection models, validate them, and export the trained model as a C++ header file for the ESP32.

---

## 📦 What's In This Folder

| File | Purpose |
|------|---------|
| `firmware/data_collector/data_collector.ino` | ESP32 Arduino sketch — reads sensors at 100Hz, prints CSV over Serial |
| `collect_data.py` | Python serial logger — captures ESP32 output into labelled CSV files |
| `feature_engineering.py` | Converts raw CSV → 12-feature vectors using sliding windows |
| `train_kmeans.py` | Trains K-Means clustering on normal data (→ centroids + scaler) |
| `train_autoencoder.py` | Trains LSTM Autoencoder on normal sequences (optional, for server-side) |
| `validate_model.py` | Tests model on ALL data, finds optimal thresholds, generates plots |
| `export_to_c_header.py` | Exports model to `model_params.h` for ESP32 C++ firmware |
| `requirements.txt` | Python dependencies |

---

## 🔌 Hardware Wiring (ESP32 DevKit WROOM-32)

> Your board: **ESP32 DevKit v1 (WROOM-32)** with pins: 3V3, GND, D2, D4, D5, D12-D15, D18, RX2, TX2, VIN, etc.

### Pin Connections

| Component | Component Pin | ESP32 Pin | Board Label | Notes |
|-----------|--------------|-----------|-------------|-------|
| **MPU6050** | VCC | 3V3 | `3V3` | Power (3.3V only!) |
| **MPU6050** | GND | GND | `GND` | Ground |
| **MPU6050** | SDA | **GPIO 21** | `D21` | I2C Data (default SDA) |
| **MPU6050** | SCL | **GPIO 22** | `D22` | I2C Clock (default SCL) |
| **MPU6050** | AD0 | GND | `GND` | Sets I2C address to 0x68 |
| **ACS712** | VCC | VIN (5V) | `VIN` | Module needs 5V power |
| **ACS712** | GND | GND | `GND` | Ground |
| **ACS712** | OUT | **GPIO 34** | `D34` | ADC input (read-only pin, no pullup) |

### Wiring Diagram

```
    ESP32 DevKit (WROOM-32)
    ========================
    Left side:              Right side:
    ─────────               ──────────
    3V3  ── MPU6050 VCC     VIN ── ACS712 VCC (5V)
    GND  ── MPU6050 GND     GND ── ACS712 GND
    D21  ── MPU6050 SDA     D34 ── ACS712 OUT (via divider)
    D22  ── MPU6050 SCL
    GND  ── MPU6050 AD0
```

### Fan Power Circuit

The fan is powered by a **separate 12V supply**. The ACS712 sits **inline** to measure current:

```
12V PSU (+) → ACS712 IP+ → ACS712 IP- → Fan (+)
Fan (-) → 12V PSU (-)
```

### Voltage Divider for ACS712 (5V output → safe for ESP32 ADC)

```
ACS712 OUT ──┬── 10kΩ ──┬── D34 (GPIO 34)
             │          │
             └── 10kΩ ──┴── GND
```
This halves the 0-5V signal to 0-2.5V (safe for ESP32 ADC which handles 0-3.3V).

> **Note:** If your ACS712 module runs on 3.3V and outputs 0-3.3V, skip the voltage divider and connect OUT directly to D34.

---

## 🌀 Fan States for Data Collection

You need to collect data in **4 different conditions**. Each creates a labelled dataset.

### State 1: `normal` — Clean Fan, Full Speed
- **Setup:** No weights. Fan runs freely.
- **Duration:** 20 minutes
- **What to do:** Just let it spin. Don't touch anything.
- **Expected samples:** ~120,000

### State 2: `normal_low` — Clean Fan, Restricted Airflow
- **Setup:** No weights. Hold a piece of cardboard 2-3cm from the fan's air intake.
- **Duration:** 15 minutes
- **What to do:** Keep cardboard in place the whole time. This simulates the fan running in a duct or under different load conditions.
- **Expected samples:** ~90,000

### State 3: `warning` — Mild Imbalance (8-12g weight)
- **⚠️ Turn fan OFF first!**
- **Setup:** Tape a small weight to the **edge of ONE blade**:
  - 1 × steel M6 nut (~8g), OR
  - 2 × stacked coins (~10g), OR
  - A small blob of blu-tack (~10g)
- Secure with strong tape so it won't fly off
- **Duration:** 10 minutes
- **What to do:** Turn fan ON. It should wobble slightly and sound different.
- **Expected samples:** ~60,000

### State 4: `critical` — Severe Imbalance (20-30g weight)
- **⚠️ Turn fan OFF first!**
- **Setup:** Tape a heavier weight to the same blade:
  - 1 × M10 bolt (~25g), OR
  - 4-5 × stacked coins (~25g), OR
  - A large blob of heavy blu-tack
- **Duration:** 10 minutes
- **What to do:** Turn fan ON. It will shake significantly and sound loud.
- **⚠️ Safety:** Hold the fan mount if it moves. Stop if anything looks like it will detach.
- **Expected samples:** ~60,000

### Data Volume Summary

| State | Label | Duration | Raw Samples | After Feature Extraction |
|-------|-------|----------|-------------|------------------------|
| 1 | `normal` | 20 min | ~120,000 | ~935 windows |
| 2 | `normal_low` | 15 min | ~90,000 | ~700 windows |
| 3 | `warning` | 10 min | ~60,000 | ~467 windows |
| 4 | `critical` | 10 min | ~60,000 | ~467 windows |
| **Total** | — | **55 min** | **~330,000** | **~2,570 windows** |

> Window = 256 samples (2.56 sec), Hop = 128 (50% overlap).
> Each window → 1 feature vector with 12 floats.

---

## 🚀 Step-by-Step Execution Guide

### STEP 0: Install Software

```bash
# 1. Install Arduino IDE 2.x from https://www.arduino.cc/en/software
#    OR install VS Code + PlatformIO extension

# 2. In Arduino IDE, install the ESP32 board package:
#    File → Preferences → Additional Board URLs:
#    https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
#    Then: Tools → Board → Boards Manager → Search "esp32" → Install

# 3. Install required Arduino libraries:
#    Sketch → Include Library → Manage Libraries:
#      - Adafruit MPU6050
#      - Adafruit Unified Sensor

# 4. Install Python dependencies:
cd D:\Sem7\CO326-Project\stage1-training
pip install -r requirements.txt
```

### STEP 1: Flash ESP32 Firmware

1. Open `firmware/data_collector/data_collector.ino` in Arduino IDE
2. Select your board: **Tools → Board → ESP32 Dev Module** (under ESP32 Arduino)
3. Select port: **Tools → Port → COM?** (your ESP32 COM port)
4. Click **Upload** (→ button)
5. Open **Serial Monitor** at **115200 baud**
6. You should see:
   ```
   ========================================
     HVAC Fan Data Collector — Stage 1
   ========================================
   [INIT] MPU6050... OK!
   [INIT] MPU6050 configured:
     Accel range: ±4g
     ...
   READY
   DATA:1234,0.0123,-0.0034,9.8100,0.0010,-0.0020,0.0000,2048
   DATA:1244,0.0156,-0.0012,9.8090,...
   ```
7. **Verify sensors:**
   - Tap the MPU6050 → ax/ay/az values should spike briefly
   - Turn fan ON → current_raw should change from ~2048 (0A baseline)
8. **Close Serial Monitor** before running Python script (it locks the port)

### STEP 2: Collect Data (All 4 States)

Run each command one at a time. Follow the fan state setup instructions above.

```bash
cd D:\Sem7\CO326-Project\stage1-training

# State 1: Normal (20 minutes)
python collect_data.py normal --port COM5 --duration 20

# State 2: Normal Low (15 minutes)
python collect_data.py normal_low --port COM5 --duration 15

# State 3: Warning - attach ~10g weight first! (10 minutes)
python collect_data.py warning --port COM5 --duration 10

# State 4: Critical - attach ~25g weight first! (10 minutes)
python collect_data.py critical --port COM5 --duration 10
```

> **Change `COM5`** to your actual ESP32 port.
> To find your port: `python collect_data.py normal --port COM1 --list-ports`

After each run, verify a CSV file was created in `data/`:
```bash
dir data\raw_*.csv
```

### STEP 3: Extract Features

```bash
python feature_engineering.py
```

This reads all `data/raw_*.csv` files and outputs `data/features_all.csv`.
You should see:
```
  Total feature vectors: 2,570
  Per-label breakdown:
    normal         :    935 windows
    normal_low     :    700 windows
    warning        :    467 windows
    critical       :    467 windows
```

### STEP 4: Train K-Means Model

```bash
python train_kmeans.py
```

This trains K-Means on **normal data only** and outputs:
- `data/kmeans_model.joblib` — saved model
- `data/centroids.json` — 3 centroids × 12 features
- `data/scaler_params.json` — normalization parameters
- `data/elbow_plot.png` — K selection chart
- `data/cluster_scatter.png` — PCA visualization of clusters

### STEP 5: Train LSTM Autoencoder (Optional)

```bash
python train_autoencoder.py
```

This is **optional** — the Autoencoder runs on the server in Stage 2, not on the ESP32.
Skip this if you don't have TensorFlow installed or want to save time.

### STEP 6: Validate Model

```bash
python validate_model.py
```

This tests the K-Means model on ALL data and outputs:
- Optimal WARNING and CRITICAL thresholds
- F1 score and ROC AUC
- `data/confusion_matrix.png`
- `data/roc_curve.png`
- `data/score_distribution.png`
- `data/threshold_results.json`

**Key Output to Check:**
```
  WARNING  threshold = 0.XXXX
  CRITICAL threshold = 0.XXXX
  F1 Score           = 0.XXXX  (should be > 0.80)
  ROC AUC            = 0.XXXX  (should be > 0.85)
```

### STEP 7: Export to C++ Header

```bash
python export_to_c_header.py
```

Generates `data/model_params.h` — this file will be copied into the Stage 2 firmware.

---

## ✅ Stage 1 Complete — What You Have Now

| Output File | What It Is | Used In |
|-------------|-----------|---------|
| `data/model_params.h` | C++ header with centroids + scaler + thresholds | Stage 2 ESP32 firmware |
| `data/centroids.json` | Raw centroid data | Documentation / reference |
| `data/scaler_params.json` | Feature normalization params | Stage 2 ESP32 firmware |
| `data/threshold_results.json` | Calibrated thresholds | Stage 2 Node-RED alerts |
| `data/autoencoder.tflite` | LSTM model (optional) | Stage 2 Node-RED server |
| `data/*.png` | Validation plots | Your project report |

**Next:** Tell me to start Stage 2, and I'll create the production ESP32 firmware + Docker stack.
