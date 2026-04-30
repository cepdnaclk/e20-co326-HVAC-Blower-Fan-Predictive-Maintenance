# 🎯 HVAC Fan Predictive Maintenance — Demo Plan

> **Structured 15-minute presentation to impress your lecturer**

---

## 🕐 Timeline (15 minutes)

| Time | Section | Duration | What You Show |
|------|---------|----------|---------------|
| 0:00 | Architecture | 2 min | Explain the system on whiteboard/slide |
| 2:00 | Docker Stack | 2 min | Show containers running + Portainer-like view |
| 4:00 | Live Normal | 3 min | Dashboard showing healthy fan in real-time |
| 7:00 | Fault Injection | 3 min | Attach weight → watch anomaly score spike |
| 10:00 | Auto-Shutdown | 2 min | Critical threshold → relay cuts fan power |
| 12:00 | Recovery | 1 min | Remove weight → score returns to normal |
| 13:00 | Code Walkthrough | 2 min | Show key C++ inference code on ESP32 |

---

## 📝 Script

### Part 1: Architecture Overview (0:00 — 2:00)

**What to say:**
> "Our system is a complete IIoT predictive maintenance pipeline. We have an ESP32 microcontroller attached to a blower fan with two sensors — an accelerometer for vibration and a current sensor. The ESP32 runs a K-Means anomaly detection model directly on the chip — this is called TinyML or Edge AI. It extracts 12 features from a 2.56-second sliding window of raw sensor data, calculates how far those features are from the 'healthy' cluster centroids, and publishes an anomaly score over MQTT to our Docker container stack."

> "On the server side, we have 4 Docker containers: Mosquitto as the MQTT broker, Node-RED for data orchestration and alerts, InfluxDB as a time-series database, and Grafana for the real-time SCADA dashboard."

**What to show:**
- Point to the physical hardware (fan, ESP32, sensors, relay)
- Draw or show the architecture diagram from README.md

---

### Part 2: Docker Stack (2:00 — 4:00)

**What to say:**
> "Let me show you the infrastructure. We have 4 containers running."

**What to do:**
```powershell
docker compose ps
```

> "Each container has a specific role. Let me show you the data pipeline in Node-RED."

**What to show:**
1. Open **http://localhost:1880** — show the 3 flow tabs:
   - **Data Pipeline**: MQTT In → Parse → InfluxDB
   - **Alert Engine**: Threshold checking with rate-limited alerts
   - **Relay Control**: HTTP endpoint for dashboard relay button
2. Point to the debug sidebar showing live JSON messages arriving

---

### Part 3: Live Normal Operation (4:00 — 7:00)

**What to say:**
> "Now let me show you the Grafana dashboard. This refreshes every 5 seconds with live data from the fan."

**What to show:**
1. Open **http://localhost:3000** → HVAC Dashboard
2. Point out each panel:
   - **Anomaly Score gauge**: "Currently at 0.0017 — deep in the green zone. This means the fan vibration signature matches our trained 'healthy' model perfectly."
   - **Vibration RMS**: "Real-time vibration magnitude in meters per second squared"
   - **Health Status**: "Shows NORMAL — computed on the ESP32, not the server"
   - **Time Series**: "30-minute rolling history. You can see the score is consistently flat and low."
   - **Spectral Bands**: "This shows the frequency decomposition — band1 is 0-50Hz (imbalance), band2 is 50-200Hz (bearing faults), band3 is 200-500Hz (blade defects)"

3. Open **Serial Monitor** on Arduino IDE:
   > "And here you can see the ESP32 printing each inference result in real-time. The feature extraction and K-Means inference take about 45 milliseconds per window — well within our 2.56-second cycle."

---

### Part 4: Fault Injection — The WOW Moment (7:00 — 10:00)

**⚠️ This is the most impressive part. Build suspense!**

**What to say:**
> "Now for the exciting part. I'm going to simulate a real-world mechanical fault — blade imbalance. In a real HVAC system, this happens when dust accumulates unevenly or a blade cracks."

**What to do:**
1. **Have the weight ready** (25g — a bolt, coins taped together, etc.)
2. Say: *"Watch the anomaly score gauge..."*
3. **STOP the fan briefly** (use relay or unplug), **tape the weight** to one blade
4. **Restart the fan**
5. Point to the dashboard and let the audience watch the score climb

**What happens:**
- Within 5-10 seconds, the anomaly score jumps from ~0.001 to ~0.6
- The gauge turns from GREEN → YELLOW → RED
- Health status changes to 🚨 CRITICAL
- Node-RED fires an alert (show debug panel)

**What to say:**
> "The K-Means model detected the imbalance in real-time. The anomaly score jumped from 0.0017 to 0.62 — that's a 365x increase. The model has never seen this specific fault before during training — it only learned what 'healthy' looks like, and correctly identified that the current vibration pattern is far outside the healthy boundaries."

---

### Part 5: Auto-Shutdown Demo (10:00 — 12:00)

**What to say:**
> "When the score crosses 0.05 — the critical threshold — the ESP32 automatically cuts the relay, physically shutting down the fan. This is edge computing in action — the decision was made on the microcontroller, not the cloud. Even if WiFi goes down, the ESP32 would still protect the equipment."

**What to show:**
- Point to the **relay status panel**: 🔴 FAN OFF
- Point to the **physical fan**: it has stopped spinning
- Show the Serial Monitor: `[ALERT] ⚠ CRITICAL ANOMALY — Auto-shutdown triggered!`

**Then demonstrate remote control:**
> "I can also control the fan remotely from the dashboard."

Open browser:
```
http://localhost:1880/relay/on
```
> "The command goes from my browser → Node-RED → MQTT → ESP32 → Relay ON. The fan restarts."

---

### Part 6: Recovery (12:00 — 13:00)

**What to do:**
1. Stop the fan (relay off)
2. Remove the weight
3. Turn relay back on: `http://localhost:1880/relay/on`

**What to show:**
- Anomaly score drops back to ~0.0015
- Health status returns to ✅ NORMAL
- Time series chart shows the full story: the spike and recovery

**What to say:**
> "The system correctly identifies recovery. The time-series chart tells the full maintenance story — we can see exactly when the fault occurred, how severe it was, and when it was resolved."

---

### Part 7: Code Walkthrough (13:00 — 15:00)

If the lecturer asks technical questions, show these key code sections:

**Feature extraction on ESP32 (C++):**
> "We compute 12 features on-device: 4 vibration features (RMS, peak, crest factor, kurtosis), 2 current features, and 6 frequency-domain features using a DFT."

**K-Means inference (C++):**
> "The inference is simple but powerful — we scale the feature vector using the saved StandardScaler parameters, compute Euclidean distance to each of 3 trained centroids, and normalize the minimum distance into a 0-1 anomaly score."

**Training pipeline (Python):**
> "We trained the model in Python using scikit-learn. We collected 2,438 feature vectors — 1,638 normal and 800 anomalous. The model achieved an ROC AUC of 0.9629."

---

## 🎯 Key Talking Points (If Lecturer Asks Questions)

### "Why K-Means instead of a neural network?"
> "K-Means runs in constant time O(K×D) per inference — about 1ms on ESP32. An LSTM would need TensorFlow Lite and takes 100x more memory. For edge deployment, simplicity wins. We also trained an LSTM Autoencoder as a secondary model for server-side verification."

### "What's your model accuracy?"
> "ROC AUC of 0.9629, which is considered outstanding. The F1 score is 0.58 for the warning class because a 10-gram weight produces a very subtle vibration change — this is realistic for early-stage faults in industrial equipment."

### "How does this scale to multiple fans?"
> "Each fan gets its own MQTT topic (hvac/fan01, hvac/fan02...) and its own trained model. Node-RED routes all data to a single InfluxDB bucket with device tags. Grafana can display multiple fans with template variables."

### "What if WiFi drops?"
> "The ESP32 continues running inference locally and protecting the equipment via the relay. The Sparkplug B protocol (our MQTT namespace) uses Last Will and Testament messages — Grafana would show the device as offline."

### "What about false positives?"
> "Our WARNING threshold (0.0035) was calibrated using the full dataset in validate_model.py. It produced zero false positives on the normal test data. The dual-threshold system (WARNING + CRITICAL) gives operators time to inspect before auto-shutdown."

---

## 📌 Pre-Demo Checklist

- [ ] Docker Desktop is running
- [ ] All 4 containers are UP (`docker compose ps`)
- [ ] ESP32 is flashed and showing `[RUN] Inference engine started!`
- [ ] Node-RED flows are deployed (green "connected" dots)
- [ ] Grafana dashboard is showing live data
- [ ] Weights are prepared and nearby (10g + 25g)
- [ ] Tape is ready for attaching weights
- [ ] Serial Monitor is open (to show live inference logs)
- [ ] Browser tabs ready: Grafana, Node-RED, InfluxDB
- [ ] Fan is running normally for at least 1 minute before demo starts
