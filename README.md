# HVAC Blower Fan Predictive Maintenance

CO326 project repository for an HVAC blower fan predictive maintenance prototype built around an ESP32, vibration/current sensing, lightweight anomaly detection, MQTT telemetry, and a Docker-based IIoT monitoring stack.

## What This Repository Contains

This repository is not a single polished application. It contains three related parts at different maturity levels:

1. `stage1-training/`
   PC-side data collection, feature engineering, model training, validation, and export of K-Means model parameters for embedded use.
2. `Project/`
   Structured CO326 implementation scaffold with modular ESP32 firmware, Docker orchestration, Node-RED flow, and architecture documents.
3. `iot-docker-project/`
   Earlier standalone MQTT + Node-RED + InfluxDB + Grafana prototype with a simple ESP32 publisher and persisted runtime data.

## System Goal

The intended end-to-end system monitors a 12V HVAC-style blower fan using:

- `MPU6050` for vibration
- `ACS712` for motor current
- `ESP32` for sensing, local inference, and relay control
- `Mosquitto` for MQTT transport
- `Node-RED` for routing, alerting, and control logic
- `InfluxDB` for time-series storage
- `Grafana` for dashboards

The core predictive-maintenance idea is:

1. Collect labeled operating data from the fan.
2. Convert raw signals into compact statistical/spectral features.
3. Train a model on normal behavior.
4. Run anomaly scoring at the edge.
5. Stream health data to an IIoT dashboard.
6. Optionally switch the fan off through a relay when a critical fault is detected.

## Repository Layout

```text
.
├── README.md
├── ML_Pipeline_Architecture.md
├── stage1-training/
│   ├── README.md
│   ├── collect_data.py
│   ├── feature_engineering.py
│   ├── train_kmeans.py
│   ├── train_autoencoder.py
│   ├── validate_model.py
│   ├── export_to_c_header.py
│   ├── requirements.txt
│   └── firmware/data_collector/data_collector.ino
├── Project/
│   ├── README.md
│   ├── CO326_Implementation_Plan.md
│   ├── docker-compose.yml
│   ├── firmware/
│   │   ├── platformio.ini
│   │   └── src/
│   │       ├── main.cpp
│   │       ├── comms/mqtt_manager.h
│   │       ├── control/relay_controller.h
│   │       ├── ml/anomaly_detector.h
│   │       └── sensors/
│   ├── docker/
│   │   ├── mosquitto/config/mosquitto.conf
│   │   └── nodered/data/flows.json
│   ├── analytics/notebooks/kmeans_training_stub.py
│   └── doc/
│       ├── architecture.md
│       ├── analytics_details.md
│       ├── mqtt_topics.md
│       └── Other_Docs/
└── iot-docker-project/
    ├── readme.md
    ├── docker-compose.yml
    ├── sketch_apr20b/sketch_apr20b.ino
    ├── mosquitto/
    ├── nodered/
    ├── influxdb/
    └── grafana/
```

## Main Sections

### 1. `stage1-training/`

This is the most complete functional part of the repository.

It implements the offline ML workflow:

- `collect_data.py`
  Reads serial output from the ESP32 and stores labeled CSV files for states such as `normal`, `normal_low`, `warning`, and `critical`.
- `feature_engineering.py`
  Converts raw sensor streams into 12 engineered features using 256-sample sliding windows with 50% overlap.
- `train_kmeans.py`
  Trains a K-Means model on normal data only, saves centroids and normalization parameters, and produces elbow/PCA plots.
- `validate_model.py`
  Scores all labeled data, derives warning/critical thresholds, and outputs validation plots and metrics.
- `train_autoencoder.py`
  Optional server-side LSTM autoencoder workflow using TensorFlow.
- `export_to_c_header.py`
  Generates `model_params.h` so the trained scaler, centroids, and thresholds can be embedded in ESP32 firmware.
- `firmware/data_collector/data_collector.ino`
  Real data-acquisition firmware for the ESP32 DevKit that samples the MPU6050 and ACS712 at 100 Hz and prints `DATA:` CSV lines over serial.

### 2. `Project/`

This is the structured project implementation area intended to tie the whole system together.

Key parts:

- `Project/firmware/`
  PlatformIO-based modular ESP32 firmware layout.
  The code currently defines clean module boundaries for MQTT, sensors, relay control, and anomaly detection.
  The current implementation is still a scaffold:
  - `accel_sensor.h` and `current_sensor.h` return synthetic values.
  - `anomaly_detector.h` uses a simple 2-feature Euclidean-distance stub.
  - `main.cpp` publishes JSON to MQTT every 2 seconds and listens for relay commands.
- `Project/docker-compose.yml`
  Brings up Mosquitto, Node-RED, InfluxDB, and Grafana.
- `Project/docker/mosquitto/config/mosquitto.conf`
  Simple anonymous MQTT broker configuration with TCP and WebSocket listeners.
- `Project/docker/nodered/data/flows.json`
  Minimal Node-RED flow that subscribes to `hvac_fan01/data/#` and shows payloads in debug.
- `Project/doc/`
  Small documentation set describing the intended architecture, MQTT topics, analytics logic, and implementation plan.

This section is best understood as the main integration target, but not yet the fully realized production implementation described in the higher-level architecture docs.

### 3. `iot-docker-project/`

This is an earlier standalone prototype for the containerized telemetry stack.

It includes:

- `docker-compose.yml`
  A simple four-service stack: Mosquitto, Node-RED, InfluxDB, and Grafana.
- `sketch_apr20b/sketch_apr20b.ino`
  A minimal ESP32 publisher that connects to Wi‑Fi, generates random `x/y/z` values, and publishes JSON to `test/topic`.
- persisted runtime state:
  - Grafana database and plugin files
  - InfluxDB data files
  - Mosquitto data/logs
  - Node-RED settings, credentials, `node_modules`

This directory is useful as a working prototype/snapshot, but it also contains generated data and environment artifacts that should usually not be treated as authored source.

## ML Pipeline Summary

The intended ML pipeline is:

1. Sample vibration and current at `100 Hz`.
2. Build windows of `256 samples` with a `128-sample` hop.
3. Extract 12 features:
   - `vib_rms`, `vib_peak`, `vib_crest`, `vib_kurt`
   - `cur_rms`, `cur_std`
   - `dom_freq`, `spec_rms`, `spec_cent`
   - `band1`, `band2`, `band3`
4. Normalize features with `StandardScaler`.
5. Train `K-Means` on normal windows.
6. Use distance to nearest centroid as anomaly score.
7. Calibrate warning and critical thresholds.
8. Export model parameters for embedded C++ inference.

## Current State

What is already concrete:

- Stage 1 data collection and ML training scripts
- ESP32 serial data-collector firmware
- A modular PlatformIO firmware scaffold
- Docker compose files for the IIoT stack
- Node-RED and Mosquitto starter configuration
- architecture and planning documents

What is still partial or prototype-level:

- `Project/firmware` sensor and ML modules are stubs
- Node-RED logic in `Project/` is minimal
- Grafana provisioning for the `Project/` stack is not present
- the repo contains duplicated concepts across `Project/` and `iot-docker-project/`
- `iot-docker-project/` includes checked-in runtime/generated files

## Recommended Way To Read The Repo

If you are trying to understand the repository quickly:

1. Start with `stage1-training/README.md`.
2. Read `Project/CO326_Implementation_Plan.md`.
3. Read `Project/doc/architecture.md`, `analytics_details.md`, and `mqtt_topics.md`.
4. Inspect `Project/firmware/src/main.cpp` and its headers.
5. Treat `iot-docker-project/` as an earlier prototype/environment snapshot.

## Notes

- The top-level `ML_Pipeline_Architecture.md` is a broader architecture narrative and is more ambitious than the current codebase.
- Some documents describe advanced features such as digital twin behavior, TLS, Sparkplug B, buffering, and richer anomaly logic that are not fully implemented in the checked-in source.
- Do not assume every documented feature already exists in code; several documents are design-forward.

## Contributors


### Team Members

  - **[Full Name 1]**
  - **[Full Name 2]**
  - **[Full Name 3]**
  - **E/20/279-Panawennage L.S.** 

