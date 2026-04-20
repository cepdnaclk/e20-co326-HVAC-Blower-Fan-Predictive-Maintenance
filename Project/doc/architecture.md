# System Architecture

## Overview
The HVAC Blower Fan Predictive Maintenance system consists of Physical, Edge, Platform, and Application layers.

1. **Physical Layer:** 12V DC fan, accelerometer, current sensor, relay.
2. **Edge Layer:** ESP32-S3 performing sensor reading, feature extraction, local anomaly detection, and MQTT publishing.
3. **Platform Layer:** Dockerized stack (Mosquitto, Node-RED, InfluxDB).
4. **Application Layer:** Grafana digital twin dashboard for visualization and Node-RED for control/RUL logic.
