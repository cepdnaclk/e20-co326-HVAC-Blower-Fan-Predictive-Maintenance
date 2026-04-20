# MQTT Topic Structure

We use a flat topic structure suitable for a small-scale industrial prototype.

## Telemetry
- `hvac_fan01/data/vibration`: Raw/RMS vibration data
- `hvac_fan01/data/current`: RMS current data
- `hvac_fan01/data/features`: Extracted features for ML
- `hvac_fan01/data/anomaly`: Anomaly score and health status

## State and Commands
- `hvac_fan01/state/status`: Device health and uptime
- `hvac_fan01/cmd/relay`: Control topic (send "ON" or "OFF")

## Analytics
- `hvac_fan01/analytics/rul`: Node-RED calculated RUL
- `hvac_fan01/alerts/critical`: Alerts triggered by high anomaly score
