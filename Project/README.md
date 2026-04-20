# CO326 HVAC Blower Fan Predictive Maintenance

This repository contains the software implementation structure for the HVAC blower fan predictive maintenance system.

## Project Structure
- `firmware/`: ESP32-S3 source code (PlatformIO), including sensor, ML inference, and comm stubs.
- `docker/`: Docker-compose stack containing Mosquitto, Node-RED, InfluxDB, and Grafana.
- `analytics/`: ML prototypes and K-Means training notebook stubs.
- `doc/`: Detailed system documentation.

## Documentation Reference
- [Implementation Plan](CO326_Implementation_Plan.md)
- [Architecture Details](doc/architecture.md)
- [MQTT Topic Layout](doc/mqtt_topics.md)
- [Analytics & Twin](doc/analytics_details.md)
