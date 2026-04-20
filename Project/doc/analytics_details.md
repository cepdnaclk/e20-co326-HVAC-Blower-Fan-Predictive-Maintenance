# Analytics and Digital Twin Details

## Edge Intelligence
The ESP32 runs a lightweight K-Means inference model. 
1. **Features Extracted:** RMS Vibration, RMS Current.
2. **Model:** K-Means (k=1 cluster) acting as a one-class anomaly detector.
3. **Anomaly Score:** Euclidean distance from the learned "normal" centroid.

## Platform Twin Logic
Once telemetry arrives via Node-RED:
1. Data is routed to InfluxDB for historical storage.
2. Anomaly scores over a specific threshold trigger a "Critical Alert".
3. RUL (Remaining Useful Life) is a secondary calculation in Node-RED simulating degradation trends.
