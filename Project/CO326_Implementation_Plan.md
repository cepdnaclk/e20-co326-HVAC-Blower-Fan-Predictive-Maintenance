# CO326 Implementation Plan
## Industrial Digital Twin & Cyber-Physical Security
### Project Focus: HVAC Blower Fan Predictive Maintenance with Edge AI and Digital Twin

---

## 1. Purpose of This Document

This document converts the original AI-generated project selection report into a practical implementation plan that can be used by the team during development. The goal is to build a compact but impressive industrial IoT prototype that demonstrates predictive maintenance, a secure edge-to-cloud pipeline, a digital twin dashboard, and basic anomaly detection using an ESP32-based edge device.

The selected concept is an **HVAC blower fan predictive maintenance system** that monitors vibration and current signals from a physical fan, processes them at the edge, sends them through an MQTT pipeline, stores them in a time-series database, and visualizes the system using Grafana dashboards and a digital twin style interface.

---

## 2. Project Objective

To design and implement a small-scale industrial digital twin system that can:

- Monitor the condition of an HVAC-style blower fan in real time
- Detect abnormal operating behavior using edge-based anomaly detection
- Transmit telemetry securely using MQTT
- Store and visualize data in a cloud-style monitoring stack
- Support bidirectional control from dashboard to device
- Demonstrate the idea of predictive maintenance and remaining useful life estimation

---

## 3. Final System Scope

The final prototype should include the following core capabilities:

### 3.1 Physical Layer
- A 12V DC brushless fan as the physical plant
- An accelerometer to capture vibration behavior
- A current sensor to measure power/current signature
- A relay module to switch the fan ON and OFF
- An ESP32-S3 as the edge controller

### 3.2 Edge Intelligence Layer
- Sensor sampling and filtering
- Feature extraction from vibration and current signals
- A lightweight anomaly detection model running on the ESP32
- Local buffering in case of network disruption
- MQTT publishing with topic-based structure

### 3.3 Platform Layer
- Mosquitto as the MQTT broker
- Node-RED for data routing, analytics, control logic, and simulation
- InfluxDB for time-series storage
- Grafana for dashboards and digital twin visualization

### 3.4 Application Layer
- Live monitoring panels
- Health index and anomaly score visualization
- Remaining useful life (RUL) approximation
- Fan ON/OFF control from dashboard
- Fault injection demo for presentation

---

## 4. Recommended Implementation Strategy

Instead of trying to build everything at once, the project should be developed in **four controlled phases**. This reduces risk and makes daily testing easier.

### Phase 1 — Foundation Setup
This phase focuses on making the hardware and software environment ready.

**Main outputs:**
- Docker services running correctly
- ESP32 development environment working
- Fan, sensors, and relay wired and tested individually

**Success criteria:**
- ESP32 can be programmed successfully
- Fan can be switched through GPIO/relay
- Sensor values can be read consistently on serial output

### Phase 2 — Data Pipeline Integration
This phase connects the edge device to the monitoring platform.

**Main outputs:**
- ESP32 publishes data through MQTT
- Node-RED receives and processes messages
- InfluxDB stores sensor measurements
- Grafana shows live telemetry

**Success criteria:**
- End-to-end flow works from sensor to dashboard
- Telemetry updates are visible in near real time
- Topic structure is stable and documented

### Phase 3 — Intelligence and Twin Behavior
This phase adds edge analytics and system modeling.

**Main outputs:**
- Feature extraction implemented
- K-Means based anomaly scoring running on ESP32
- Dashboard includes anomaly score and health status
- Digital twin visualization reflects actual fan state

**Success criteria:**
- Normal and faulty conditions can be distinguished
- Fault injection causes visible anomaly changes
- Dashboard state matches physical device state

### Phase 4 — Reliability, Security, and Demo Readiness
This phase improves the professionalism of the system.

**Main outputs:**
- TLS or at least authenticated MQTT communication
- Reconnection and buffering logic
- RUL estimate and alerting flow
- Final documentation and rehearsed demo

**Success criteria:**
- System can recover from brief disconnections
- Security features are demonstrable
- Demo can be presented smoothly within 5 minutes

---

## 5. Work Breakdown Structure (WBS)

## 5.1 Hardware Workstream

### Tasks
1. Select and purchase all components
2. Test fan operation with dedicated power supply
3. Connect accelerometer to ESP32 using I2C
4. Connect ACS712 to ESP32 ADC
5. Integrate relay with fan switching circuit
6. Mount sensors securely for repeatable readings
7. Prepare safe and neat desk-top enclosure/base

### Expected deliverables
- Stable hardware prototype
- Wiring diagram
- Basic electrical safety notes

---

## 5.2 Firmware Workstream

### Tasks
1. Create ESP32 firmware project structure
2. Implement Wi-Fi connection manager
3. Implement sensor reading modules
4. Implement data filtering and calibration
5. Implement feature extraction functions
6. Implement MQTT publishing/subscription
7. Implement command handling for relay control
8. Add anomaly detection logic
9. Add offline buffering and reconnection logic

### Expected deliverables
- Modular firmware source code
- Configuration file for Wi-Fi, MQTT, and certificates
- Serial test logs showing stable operation

---

## 5.3 Backend / Middleware Workstream

### Tasks
1. Configure Mosquitto broker
2. Create Node-RED ingestion flow
3. Validate incoming payload format
4. Write processed data to InfluxDB
5. Build control command flow from dashboard to edge
6. Add simulation and analytics flow
7. Add alert flow for abnormal conditions

### Expected deliverables
- Node-RED flow export
- MQTT topic documentation
- Working end-to-end data processing pipeline

---

## 5.4 Visualization Workstream

### Tasks
1. Connect Grafana to InfluxDB
2. Create real-time telemetry panels
3. Build anomaly and health panels
4. Create digital twin status view
5. Add RUL and confidence indicators
6. Add alert and event panels
7. Improve layout to look like a professional SCADA screen

### Expected deliverables
- Final Grafana dashboard
- Dashboard screenshots for report/presentation

---

## 5.5 ML / Analytics Workstream

### Tasks
1. Collect normal operation samples
2. Preprocess and analyze collected data on PC
3. Train a simple K-Means model on extracted features
4. Select centroid and threshold values
5. Port inference logic to ESP32
6. Test anomaly scoring using induced fault conditions
7. Implement simple RUL trend estimation in Node-RED

### Expected deliverables
- Training notebook or Python script
- Model description
- Threshold selection notes
- Demo results showing anomaly spike under fault condition

---

## 5.6 Documentation and Presentation Workstream

### Tasks
1. Prepare architecture diagram
2. Prepare wiring diagram
3. Document topic tree and payload fields
4. Document firmware module structure
5. Document security design choices
6. Write testing evidence and screenshots
7. Prepare final demo script and speaking flow

### Expected deliverables
- Technical report material
- Presentation-ready diagrams
- Final demo checklist

---

## 6. Team Role Allocation

Assuming a team of 3–4 members, a practical distribution is as follows:

| Role | Main Responsibility |
|---|---|
| Member 1 | ESP32 firmware, MQTT, anomaly detection |
| Member 2 | Hardware integration, relay/fan circuit, testing |
| Member 3 | Node-RED, InfluxDB, Grafana dashboards |
| Member 4 | Documentation, diagrams, integration support, demo planning |

If there are only 3 members, Member 4 responsibilities can be shared across the team.

---

## 7. Implementation Timeline

## Day 1 — Setup and Architecture

### Main focus
Set up the overall development environment and verify the basic hardware/software foundation.

### Tasks
- Install Docker Desktop and pull required images
- Create the initial `docker-compose.yml`
- Start Mosquitto, Node-RED, InfluxDB, and Grafana
- Install Arduino IDE or PlatformIO
- Flash a basic ESP32 test program
- Define project folder structure and topic tree

### End-of-day target
The infrastructure stack is running and the ESP32 board is confirmed operational.

---

## Day 2 — Sensor and Actuator Integration

### Main focus
Connect all hardware modules and confirm reliable signal acquisition.

### Tasks
- Wire accelerometer to ESP32
- Wire current sensor to ESP32
- Build relay + fan switching circuit
- Read raw values from all sensors
- Add sampling loops and basic filtering
- Validate power and grounding stability

### End-of-day target
The fan can be controlled, and sensor readings are being captured correctly.

---

## Day 3 — End-to-End Communication

### Main focus
Create the full telemetry path from edge device to dashboard backend.

### Tasks
- Connect ESP32 to Wi-Fi
- Publish telemetry using MQTT
- Build Node-RED ingestion flow
- Store measurements in InfluxDB
- Connect Grafana to the database
- Visualize raw measurements in real time

### End-of-day target
Live data should move successfully from the physical system to Grafana.

---

## Day 4 — Edge Intelligence

### Main focus
Implement anomaly detection and validate it using simple fault injection.

### Tasks
- Record normal operating data
- Extract features such as RMS, peak, and current variation
- Train simple K-Means model on PC
- Port centroid-based inference to ESP32
- Compute anomaly score and publish it via MQTT
- Test abnormal behavior by attaching tape/weight to the fan blade

### End-of-day target
The system can distinguish between normal and faulty operation using edge-based scoring.

---

## Day 5 — Digital Twin and Control

### Main focus
Improve the monitoring interface and add control functionality.

### Tasks
- Build dashboard panels for vibration, current, anomaly score, and state
- Create dashboard control for fan ON/OFF
- Route control command through Node-RED to ESP32 relay
- Build a digital twin-style display synchronized with real fan state
- Add simulated “what-if” scenario using Node-RED

### End-of-day target
The dashboard is interactive and behaves like a basic digital twin instead of only a monitoring panel.

---

## Day 6 — Reliability, Security, and Analytics

### Main focus
Make the system more realistic and presentation-ready.

### Tasks
- Add reconnection logic and message buffering
- Add authentication and, if possible, TLS for MQTT
- Implement simple RUL trend estimation in Node-RED
- Add health index and confidence display to dashboard
- Add alarm or visual warning logic for critical anomalies
- Perform full integration testing

### End-of-day target
The full system is stable, secure enough for demo purposes, and analytically complete.

---

## Day 7 — Documentation and Final Demo Preparation

### Main focus
Finish project documentation and prepare the demonstration flow.

### Tasks
- Prepare architecture diagram
- Prepare wiring diagram and simplified P&ID
- Export Node-RED flows
- Document MQTT topic tree and payload design
- Prepare screenshots and testing evidence
- Rehearse full demo several times
- Clean code and organize repository

### End-of-day target
All technical artifacts are complete and the team is ready to present confidently.

---

## 8. Suggested Repository / Folder Structure

```text
project-root/
├── firmware/
│   ├── src/
│   │   ├── main.cpp
│   │   ├── sensors/
│   │   ├── ml/
│   │   ├── comms/
│   │   └── control/
│   ├── certs/
│   └── platformio.ini
├── docker/
│   ├── mosquitto/
│   ├── nodered/
│   ├── influxdb/
│   └── grafana/
├── analytics/
│   ├── notebooks/
│   ├── training/
│   └── datasets/
├── docs/
│   ├── architecture/
│   ├── diagrams/
│   ├── screenshots/
│   └── demo-script/
├── docker-compose.yml
└── README.md
```

This structure keeps firmware, platform services, analytics, and documentation clearly separated.

---

## 9. Key MQTT Topic Plan

A simplified topic structure is enough if the full Sparkplug B implementation becomes too heavy for the timeline.

### Recommended practical topic structure

```text
hvac_fan01/data/vibration
hvac_fan01/data/current
hvac_fan01/data/features
hvac_fan01/data/anomaly
hvac_fan01/state/status
hvac_fan01/cmd/relay
hvac_fan01/analytics/rul
hvac_fan01/alerts/critical
```

### If time allows
Move to a more industrial naming style aligned with Sparkplug B / unified namespace concepts.

---

## 10. Minimum Viable Product (MVP)

If time becomes tight, the team should protect the following minimum working version first:

- Fan hardware working safely
- ESP32 reading vibration and current
- MQTT telemetry reaching Node-RED
- InfluxDB + Grafana dashboard working
- Relay control from dashboard
- Simple anomaly score based on threshold or centroid distance

This MVP alone is already a strong demo. The following can be treated as enhancement items:

- Full TLS on MQTT
- Full Sparkplug B compliance
- Advanced digital twin animation
- Sophisticated RUL modeling
- Email alerts

---

## 11. Risk-Based Planning Notes

### High-priority risks

| Risk | Likely Impact | Response |
|---|---|---|
| ESP32-S3 unavailable | Delays firmware work | Use standard ESP32 as fallback |
| Accelerometer readings are noisy | Poor anomaly detection | Apply moving average and stable mounting |
| MQTT/TLS setup takes too long | Integration delay | Start with plain MQTT first, secure later |
| Fan vibration is too weak | Demo impact reduced | Mount sensor directly and use intentional imbalance |
| Docker uses too much memory | Platform instability | Close other apps and reduce resource usage |
| K-Means on edge becomes difficult | ML delay | Use threshold-based anomaly score as backup |

### Important planning principle
The team should always implement **basic functionality first**, then add industrial-grade improvements after the pipeline is already working.

---

## 12. Testing Plan

Testing should be done continuously instead of waiting until the end.

### Unit-level checks
- Sensor reading validation on serial monitor
- Relay switching test
- Wi-Fi connection test
- MQTT publish/subscribe test
- InfluxDB write verification
- Grafana panel update verification

### Integration-level checks
- Sensor to MQTT pipeline
- MQTT to Node-RED to database flow
- Dashboard control to relay action
- Fault injection to anomaly detection response
- Network disconnection to buffering/recovery behavior

### Demo-level checks
- System startup sequence works cleanly
- Dashboard values are updating live
- Fan responds to control command
- Fault injection creates visible anomaly spike
- Team can explain architecture clearly in simple language

---

## 13. Demo Planning

The presentation should focus on clarity, not only technical detail.

### Recommended 5-minute flow
1. Introduce the problem: industrial fans degrade over time and need predictive maintenance.
2. Show the physical setup: fan, sensors, ESP32, relay.
3. Show the architecture: edge, transport, processing, visualization.
4. Show live dashboard updates.
5. Turn the fan ON/OFF from the dashboard.
6. Inject a fault using tape/weight and show anomaly score increase.
7. Show health/RUL estimate.
8. Briefly mention security and buffering features.

### What will make the demo strong
- Real hardware visible on the table
- Live dashboard reacting to changes
- Real-time anomaly response during fault injection
- Clear explanation of how edge AI is being used
- A professional-looking dashboard and clean wiring setup

---

## 14. Recommended Deliverables to Prepare

By the final day, the team should have the following ready:

- Working prototype
- Source code repository
- Docker Compose setup
- Firmware modules
- Node-RED flow export
- Grafana dashboard screenshots
- System architecture diagram
- Wiring diagram
- MQTT topic documentation
- TinyML / anomaly detection explanation
- Cybersecurity design summary
- Final demo script

---

## 15. Final Recommendation

This project is a strong choice because it is practical, visually demonstrable, technically rich, and achievable within a short time if the team follows a phased implementation strategy. The most important factor is disciplined execution: start from a small working core, validate each layer one by one, and only then add advanced features like edge ML, security hardening, and RUL estimation.

The team should treat the project as a **real engineering build**, not only a feature list. That means each day should end with something working, tested, and documented. If this approach is followed, the final system will not only be impressive during the demo, but also easy to explain to the lecturer as a complete industrial IoT and digital twin solution.

---

## 16. Source Basis

This implementation plan was prepared by restructuring the uploaded project planning/report document and turning it into a more execution-oriented markdown guide.
