

## Project Proposal
Industrial Digital Twin & Cyber-Physical Security
An Edge-to-Cloud IIoT Integration Project
## Target Audience:
3rd-Year Computer Engineering Undergraduates
## Project Duration:
3 Weeks (Team of 3–4 students)
## Role Assumption:
Students act as Industrial IoT System Integrators, designing a secure, production-oriented
IIoT system

## 1. Executive Summary
Industrial systems are undergoing a fundamental transformation driven by OT/IT convergence,
where traditionally isolated Operational Technology (OT) systems are now tightly integrated with
modern Information Technology (IT) platforms. This convergence enables real-time visibility,
predictive analytics, and intelligent decision-making across industrial operations.

This project challenges students to design and implement a secure, industrial-grade Digital
Twin system that bridges edge devices (ESP32-S3) with cloud-based analytics, using open
industrial protocols and tools. The system moves beyond traditional reactive maintenance
toward predictive and condition-based maintenance, leveraging real sensor data, edge AI,
and cloud analytics.

Each group should take one industrial problem (e.g., motor health monitoring, pump cavitation
detection, fan imbalance detection). Only one sensor and one actuator should be used.
Although a reliable power supply is required for industry applications, this project does not
necessitate one unless required by the components.



Although the industrial application differs, all groups must use the same technical
framework, architecture, and tools. The course coordinator will provide them. The goal is not to
build a complex physical machine, but to design a realistic, scalable, and secure industrial
monitoring and Digital Twin system.
Students will develop:
● A Cyber-Physical System (CPS)

● A Unified Namespace–driven IIoT architecture

● A Digital Twin with bidirectional control

● An ML-enabled fault detection pipeline

● A secure and reliable MQTT-based data infrastructure

The final system emulates real industrial deployments used in power plants, manufacturing
lines, and utilities, preparing students for Industry 4.0 roles.

## 2. Project Objectives
## Primary Objectives
- Design and implement a 4-layer Industrial IoT architecture
- Implement a secure edge-to-cloud data pipeline

- Build a Digital Twin synchronised with physical assets

- Apply Edge AI (TinyML) for real-time anomaly detection

- Implement predictive analytics for Remaining Useful Life (RUL) or any other ML-based
output

- Demonstrate bidirectional cyber-physical control

- Produce industry-standard technical documentation


## Learning Outcomes
By completing this project, students will:
● Understand OT vs IT system integration

● Apply industrial communication standards

● Design fault-tolerant cyber-physical systems

● Gain hands-on experience with edge-to-cloud architectures

● Produce industry-grade documentation


## 3. System Overview
Physical System (Plant Model)
An example industrial rotating asset (e.g., motor + load) instrumented with:
## Sensor Purpose
Split-core CT Motor current signature analysis
Accelerometer Vibration and mechanical fault detection
## Relay / Contactor


Actuation and control
Sensors and actuators are different for each industry project. Select appropriately.
## Cyber System
● Edge data acquisition & AI inference

● Secure message transport

● Centralised historian and analytics

● Real-time Digital Twin visualisation and control



- Core Technologies (Mandatory)
## Hardware
● ESP32-S3 (Dual-core, AI-capable MCU)

● Split-core Current Transformers (CTs)

## ● 3-axis Accelerometers

● Industrial relay module

## Communication & Infrastructure
● MQTT with Sparkplug B

● Modbus TCP (for industrial realism)

● Docker-based deployment

## Software Stack
## Layer Technology
Edge Logic ESP-IDF / Arduino + TinyML
Middleware Node-RED
Historian InfluxDB
Visualization (SCADA) Grafana

- Industrial IIoT Architecture
5.1 Four-Layer Architecture
## Layer 1 – Perception Layer

● Sensors acquire raw physical signals

● ESP32-S3 performs:

## ○ Sampling

## ○ Filtering

○ Feature extraction

○ Local inference (TinyML)

## Layer 2 – Transport Layer
● MQTT (Sparkplug B payloads)

● Modbus TCP for register-based data

● Encrypted communication (TLS)

Layer 3 – Edge-Logic Layer
● Node-RED flows handle:

○ Data normalization

○ State modeling

○ Rule-based decisions

○ ML inference orchestration

## Layer 4 – Application Layer
● InfluxDB time-series historian

● Grafana dashboards (SCADA-like)

● Digital Twin control interface



- Unified Namespace (UNS)
## Concept
A Unified Namespace is a single, structured, real-time data model representing the entire
industrial system.
## Requirements
● All devices publish to a hierarchical MQTT topic structure

● Sparkplug B used for:

○ Birth certificates

○ State awareness

○ Metric consistency

## Example Topic Structure:
spBv1.0/factoryA/NCMD/area1/motor01
spBv1.0/factoryA/DDATA/area1/motor01

## Benefits
● Decouples producers from consumers

● Enables scalable Digital Twins

● Simplifies analytics and integration


## 7. Digital Twin Specifications
7.1 Digital Model vs Digital Shadow
## Concept Description

Digital Model Static representation, no live data
Digital Shadow Real-time synchronized data flow (one-way)
Digital Twin Bidirectional synchronization and control
## 7.2 Mandatory Digital Twin Features
- Live synchronization with physical system

- Bidirectional control

○ Grafana / Node-RED dashboard controls physical relay

## 3. Simulation Mode

○ “What-if” analysis:

■ Increased load

■ Abnormal vibration

■ Current imbalance

- State consistency checks

○ Twin vs physical mismatch detection


## 8. Machine Learning Deliverables
8.1 Edge AI (TinyML on ESP32-S3)
## Objective
Detect mechanical anomalies locally, without cloud dependency.
Algorithms (Choose One)
● K-Means clustering (unsupervised)


● Lightweight autoencoder

## Input Features
● RMS current

● Vibration magnitude

● Frequency components (optional)

## Requirements
● Model must run on ESP32-S3

● Inference latency < 50 ms

● Publish anomaly score via MQTT


8.2 Cloud Analytics – RUL Estimation
## Method
● Linear regression implemented in Node-RED

## Inputs
● Historical vibration trend

● Anomaly frequency

● Load variation

## Output
● Remaining Useful Life (RUL) estimate

● Confidence indicator



## 9. Cybersecurity & Reliability Requirements
## 9.1 Security
● MQTT over TLS

● Credential-based device authentication

● Encrypted configuration storage

## 9.2 Reliability
● MQTT Last Will & Testament (LWT)

● Local buffering on ESP32 during network outages

● Automatic reconnection logic

● Timestamped data consistency


## 10. Industrial Standards & Documentation
## Mandatory Documentation
## 1. System Architecture Diagram

## 2. Electrical Wiring Diagram

- P&ID (simplified)

- MQTT Topic Tree

- Node-RED Flow Export

- ML Model Description


## 7. Cybersecurity Design Summary


- Project Timeline (Suggested)
## Week Activities
1 Architecture design, UNS definition
2 Firmware + sensor integration
3 Edge AI + MQTT + buffering
4 Digital Twin + dashboards
5 Security, testing, documentation

## 12. Grading Rubric
## Category Weight Evaluation Criteria
Firmware Robustness 20% Stability, buffering, error handling
Network Design 20% UNS correctness, Sparkplug B,
security
ML Model Accuracy 20% Detection quality, inference efficiency
Digital Twin Synchronisation 20% Bidirectional control, simulation
## Documentation & Industrial
## Presentation
20% Professional quality, clarity

## 13. Expected Deliverables
● Fully working IIoT system

● Live Digital Twin demonstration

● ML-based fault detection


● Industrial-grade documentation

● Final technical presentation


## 14. Conclusion
This project bridges theoretical engineering knowledge with real-world industrial practice,
exposing students to modern IIoT architectures, cybersecurity challenges, Digital Twins,
and predictive maintenance systems. Successful completion equips students with skills
directly applicable to Industry 4.0, smart manufacturing, utilities, and critical infrastructure
environments.
