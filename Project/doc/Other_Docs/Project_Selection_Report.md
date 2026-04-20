# 🏭 CO326 Project Selection Report
## Industrial Digital Twin & Cyber-Physical Security

**Course:** CO326 — Computer Engineering Project  
**Date:** April 9, 2026  
**Timeline:** 1 Week (Full-Time Commitment)

---

## 📋 Table of Contents
1. [Project Selection Analysis](#1-project-selection-analysis)
2. [Recommended Project](#2-recommended-project)
3. [Why This Project Wins](#3-why-this-project-wins)
4. [Equipment & Components List](#4-equipment--components-list)
5. [Software Stack & Setup](#5-software-stack--setup)
6. [System Architecture](#6-system-architecture)
7. [Day-by-Day Implementation Timeline](#7-day-by-day-implementation-timeline)
8. [Detailed Implementation Steps](#8-detailed-implementation-steps)
9. [Deliverables Checklist](#9-deliverables-checklist)
10. [Risk Mitigation](#10-risk-mitigation)

---

## 1. Project Selection Analysis

### Selection Criteria (Weighted)

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Demonstrability** | 25% | How visually impressive and easy to demo live |
| **Understandability** | 20% | How deeply concepts can be understood and explained |
| **Perceived Difficulty** | 20% | How "hard" it looks to the lecturer |
| **1-Week Feasibility** | 25% | Realistic completion in 7 days full-time |
| **Component Availability** | 10% | Easy to source locally or online quickly |

### Top 5 Candidates Evaluated

| # | Project | Demo | Understand | Difficulty | Feasibility | Parts | **Total** |
|---|---------|------|------------|------------|-------------|-------|-----------|
| 17 | **HVAC Blower Fan Predictive Maintenance** | 9 | 9 | 8 | 9 | 9 | **8.85** |
| 7 | Water Pump Cavitation Detection | 8 | 8 | 8 | 7 | 7 | **7.65** |
| 27 | Industrial Air Compressor Health | 8 | 7 | 9 | 6 | 5 | **7.05** |
| 12 | Industrial Fan Blade Fouling Detection | 8 | 8 | 7 | 8 | 8 | **7.90** |
| 32 | Data Centre Cooling Fan Maintenance | 8 | 8 | 8 | 8 | 8 | **8.00** |

### Why Others Were Eliminated

- **Motor/Bearing projects (1, 3, etc.):** Require real industrial motors — expensive, heavy, hard to demo on a desk.
- **Conveyor/Elevator/Crane (2, 16, 21, 24):** Require building mechanical structures — too time-consuming for 1 week.
- **Generator/Transformer (6, 8, 20):** Involve high-voltage systems — safety risk, complex setup.
- **Process Industry (11-15):** Require specialized equipment (agitators, screw feeders) — not practical.
- **Railway/AGV (22, 23):** Simulated/scaled models take too long to construct.

---

## 2. Recommended Project

# 🌀 Project #17: HVAC Blower Fan Predictive Maintenance

> **"Monitor airflow degradation and bearing wear in an HVAC blower fan system using edge AI and a real-time Digital Twin."**

### Why This is THE Project

This project simulates a **real-world HVAC fan system** monitoring scenario using a simple **DC/brushless fan motor** as the physical plant. It is:

- ✅ **Visually impressive** — a spinning fan with real-time dashboards is immediately understandable
- ✅ **Deeply technical** — covers vibration analysis, current monitoring, TinyML, MQTT Sparkplug B, Digital Twin
- ✅ **Easy to explain** — everyone understands fans and why monitoring them matters
- ✅ **Compact setup** — fits on a desk, no heavy machinery needed
- ✅ **Quick to build** — components are simple and readily available
- ✅ **Looks like hard work** — full 4-layer IIoT architecture, ML pipeline, cybersecurity, Docker deployment

---

## 3. Why This Project Wins

### Demonstrability (9/10)
- **Live fan spinning** on the desk — physical system is immediately visible
- **Real-time Grafana dashboards** showing vibration, current, anomaly scores
- **Digital Twin** on screen synchronized with the physical fan
- **Bidirectional control** — turn the fan ON/OFF from the dashboard
- **Live anomaly detection** — attach weight to fan blade mid-demo to trigger vibration alert
- **"What-if" simulation** — show predicted behavior under increased load

### Understandability (9/10)
- Everyone understands what a fan does and why it might fail
- Clear mapping: physical fan → sensor data → edge processing → cloud dashboard
- Predictive maintenance concept is intuitive: "fan is degrading, replace in X hours"
- MQTT topic tree maps directly to a factory namespace

### Perceived Difficulty (8/10)
- Full 4-layer IIoT architecture with edge-to-cloud pipeline
- TinyML anomaly detection running on ESP32-S3
- MQTT Sparkplug B protocol implementation
- Docker containerized cloud infrastructure
- Cybersecurity (TLS, authentication, LWT)
- RUL estimation with linear regression
- Professional Grafana SCADA dashboards

### 1-Week Feasibility (9/10)
- Fan + sensors can be wired in a few hours
- Docker setup is streamlined (all containers provided)
- Node-RED flows can be built visually
- TinyML can use simple K-Means clustering
- No mechanical construction needed

---

## 4. Equipment & Components List

### 🔧 Hardware Components

| # | Component | Quantity | Purpose | Estimated Cost (LKR) |
|---|-----------|----------|---------|---------------------|
| 1 | **ESP32-S3 DevKit** (e.g., ESP32-S3-WROOM-1) | 1 | Main edge MCU — data acquisition, TinyML inference | 3,000 - 4,500 |
| 2 | **12V DC Brushless Fan** (e.g., 80mm or 120mm PC fan) | 1 | Physical plant — the "HVAC blower fan" | 500 - 1,500 |
| 3 | **ADXL345 / MPU6050 Accelerometer** (3-axis, I2C) | 1 | Vibration sensing — mounted on fan housing | 400 - 800 |
| 4 | **ACS712 Current Sensor Module** (5A or 20A) | 1 | Current signature analysis — measures fan motor current | 300 - 600 |
| 5 | **5V Relay Module** (1-channel) | 1 | Actuator — bidirectional control (on/off fan from dashboard) | 150 - 300 |
| 6 | **12V DC Power Supply** (1A-2A) | 1 | Power the fan motor | 400 - 800 |
| 7 | **Breadboard + Jumper Wires** | 1 set | Prototyping connections | 300 - 500 |
| 8 | **USB-C Cable** | 1 | Programming and powering ESP32-S3 | 200 - 400 |
| 9 | **Small weight/tape** (for demo) | — | Attach to fan blade to simulate imbalance fault | Free |
| 10 | **Small enclosure/mounting base** (optional) | 1 | Clean demo presentation | 200 - 500 |

> **Total Estimated Hardware Cost: LKR 5,450 - 9,900 (~USD 17 - 30)**

### 💻 Required PC/Laptop Specifications
- Windows/Linux/macOS with at least 8GB RAM
- Docker Desktop installed
- Wi-Fi connectivity (same network as ESP32)
- USB port for ESP32 programming

---

## 5. Software Stack & Setup

### Mandatory Software (as per project spec)

| Layer | Software | Deployment | Purpose |
|-------|----------|------------|---------|
| **Edge** | Arduino IDE / PlatformIO | Local install | ESP32-S3 firmware development |
| **Edge ML** | TensorFlow Lite Micro / Custom K-Means | Compiled on ESP32 | TinyML anomaly detection |
| **Broker** | Eclipse Mosquitto | Docker container | MQTT message broker with TLS |
| **Middleware** | Node-RED | Docker container | Data flow orchestration, RUL logic |
| **Historian** | InfluxDB | Docker container | Time-series data storage |
| **Visualization** | Grafana | Docker container | SCADA dashboards, Digital Twin UI |

### Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  mosquitto:
    image: eclipse-mosquitto:2
    ports:
      - "1883:1883"
      - "8883:8883"
    volumes:
      - ./mosquitto/config:/mosquitto/config
      - ./mosquitto/data:/mosquitto/data

  nodered:
    image: nodered/node-red:latest
    ports:
      - "1880:1880"
    volumes:
      - ./nodered/data:/data

  influxdb:
    image: influxdb:2
    ports:
      - "8086:8086"
    volumes:
      - ./influxdb/data:/var/lib/influxdb2

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/data:/var/lib/grafana
```

---

## 6. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SYSTEM ARCHITECTURE OVERVIEW                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────┐                           │
│  │     LAYER 1: PERCEPTION (EDGE)       │                           │
│  │  ┌─────────┐  ┌──────────┐          │                           │
│  │  │ MPU6050  │  │ ACS712   │          │                           │
│  │  │Vibration │  │ Current  │          │                           │
│  │  └────┬─────┘  └────┬─────┘          │                           │
│  │       │              │                │                           │
│  │  ┌────▼──────────────▼─────────┐     │                           │
│  │  │       ESP32-S3              │     │                           │
│  │  │  • Sampling & Filtering     │     │                           │
│  │  │  • Feature Extraction       │     │                           │
│  │  │  • TinyML Anomaly Detection │     │                           │
│  │  │  • Local Buffering          │     │                           │
│  │  └────────────┬────────────────┘     │                           │
│  └───────────────┼──────────────────────┘                           │
│                  │ MQTT (Sparkplug B)                                │
│                  │ TLS Encrypted                                     │
│  ┌───────────────▼──────────────────────┐                           │
│  │     LAYER 2: TRANSPORT               │                           │
│  │  ┌────────────────────────┐          │                           │
│  │  │   Mosquitto Broker     │          │                           │
│  │  │  • TLS Authentication  │          │                           │
│  │  │  • Last Will (LWT)     │          │                           │
│  │  │  • Topic-based routing │          │                           │
│  │  └────────────┬───────────┘          │                           │
│  └───────────────┼──────────────────────┘                           │
│                  │                                                    │
│  ┌───────────────▼──────────────────────┐                           │
│  │     LAYER 3: EDGE LOGIC              │                           │
│  │  ┌────────────────────────┐          │                           │
│  │  │      Node-RED          │          │                           │
│  │  │  • Data Normalization  │          │                           │
│  │  │  • State Modeling      │          │                           │
│  │  │  • RUL Estimation      │          │                           │
│  │  │  • Rule-based Alerts   │          │                           │
│  │  │  • Bidirectional Ctrl  │          │                           │
│  │  └────────────┬───────────┘          │                           │
│  └───────────────┼──────────────────────┘                           │
│                  │                                                    │
│  ┌───────────────▼──────────────────────┐                           │
│  │     LAYER 4: APPLICATION             │                           │
│  │  ┌──────────┐  ┌──────────────┐      │                           │
│  │  │ InfluxDB │  │   Grafana    │      │                           │
│  │  │Historian │  │ SCADA / Twin │      │                           │
│  │  └──────────┘  └──────────────┘      │                           │
│  └──────────────────────────────────────┘                           │
│                                                                      │
│  ┌──────────────────────────────────────┐                           │
│  │     PHYSICAL PLANT                    │                           │
│  │  ┌──────────┐  ┌──────────────┐      │                           │
│  │  │ 12V DC   │◄─│  5V Relay    │◄─── Bidirectional Control       │
│  │  │ Fan Motor │  │  Module      │      │                           │
│  │  └──────────┘  └──────────────┘      │                           │
│  └──────────────────────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────┘
```

### MQTT Topic Tree (Unified Namespace)

```
spBv1.0/buildingA/
├── NBIRTH/area1/hvac_fan01          # Node birth certificate
├── NDEATH/area1/hvac_fan01          # Node death (LWT)
├── NDATA/area1/hvac_fan01           # Node data
│   ├── vibration_rms                # g (m/s²)
│   ├── vibration_x                  # Raw X-axis
│   ├── vibration_y                  # Raw Y-axis
│   ├── vibration_z                  # Raw Z-axis
│   ├── current_rms                  # Amps
│   ├── anomaly_score                # 0.0 - 1.0
│   ├── anomaly_label                # normal / warning / critical
│   ├── temperature                  # °C (optional)
│   ├── fan_state                    # ON / OFF
│   └── uptime_ms                    # Milliseconds
├── NCMD/area1/hvac_fan01            # Commands TO device
│   ├── relay_control                # ON / OFF
│   └── set_sampling_rate            # Hz
└── analytics/
    ├── rul_estimate                  # Hours remaining
    ├── rul_confidence                # 0.0 - 1.0
    └── health_index                  # 0 - 100%
```

---

## 7. Day-by-Day Implementation Timeline

> **Total Duration: 7 Days (Full-Time, ~10-12 hours/day)**  
> **Assuming team of 3-4 members working in parallel**

---

### 📅 Day 1 (April 9): Architecture & Infrastructure Setup

| Time Block | Task | Owner | Deliverable |
|------------|------|-------|-------------|
| Morning (3h) | Install Docker Desktop, pull all container images | All | Working Docker environment |
| Morning (3h) | Write `docker-compose.yml`, configure Mosquitto (TLS, auth) | Member A | Running broker with TLS |
| Afternoon (3h) | Set up InfluxDB (org, bucket, API token) | Member B | Configured InfluxDB |
| Afternoon (3h) | Install Grafana, connect to InfluxDB datasource | Member C | Grafana connected to InfluxDB |
| Evening (3h) | Define MQTT topic tree (UNS), document architecture | Member D | Architecture doc + topic tree |
| Evening (2h) | Install Arduino IDE / PlatformIO, test ESP32-S3 blink | All | ESP32-S3 verified working |

**Day 1 Completion: ✅ Full cloud infrastructure running, ESP32 verified**

---

### 📅 Day 2 (April 10): Sensor Integration & Data Acquisition

| Time Block | Task | Owner | Deliverable |
|------------|------|-------|-------------|
| Morning (3h) | Wire MPU6050 accelerometer to ESP32-S3 (I2C) | Member A+B | Raw vibration data reading |
| Morning (3h) | Wire ACS712 current sensor to ESP32-S3 (ADC) | Member C | Raw current data reading |
| Afternoon (3h) | Wire relay module + fan motor circuit | Member B | Fan controllable via GPIO |
| Afternoon (3h) | Implement sensor sampling loop (100Hz vibration, 10Hz current) | Member A | Structured sampling code |
| Evening (3h) | Implement feature extraction (RMS, peak-to-peak, dominant freq) | Member A+C | Feature vector output |
| Evening (2h) | Test all sensor readings, calibrate values | All | Verified sensor data |

**Day 2 Completion: ✅ All sensors reading, fan controllable, features computed**

---

### 📅 Day 3 (April 11): MQTT & Edge-to-Cloud Communication

| Time Block | Task | Owner | Deliverable |
|------------|------|-------|-------------|
| Morning (3h) | Implement MQTT client on ESP32 (WiFi + MQTT connect) | Member A | ESP32 connected to Mosquitto |
| Morning (3h) | Implement Sparkplug B payload encoding (birth/data/death) | Member A | Sparkplug B compliant messages |
| Afternoon (3h) | Add TLS to MQTT connection (self-signed certs) | Member B | Encrypted MQTT communication |
| Afternoon (3h) | Implement Last Will & Testament (LWT) | Member A | Device death detection |
| Afternoon (3h) | Build Node-RED flows: MQTT → Parse → InfluxDB write | Member C | Data flowing to InfluxDB |
| Evening (3h) | Implement local buffering on ESP32 (circular buffer for outages) | Member A | Offline data retention |
| Evening (2h) | Test full pipeline: sensor → MQTT → Node-RED → InfluxDB | All | End-to-end data flow verified |

**Day 3 Completion: ✅ Full secure data pipeline working end-to-end**

---

### 📅 Day 4 (April 12): TinyML Edge Anomaly Detection

| Time Block | Task | Owner | Deliverable |
|------------|------|-------|-------------|
| Morning (3h) | Collect normal operation data (fan running smoothly for 30 min) | Member B | Training dataset |
| Morning (3h) | Implement K-Means clustering on PC (Python, 2 clusters) | Member C | Trained K-Means model |
| Afternoon (3h) | Port K-Means to ESP32-S3 (hardcoded centroids, distance calc) | Member A | TinyML model running |
| Afternoon (3h) | Implement anomaly scoring (distance from normal centroid) | Member A | Anomaly score 0.0-1.0 |
| Evening (3h) | Test with artificial faults (tape weight to fan blade) | All | Anomaly detection working |
| Evening (2h) | Publish anomaly score and label via MQTT | Member A | Anomaly data in pipeline |

**Day 4 Completion: ✅ Edge AI detecting anomalies, publishing scores via MQTT**

---

### 📅 Day 5 (April 13): Digital Twin & Grafana Dashboards

| Time Block | Task | Owner | Deliverable |
|------------|------|-------|-------------|
| Morning (3h) | Design Grafana SCADA dashboard layout | Member C | Dashboard wireframe |
| Morning (3h) | Build real-time panels: vibration gauge, current graph, anomaly meter | Member C | Live visualization |
| Afternoon (3h) | Implement bidirectional control: Grafana button → Node-RED → MQTT → ESP32 relay | Member B+C | Fan ON/OFF from dashboard |
| Afternoon (3h) | Build Digital Twin panel: fan animation synced with real fan state | Member C | Visual Digital Twin |
| Evening (3h) | Implement "What-If" simulation in Node-RED (simulated load increase) | Member B | Simulation mode working |
| Evening (2h) | Add state consistency check (Twin vs Physical mismatch alert) | Member B | Mismatch detection |

**Day 5 Completion: ✅ Full Digital Twin with bidirectional control and simulation**

---

### 📅 Day 6 (April 14): RUL, Cloud Analytics & Security Hardening

| Time Block | Task | Owner | Deliverable |
|------------|------|-------|-------------|
| Morning (3h) | Implement RUL estimation in Node-RED (linear regression on vibration trend) | Member B | RUL prediction working |
| Morning (3h) | Add RUL + confidence + health index to Grafana dashboard | Member C | RUL visualization |
| Afternoon (3h) | Harden security: credential-based auth, encrypted config storage | Member A | Security requirements met |
| Afternoon (3h) | Implement automatic reconnection logic on ESP32 | Member A | Reliability features done |
| Evening (3h) | Create alarm system: email/visual alerts on critical anomaly | Member C | Alert system working |
| Evening (2h) | Full system integration test — all layers working together | All | Integrated system verified |

**Day 6 Completion: ✅ Complete system with RUL, security, and reliability**

---

### 📅 Day 7 (April 15): Documentation, Testing & Demo Preparation

| Time Block | Task | Owner | Deliverable |
|------------|------|-------|-------------|
| Morning (3h) | Write System Architecture Diagram (draw.io / Lucidchart) | Member D | Architecture diagram |
| Morning (3h) | Write Electrical Wiring Diagram + P&ID | Member B | Wiring documentation |
| Afternoon (3h) | Document MQTT Topic Tree, Node-RED Flow Export, ML Model Description | Member A+C | Technical docs |
| Afternoon (3h) | Write Cybersecurity Design Summary | Member A | Security documentation |
| Evening (2h) | Prepare demo script: what to show, what to break (fault injection) | All | Demo plan |
| Evening (2h) | Full dress rehearsal — run entire demo end-to-end | All | Demo ready |
| Evening (1h) | Clean up code, add comments, final commit | All | Clean codebase |

**Day 7 Completion: ✅ All documentation complete, demo rehearsed, ready to present**

---

## 8. Detailed Implementation Steps

### 8.1 ESP32-S3 Firmware Structure

```
firmware/
├── src/
│   ├── main.cpp                # Main loop: sample → extract → infer → publish
│   ├── sensors/
│   │   ├── vibration.h/cpp     # MPU6050 I2C driver + RMS calculation
│   │   └── current.h/cpp       # ACS712 ADC reading + RMS calculation
│   ├── ml/
│   │   ├── kmeans.h/cpp        # K-Means inference (hardcoded centroids)
│   │   └── features.h/cpp      # Feature extraction (RMS, peak, freq)
│   ├── comms/
│   │   ├── mqtt_client.h/cpp   # MQTT + Sparkplug B + TLS
│   │   ├── wifi_manager.h/cpp  # WiFi connection + reconnection
│   │   └── buffer.h/cpp        # Circular buffer for offline storage
│   └── control/
│       └── relay.h/cpp         # Relay control via MQTT commands
├── certs/
│   ├── ca.crt                  # CA certificate
│   └── client.crt              # Client certificate
└── platformio.ini
```

### 8.2 Node-RED Flow Overview

```
Flow 1: Data Ingestion
  MQTT In → Sparkplug B Decode → Data Validation → InfluxDB Write

Flow 2: RUL Estimation
  InfluxDB Query (last 1hr vibration) → Linear Regression → RUL Publish → InfluxDB Write

Flow 3: Bidirectional Control
  Grafana HTTP → Validate Command → MQTT Publish (NCMD) → Confirm State

Flow 4: Simulation / What-If
  Manual Trigger → Generate Synthetic Data → Run Through ML → Display Prediction

Flow 5: Alerting
  Anomaly Score Subscribe → Threshold Check → Alert Dashboard + Log
```

### 8.3 TinyML: K-Means Anomaly Detection

**Algorithm Summary:**
1. **Training (on PC, Python):** Collect ~1000 samples of normal operation. Compute K-Means with K=2 clusters.
2. **Deployment (on ESP32):** Hardcode the 2 centroid vectors into firmware.
3. **Inference Loop:**
   - Extract feature vector: `[vib_rms, vib_peak, current_rms, current_std]`
   - Compute Euclidean distance to each centroid
   - Anomaly score = distance to "normal" centroid / max expected distance
   - If score > threshold → classify as anomaly
4. **Latency target:** < 50ms per inference

### 8.4 RUL Estimation (Node-RED)

**Method:** Simple Linear Regression on vibration RMS trend
1. Query last N hours of vibration RMS from InfluxDB
2. Fit linear regression: `vib_rms = m * time + b`
3. Extrapolate to failure threshold (e.g., vib_rms = 3.0g)
4. RUL = (threshold - current) / slope
5. Confidence = R² value of the regression

---

## 9. Deliverables Checklist

| # | Deliverable | Required By | Status |
|---|-------------|-------------|--------|
| 1 | Fully working IIoT system (4 layers) | Day 6 | ☐ |
| 2 | Live Digital Twin demonstration | Day 5 | ☐ |
| 3 | ML-based fault detection (TinyML on ESP32) | Day 4 | ☐ |
| 4 | Bidirectional control (dashboard → relay) | Day 5 | ☐ |
| 5 | MQTT Sparkplug B with UNS | Day 3 | ☐ |
| 6 | TLS encrypted communication | Day 3 | ☐ |
| 7 | Local buffering during outages | Day 3 | ☐ |
| 8 | RUL estimation with confidence | Day 6 | ☐ |
| 9 | System Architecture Diagram | Day 7 | ☐ |
| 10 | Electrical Wiring Diagram | Day 7 | ☐ |
| 11 | P&ID (simplified) | Day 7 | ☐ |
| 12 | MQTT Topic Tree documentation | Day 7 | ☐ |
| 13 | Node-RED Flow Export | Day 7 | ☐ |
| 14 | ML Model Description | Day 7 | ☐ |
| 15 | Cybersecurity Design Summary | Day 7 | ☐ |
| 16 | Final technical presentation | Day 7 | ☐ |

---

## 10. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| ESP32-S3 not available locally | 🔴 High | Order immediately; use ESP32 (non-S3) as fallback — TinyML still works |
| MPU6050 noisy readings | 🟡 Medium | Apply moving average filter + calibration offset |
| Sparkplug B complex to implement | 🟡 Medium | Use simplified Sparkplug B (protobuf optional, use JSON with proper topic structure) |
| TLS setup on ESP32 difficult | 🟡 Medium | Start without TLS, add last; use self-signed certs with `WiFiClientSecure` |
| RUL estimation inaccurate | 🟢 Low | Not graded on accuracy — focus on demonstrating the concept with real trend data |
| Docker resource issues on laptop | 🟡 Medium | Allocate min 4GB RAM to Docker; close unnecessary applications |
| Fan motor too quiet for vibration | 🟡 Medium | Mount accelerometer directly on motor housing; use tape/weight for induced fault |

---

## 🎯 Demo Day Strategy

### What to Show (5-Minute Demo Flow)

1. **Start system** — Show Docker containers running (30s)
2. **Show live Grafana dashboard** — vibration, current, health gauges (60s)
3. **Explain architecture** — Point to architecture diagram, explain 4 layers (60s)
4. **Demonstrate bidirectional control** — Click button on Grafana → fan turns ON/OFF (30s)
5. **Inject fault** — Attach tape/weight to fan blade → show anomaly score spike live (60s)
6. **Show RUL prediction** — Point to estimated remaining life decreasing (30s)
7. **Show security** — Demonstrate TLS in packet capture, show LWT death message by unplugging ESP32 (30s)
8. **Show simulation** — Run "What-If" scenario with increased load (30s)

### What Will Impress the Lecturer

- ✨ **Live fault injection** during demo — nothing beats real-time anomaly detection
- ✨ **Professional Grafana dashboards** that look like real SCADA systems
- ✨ **Sparkplug B topic tree** showing industrial-grade UNS design
- ✨ **Edge AI** running on a microcontroller (not cloud — this is the hard part)
- ✨ **Bidirectional control** proving it's a true Digital Twin, not just a Digital Shadow
- ✨ **Security features** (TLS, auth, LWT) showing production-readiness

---

> **🚀 Start today. You have 7 days. This is achievable, impressive, and will demonstrate deep understanding of Industrial IoT systems.**
