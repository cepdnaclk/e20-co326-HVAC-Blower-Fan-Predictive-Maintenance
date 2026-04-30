# 🏭 HVAC Blower Fan — Stage 2: Live Inference & IIoT Dashboard

> **CO326 — Computer Systems Engineering Project**  
> Real-time predictive maintenance system using Edge ML + Docker IIoT stack

---

## 📋 Table of Contents

1. [What This Does](#what-this-does)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Hardware Wiring](#hardware-wiring)
5. [Step 1 — Start Docker Stack](#step-1--start-docker-stack)
6. [Step 2 — Configure & Flash ESP32](#step-2--configure--flash-esp32)
7. [Step 3 — Install Node-RED Packages](#step-3--install-node-red-packages)
8. [Step 4 — Verify Data Flow](#step-4--verify-data-flow)
9. [Step 5 — Open Grafana Dashboard](#step-5--open-grafana-dashboard)
10. [Step 6 — Test Fault Injection](#step-6--test-fault-injection)
11. [Step 7 — Test Relay Control](#step-7--test-relay-control)
12. [Troubleshooting](#troubleshooting)
13. [File Structure](#file-structure)

---

## What This Does

The ESP32 reads vibration (MPU6050) and current (ACS712) at **100Hz**, extracts 12 features from a sliding window (2.56 seconds), runs a **K-Means anomaly detection model** on-device, and publishes the results every ~2.56 seconds over **MQTT** (WiFi) to a **Docker container stack** on your PC:

```
┌────────────────────┐      WiFi/MQTT       ┌─────────────────────────────────┐
│     ESP32          │ ──────────────────►   │  Docker Stack (Your PC)        │
│  ┌──────────────┐  │   JSON every 2.56s   │                                │
│  │ MPU6050      │  │                      │  Mosquitto → Node-RED →        │
│  │ ACS712       │  │  ◄─────────────────  │  InfluxDB → Grafana            │
│  │ K-Means ML   │  │   Relay ON/OFF cmd   │                                │
│  │ Relay Control│  │                      │  🖥 Live Dashboard at :3000    │
│  └──────────────┘  │                      └─────────────────────────────────┘
└────────────────────┘
```

**What gets published (JSON):**
```json
{
  "device": "hvac_fan01",
  "vib_rms": 9.74, "vib_peak": 9.92, "vib_crest": 1.02, "vib_kurt": -0.81,
  "cur_rms": 3.93, "cur_std": 0.04,
  "dom_freq": 35.0, "spec_rms": 1.10, "spec_cent": 27.9,
  "band1": 11.1, "band2": 13.0, "band3": 50.2,
  "anomaly_score": 0.0017, "anomaly_label": 0,
  "relay": true, "rssi": -45
}
```

---

## Architecture Overview

```
                    ┌─────────────────────┐
                    │      GRAFANA        │  ← You view this (port 3000)
                    │  Live Dashboard     │
                    │  Gauges + Charts    │
                    └────────┬────────────┘
                             │ Flux Queries
                    ┌────────▼────────────┐
                    │     InfluxDB 2.7    │  ← Time-series database (port 8086)
                    │   Bucket: hvac_data │
                    └────────┬────────────┘
                             │ Write API
                    ┌────────▼────────────┐
                    │     Node-RED        │  ← Data pipeline + alerts (port 1880)
                    │  Parse → Store      │
                    │  Alert → Control    │
                    └────────┬────────────┘
                             │ MQTT Subscribe
                    ┌────────▼────────────┐
                    │    Mosquitto MQTT   │  ← Message broker (port 1883)
                    │   Topic Router      │
                    └────────┬────────────┘
                             │ WiFi
                    ┌────────▼────────────┐
                    │   ESP32 WROOM-32    │  ← Edge device
                    │  Sensors + K-Means  │
                    │  + Relay Control    │
                    └─────────────────────┘
```

---

## Prerequisites

### Software
| Tool | Version | Install |
|------|---------|---------|
| **Docker Desktop** | Latest | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |
| **Arduino IDE** | 2.x | [arduino.cc/en/software](https://www.arduino.cc/en/software) |
| **ESP32 Board Package** | 3.x | In Arduino IDE: Tools → Board Manager → Search "esp32" |

### Arduino Libraries (Install via Library Manager)
| Library | Author |
|---------|--------|
| Adafruit MPU6050 | Adafruit |
| Adafruit Unified Sensor | Adafruit |
| PubSubClient | Nick O'Leary |
| ArduinoJson | Benoit Blanchon |

### Hardware
| Component | Purpose |
|-----------|---------|
| ESP32 DevKit v1 (WROOM-32) | Edge processor |
| MPU6050 / GY-521 | Vibration sensor |
| ACS712-5A | Current sensor |
| YC3F DC5V SHC Relay (5-pin) | Fan auto-shutdown *(optional)* |
| BC547 / 2N2222 NPN Transistor | Relay driver (ESP32 can't drive relay coil directly) |
| 1N4007 Diode | Flyback protection for relay coil |
| 1KΩ Resistor | Transistor base resistor |
| 12V DC Blower Fan | The fan being monitored |
| 12V Power Supply | Fan power |
| Breadboard + Jumper Wires | Connections |

---

## Hardware Wiring

### Same as Stage 1 (MPU6050 + ACS712):
```
ESP32 Pin       Sensor Pin       Notes
─────────       ──────────       ─────
3V3         →   MPU6050 VCC      Power
GND         →   MPU6050 GND      Ground
GPIO 21     →   MPU6050 SDA      I2C Data
GPIO 22     →   MPU6050 SCL      I2C Clock
GPIO 34     →   ACS712 OUT       ADC (current reading)
5V (VIN)    →   ACS712 VCC       Power ACS712
GND         →   ACS712 GND       Ground
```

### ⚡ NEW for Stage 2: YC3F DC5V SHC Relay (5-pin)

**Step 1: Identify the relay pins**

Look at the **BOTTOM** of the relay. There is a small **dot** on one corner.
Hold the relay so the dot is in the **top-left** corner:

```
    BOTTOM VIEW (pins facing you, dot in top-left)
    ═══════════════════════════════════════════

     [DOT]
     Pin 1 (Coil +)                    Pin 5 (NO — Normally Open)

     Pin 2 (Coil -)                    Pin 4 (NC — Normally Closed)

                                        Pin 3 (COM — Common)

    ───────────────────────────────────────────
    LEFT SIDE = 2 Coil Pins        RIGHT SIDE = 3 Contact Pins
```

| Pin | Name | What it does |
|-----|------|-------------|
| Pin 1 (near dot) | **Coil +** | Powers the electromagnet (5V) |
| Pin 2 | **Coil -** | Ground for electromagnet |
| Pin 3 | **COM** | Common contact (fan power goes here) |
| Pin 4 | **NC** | Normally Closed — connected to COM when relay is OFF |
| Pin 5 | **NO** | Normally Open — connected to COM when relay is ON ✅ |

**Step 2: Build the driver circuit**

The ESP32 GPIO outputs only **12mA**, but the relay coil needs **~70mA**.
We use a **BC547 NPN transistor** as a switch to boost the current:

```
                      1N4007 Diode (stripe towards +5V)
                    ┌──────◄──────┐
                    │              │
    ESP32 5V (VIN) ─┤              ├─── Relay Pin 1 (Coil +, near dot)
                    │              │
                    └──────────────┘
                                   │
                         Relay Pin 2 (Coil -)
                                   │
                              ┌────┘
                              │  Collector
                           ┌──┴──┐
                           │BC547│  (flat side facing you)
                           └──┬──┘
                              │  Emitter
                              │
                           ESP32 GND
                              
    ESP32 GPIO 26 ───[1KΩ]─── Base (middle pin of BC547)
```

**Step 3: Connect the wiring on breadboard**

```
Relay Driver Circuit:
─────────────────────
ESP32 GPIO 26  ──► 1KΩ Resistor ──► BC547 Base (middle pin)
ESP32 GND      ──► BC547 Emitter (right pin, flat side facing you)
ESP32 5V (VIN) ──► Relay Pin 1 (Coil +, near dot)
BC547 Collector (left pin) ──► Relay Pin 2 (Coil -)
1N4007 Diode: Stripe end to Pin 1, other end to Pin 2
              (bridges across the coil pins for protection)

Fan Power Circuit:
──────────────────
12V Supply (+)  ──► ACS712 [IP+]
ACS712 [IP-]    ──► Relay Pin 3 (COM — middle of the 3 contact pins)
Relay Pin 5 (NO — farthest from dot) ──► Fan (+)
Fan (-)         ──► 12V Supply (-)

How it works:
  GPIO 26 HIGH → Transistor ON → Coil energized → COM connects to NO → Fan runs
  GPIO 26 LOW  → Transistor OFF → Coil off → COM disconnects from NO → Fan stops
```

### Full Wiring Diagram:
```
┌──────────────────────────────────────────────────────┐
│  12V Power Supply                                     │
│  (+) ──► ACS712 [IP+]                                │
│          ACS712 [IP-] ──► Relay Pin 3 (COM)          │
│                                                       │
│          Relay Pin 5 (NO) ──────► Fan (+)             │
│  (-) ◄──────────────────────── Fan (-)               │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│  ESP32 WROOM-32                                       │
│                                                       │
│  3V3  ────► MPU6050 VCC                               │
│  GND  ────► MPU6050 GND                               │
│  D21  ────► MPU6050 SDA                               │
│  D22  ────► MPU6050 SCL                               │
│                                                       │
│  VIN  ────► ACS712 VCC                                │
│  GND  ────► ACS712 GND                                │
│  D34  ◄──── ACS712 OUT                                │
│                                                       │
│  VIN  ────► Relay Pin 1 (Coil +, near dot)           │
│  GND  ────► BC547 Emitter                             │
│  D26  ──[1KΩ]──► BC547 Base                          │
│             BC547 Collector ──► Relay Pin 2 (Coil -)  │
│             1N4007 Diode across Relay Pin 1 ↔ Pin 2   │
│             (stripe towards Pin 1)                    │
│                                                       │
│  USB ────► PC (for flashing)                          │
└──────────────────────────────────────────────────────┘
```

> **⚠️ BC547 Pin Identification:** Hold the transistor with the **flat side facing you** and pins pointing down. Left = Collector, Middle = Base, Right = Emitter.

> **⚠️ 1N4007 Diode Direction:** The diode has a **silver/white stripe** on one end. The stripe end connects to Relay Pin 1 (the +5V side). This diode protects the transistor from voltage spikes when the relay coil switches off.

> **Note:** If you don't have a relay, transistor, or diode — the system still works perfectly! You just won't have the physical fan auto-shutdown feature. Skip the relay wiring and everything else remains the same.

---

## Step 1 — Start Docker Stack

### 1.1 Make sure Docker Desktop is running
Open Docker Desktop and wait until the engine is ready (green icon in system tray).

### 1.2 Start all containers
Open a terminal in this `stage2-running` folder and run:

```powershell
cd D:\Sem7\CO326-Project\stage2-running
docker compose up -d
```

### 1.3 Verify all containers are running
```powershell
docker compose ps
```

You should see:
```
NAME         IMAGE                          STATUS
mosquitto    eclipse-mosquitto:2            Up
nodered      nodered/node-red:latest        Up
influxdb     influxdb:2.7                   Up
grafana      grafana/grafana-oss:10.2.0     Up
```

### 1.4 Wait 30 seconds for all services to initialize

| Service | URL | Login |
|---------|-----|-------|
| **Node-RED** | http://localhost:1880 | No login needed |
| **InfluxDB** | http://localhost:8086 | admin / hvac_admin_2026 |
| **Grafana** | http://localhost:3000 | admin / hvac_grafana_2026 |

> **If containers fail to start**, see [Troubleshooting](#troubleshooting) section.

---

## Step 2 — Configure & Flash ESP32

### 2.1 Find your PC's IP address
The ESP32 needs to know your PC's IP to send MQTT data. Run:

```powershell
ipconfig
```

Look for your **WiFi adapter** and note the `IPv4 Address` (e.g., `192.168.1.100`).

### 2.2 Edit the firmware configuration
Open `firmware/inference_firmware/inference_firmware.ino` in Arduino IDE and edit these 3 lines at the top:

```cpp
#define WIFI_SSID       "YourWiFiName"        // ← Your WiFi network name
#define WIFI_PASS       "YourWiFiPassword"     // ← Your WiFi password
#define MQTT_BROKER     "192.168.1.100"        // ← Your PC's IP address
```

### 2.3 Select the correct board
In Arduino IDE:
- **Tools → Board → esp32 → ESP32 Dev Module**
- **Tools → Port → COM? (your ESP32 port)**

### 2.4 Upload the firmware
Click the **Upload** button (→ arrow). Wait for:
```
[WiFi] Connecting to YourWiFiName... Connected!
[WiFi] IP: 192.168.1.xxx
[MQTT] Connecting to 192.168.1.100... Connected!
[RUN] Inference engine started!
```

### 2.5 Verify on Serial Monitor
Open **Tools → Serial Monitor** (115200 baud). You should see:
```
[INF #1] Score=0.0017 Label=NORMAL Dist=1.44 Cluster=0 Feat=45231us Total=45312us
[INF #2] Score=0.0015 Label=NORMAL Dist=1.27 Cluster=1 Feat=44891us Total=44973us
```
These print every ~2.56 seconds — one per sliding window inference.

---

## Step 3 — Install Node-RED Packages

### 3.1 Open Node-RED
Go to **http://localhost:1880** in your browser.

### 3.2 Install the InfluxDB node
1. Click the **☰ Menu** (top-right hamburger icon)
2. Click **Manage palette**
3. Click the **Install** tab
4. Search for: `node-red-contrib-influxdb`
5. Click **Install** → Confirm

### 3.3 Configure the InfluxDB connection
After installing the package, the flows should auto-load. But you need to configure the InfluxDB connection:

1. Double-click the **"💾 Write to InfluxDB"** node
2. Click the **pencil icon** next to the Server field to edit
3. Set:
   - **Version**: 2.0
   - **URL**: `http://influxdb:8086`
   - **Token**: `my-super-secret-influx-token-change-me`
   - **Organisation**: `hvac_lab`
   - **Bucket**: `hvac_data`
4. Click **Update** → **Done**

### 3.4 Configure the MQTT connection
1. Double-click any **MQTT** node (e.g., "📡 MQTT: hvac/fan01/data")
2. Click the **pencil icon** next to Server
3. Set:
   - **Server**: `mosquitto`
   - **Port**: `1883`
4. Click **Update** → **Done**

### 3.5 Deploy
Click the red **Deploy** button (top-right). All flows should now show "connected" status.

---

## Step 4 — Verify Data Flow

### 4.1 Check MQTT messages are arriving
In Node-RED, look at the **Debug** sidebar (🐛 bug icon). You should see JSON payloads appearing every ~2.56 seconds.

### 4.2 Check InfluxDB is receiving data
1. Go to **http://localhost:8086**
2. Login: `admin` / `hvac_admin_2026`
3. Click **Data Explorer** (left sidebar)
4. Select bucket: `hvac_data`
5. Select measurement: `hvac_sensor`
6. Select a field (e.g., `anomaly_score`)
7. Click **Submit** — you should see data points appearing

### 4.3 Alternative: Test from terminal
```powershell
# Subscribe to MQTT to see raw ESP32 messages:
docker exec mosquitto mosquitto_sub -t "hvac/fan01/data" -C 3
```
This will print 3 messages and exit.

---

## Step 5 — Open Grafana Dashboard

### 5.1 Login to Grafana
1. Go to **http://localhost:3000**
2. Login: `admin` / `hvac_grafana_2026`

### 5.2 Open the dashboard
The **HVAC Fan — Predictive Maintenance Dashboard** should be the home dashboard. If not:
1. Click **☰** → **Dashboards**
2. Click **HVAC Fan — Predictive Maintenance Dashboard**

### 5.3 What you should see
| Panel | What it shows |
|-------|---------------|
| 🔴 **Anomaly Score** gauge | Current anomaly score (0–1), green/yellow/red zones |
| 📊 **Vibration RMS** gauge | Current vibration magnitude in m/s² |
| ⚡ **Fan Health Status** | Text: ✅ NORMAL / ⚠️ WARNING / 🚨 CRITICAL |
| 🔌 **Relay / Fan Power** | Text: 🟢 FAN ON / 🔴 FAN OFF |
| 📈 **Anomaly Time Series** | 30-min chart with threshold lines |
| 📈 **Vibration Time Series** | 30-min chart of vib_rms |
| ⚡ **Current Time Series** | 30-min chart of cur_rms |
| 🎵 **Spectral Band Power** | Stacked area of band1/band2/band3 |

The dashboard auto-refreshes every **5 seconds**.

> **If panels show "No Data"**, make sure the InfluxDB datasource is configured. Go to **⚙ Settings → Data Sources → InfluxDB** and verify the token matches the `.env` file.

---

## Step 6 — Test Fault Injection

This is the most exciting part — proving the AI works!

### 6.1 Baseline: Normal operation
Watch the dashboard for 1 minute with the fan running normally. You should see:
- Anomaly Score: **~0.0015** (deep green)
- Health Status: **✅ NORMAL**

### 6.2 Warning: Attach 10g weight to fan blade
Use tape to stick a small weight (coin, bolt, etc.) to one blade:
- Anomaly Score should jump to **~0.003–0.005** (yellow zone)
- Health Status changes to: **⚠️ WARNING**
- Node-RED debug shows alert message

### 6.3 Critical: Attach 25g weight
Add more weight:
- Anomaly Score jumps to **>0.05** (red zone)
- Health Status: **🚨 CRITICAL**
- **If relay is connected**: Fan automatically shuts down!
- Node-RED shows critical alert

### 6.4 Recovery
Remove the weights:
- Score returns to ~0.0015
- Status returns to NORMAL

---

## Step 7 — Test Relay Control

### Via browser (simple):
```
# Turn fan OFF:
http://localhost:1880/relay/off

# Turn fan ON:
http://localhost:1880/relay/on
```

### Via curl/PowerShell:
```powershell
# Turn OFF
Invoke-RestMethod -Uri "http://localhost:1880/relay" -Method Post -Body '{"relay": false}' -ContentType "application/json"

# Turn ON
Invoke-RestMethod -Uri "http://localhost:1880/relay" -Method Post -Body '{"relay": true}' -ContentType "application/json"
```

---

## Troubleshooting

### Docker Issues

| Problem | Solution |
|---------|----------|
| `docker compose up` fails | Make sure Docker Desktop is running. Check with `docker info` |
| Port 1883/1880/8086/3000 in use | Close other apps using those ports, or change ports in `docker-compose.yml` |
| Container keeps restarting | Check logs: `docker logs <container_name>` |
| InfluxDB won't start | Delete volume and restart: `docker compose down -v && docker compose up -d` |

### ESP32 Issues

| Problem | Solution |
|---------|----------|
| WiFi won't connect | Check SSID/password. Make sure 2.4GHz WiFi (ESP32 doesn't support 5GHz) |
| MQTT won't connect | Check PC IP is correct. Make sure ESP32 and PC are on same WiFi network |
| COM port busy | Close Arduino Serial Monitor before uploading. Close other serial programs |
| MPU6050 not found | Check I2C wiring (SDA=21, SCL=22). Check 3V3 power |
| No MQTT messages | Verify with `docker exec mosquitto mosquitto_sub -t "#"` to see all messages |

### Grafana Issues

| Problem | Solution |
|---------|----------|
| "No Data" on panels | Check InfluxDB datasource config. Verify token matches `.env` file |
| Dashboard not loading | Go to Dashboards → Browse → Find and click the HVAC dashboard |
| Login failed | Default: admin / hvac_grafana_2026. Reset: `docker exec grafana grafana-cli admin reset-admin-password newpass` |

### Firewall Issues
If the ESP32 can connect to WiFi but not to MQTT, your Windows Firewall may be blocking port 1883:
1. Open **Windows Defender Firewall** → **Advanced Settings**
2. **Inbound Rules** → **New Rule**
3. Port → TCP → 1883 → Allow → Name: "MQTT Broker"

---

## File Structure

```
stage2-running/
├── docker-compose.yml          # 4-service Docker stack
├── .env                        # Passwords & tokens
│
├── firmware/
│   └── inference_firmware/
│       ├── inference_firmware.ino   # ESP32 firmware (THE MAIN CODE)
│       └── model_params.h          # Trained ML model (from Stage 1)
│
├── mosquitto/
│   └── config/
│       └── mosquitto.conf      # MQTT broker configuration
│
├── nodered/
│   └── data/
│       ├── flows.json          # Data pipeline + alert flows
│       └── settings.js         # Node-RED settings
│
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── datasource.yml  # Auto-config InfluxDB source
│       └── dashboards/
│           ├── dashboard.yml   # Dashboard provisioner config
│           └── hvac_dashboard.json  # 8-panel SCADA dashboard
│
├── README.md                   # This file
└── DEMO_PLAN.md                # Structured demo script for presentation
```

---

## Technology Stack Summary

| Layer | Technology | Role |
|-------|-----------|------|
| **Edge** | ESP32 + Arduino C++ | Sensor reading, feature extraction, K-Means inference |
| **Communication** | MQTT (Mosquitto) | Lightweight publish/subscribe messaging |
| **Data Pipeline** | Node-RED | JSON parsing, InfluxDB writing, alerts, relay control |
| **Time-Series DB** | InfluxDB 2.7 | Stores all sensor + anomaly data with timestamps |
| **Visualization** | Grafana 10.2 | Real-time SCADA dashboard with 8 panels |
| **ML Model** | K-Means (3 clusters) | Anomaly detection trained in Stage 1 |

---

## How the AI Works (Quick Reference)

```
Sensor Data (100Hz)
     │
     ▼
256-sample Window (2.56s)
     │
     ▼
12 Features Extracted:
  [vib_rms, vib_peak, vib_crest, vib_kurt,
   cur_rms, cur_std,
   dom_freq, spec_rms, spec_cent,
   band1, band2, band3]
     │
     ▼
StandardScaler:  scaled = (raw - mean) / std
     │
     ▼
K-Means Distance: min_dist = min(dist_to_centroid[0..2])
     │
     ▼
Anomaly Score: score = min_dist / 845.6
     │
     ▼
Classification:
  score < 0.0035  → NORMAL
  score < 0.0500  → WARNING   → Alert sent
  score ≥ 0.0500  → CRITICAL  → Auto-shutdown relay
```
