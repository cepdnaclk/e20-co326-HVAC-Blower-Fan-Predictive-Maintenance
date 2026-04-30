/*
 * HVAC Blower Fan — Stage 2 Inference Firmware
 * ==============================================
 * Board:  ESP32 DevKit v1 (WROOM-32)
 *
 * Purpose:
 *   1. Read MPU6050 (vibration) + ACS712 (current) at 100Hz
 *   2. Accumulate 256-sample sliding window (2.56s)
 *   3. Extract 12 features on-device (same as Python pipeline)
 *   4. Run K-Means anomaly detection using trained centroids
 *   5. Publish results over MQTT as JSON to Docker stack
 *   6. Listen for relay control commands from dashboard
 *
 * Wiring (same as Stage 1, plus relay):
 *   MPU6050 VCC → 3V3      MPU6050 GND → GND
 *   MPU6050 SDA → GPIO 21  MPU6050 SCL → GPIO 22
 *   ACS712  OUT → GPIO 34  (ADC input-only pin)
 *   Relay   IN  → GPIO 26  Relay VCC → 5V (from VIN)
 *   Relay   GND → GND
 *
 * MQTT Topics:
 *   Publish:   hvac/fan01/data     (sensor + anomaly JSON)
 *   Subscribe: hvac/fan01/command  (relay ON/OFF)
 *
 * Libraries needed (install via Arduino Library Manager):
 *   - Adafruit MPU6050
 *   - Adafruit Unified Sensor
 *   - PubSubClient (by Nick O'Leary)
 *   - ArduinoJson (by Benoit Blanchon)
 */

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <WiFi.h>
#include <Wire.h>
#include <math.h>

// ═══════════════════════════════════════════════════════════════
// DATA STRUCTURES (Must be defined before auto-generated prototypes)
// ═══════════════════════════════════════════════════════════════
struct FeatureVector {
  float vib_rms, vib_peak, vib_crest, vib_kurt;
  float cur_rms, cur_std;
  float dom_freq, spec_rms, spec_cent;
  float band1, band2, band3;
};

struct AnomalyResult {
  float score;
  int label;
  int nearest_cluster;
  float min_distance;
};

// ═══════════════════════════════════════════════════════════════
// CONFIGURATION — CHANGE THESE FOR YOUR NETWORK
// ═══════════════════════════════════════════════════════════════
#define WIFI_SSID "DialogTharindu4g"
#define WIFI_PASS "g2dM273d"
#define MQTT_BROKER                                                            \
  "192.168.8.101" // PC's IP on same WiFi (e.g. "192.168.1.100")
#define MQTT_PORT 1883
#define MQTT_USER "" // Leave empty (no auth for demo)
#define MQTT_PASS ""
#define DEVICE_ID "hvac_fan01"

// ─── Pin Configuration (same as Stage 1) ─────────────────────
#define I2C_SDA_PIN 21
#define I2C_SCL_PIN 22
#define CURRENT_ADC_PIN 34
#define RELAY_PIN 26 // NEW: Relay module control
#define LED_PIN 2    // Built-in LED for status

// ─── Sampling Configuration ─────────────────────────────────
#define SAMPLE_RATE_HZ 100
#define SAMPLE_PERIOD_US (1000000 / SAMPLE_RATE_HZ)
#define WINDOW_SIZE 256 // 2.56 seconds at 100Hz
#define HOP_SIZE 128    // 50% overlap
#define N_FEATURES 12

// ─── MQTT Topics ─────────────────────────────────────────────
#define TOPIC_DATA "hvac/fan01/data"
#define TOPIC_COMMAND "hvac/fan01/command"
#define TOPIC_STATUS "hvac/fan01/status"

// ═══════════════════════════════════════════════════════════════
// MODEL PARAMETERS (from Stage 1 training)
// ═══════════════════════════════════════════════════════════════
#include "model_params.h"

// ─── ACS712 Calibration ─────────────────────────────────────
#define ACS712_ZERO_POINT 2930    // Your calibrated zero-current ADC reading
#define ACS712_SENSITIVITY 0.185f // V/A for ACS712-5A (185 mV/A)
#define ADC_VREF 3.3f
#define ADC_RESOLUTION 4095.0f

// ─── Current Sensor Toggle ──────────────────────────────────
// Set to false if the fan is NOT wired through the ACS712 sensor.
// When false, cur_rms and cur_std are set to training means (zero
// contribution). Set to true when you wire: 12V → ACS712 IP+ → IP- → Fan
#define USE_CURRENT_SENSOR false

// ═══════════════════════════════════════════════════════════════
// GLOBAL OBJECTS & BUFFERS
// ═══════════════════════════════════════════════════════════════
Adafruit_MPU6050 mpu;
WiFiClient espClient;
PubSubClient mqtt(espClient);

// Circular buffer for sensor data
float buf_ax[WINDOW_SIZE];
float buf_ay[WINDOW_SIZE];
float buf_az[WINDOW_SIZE];
float buf_cur[WINDOW_SIZE];
int buf_idx = 0;
int samples_collected = 0;
bool window_ready = false;

// Timing
unsigned long last_sample_us = 0;
unsigned long last_mqtt_reconnect = 0;
unsigned long inference_count = 0;
unsigned long wifi_connect_start = 0;

// State
bool relay_state = true; // true = fan ON
int current_label = LABEL_NORMAL;
float current_score = 0.0f;

// ═══════════════════════════════════════════════════════════════
// FEATURE EXTRACTION (mirrors Python feature_engineering.py)
// ═══════════════════════════════════════════════════════════════

void extract_features(FeatureVector *fv) {
  // ─── Compute accelerometer magnitude ────────────────────
  static float accel_mag[WINDOW_SIZE]; // static to avoid stack overflow
  for (int i = 0; i < WINDOW_SIZE; i++) {
    accel_mag[i] = sqrtf(buf_ax[i] * buf_ax[i] + buf_ay[i] * buf_ay[i] +
                         buf_az[i] * buf_az[i]);
  }

  // ─── Convert raw ADC to current (Amps) ──────────────────
  static float current[WINDOW_SIZE]; // static to avoid stack overflow
  for (int i = 0; i < WINDOW_SIZE; i++) {
    float voltage =
        (buf_cur[i] - ACS712_ZERO_POINT) * (ADC_VREF / ADC_RESOLUTION);
    current[i] = voltage / ACS712_SENSITIVITY;
  }

  // ─── Time-domain: Vibration features ────────────────────
  // RMS
  float sum_sq = 0;
  for (int i = 0; i < WINDOW_SIZE; i++)
    sum_sq += accel_mag[i] * accel_mag[i];
  fv->vib_rms = sqrtf(sum_sq / WINDOW_SIZE);

  // Peak
  fv->vib_peak = 0;
  for (int i = 0; i < WINDOW_SIZE; i++) {
    float v = fabsf(accel_mag[i]);
    if (v > fv->vib_peak)
      fv->vib_peak = v;
  }

  // Crest factor
  fv->vib_crest = fv->vib_peak / (fv->vib_rms + 1e-9f);

  // Kurtosis
  float mean_mag = 0;
  for (int i = 0; i < WINDOW_SIZE; i++)
    mean_mag += accel_mag[i];
  mean_mag /= WINDOW_SIZE;

  float m2 = 0, m4 = 0;
  for (int i = 0; i < WINDOW_SIZE; i++) {
    float d = accel_mag[i] - mean_mag;
    float d2 = d * d;
    m2 += d2;
    m4 += d2 * d2;
  }
  m2 /= WINDOW_SIZE;
  m4 /= WINDOW_SIZE;
  fv->vib_kurt = (m2 > 1e-9f) ? (m4 / (m2 * m2)) - 3.0f : 0.0f;

  // ─── Time-domain: Current features ──────────────────────
  float cur_mean = 0;
  float cur_sq_sum = 0;
  for (int i = 0; i < WINDOW_SIZE; i++) {
    cur_mean += current[i];
    cur_sq_sum += current[i] * current[i];
  }
  cur_mean /= WINDOW_SIZE;
  fv->cur_rms = sqrtf(cur_sq_sum / WINDOW_SIZE);

  float cur_var = 0;
  for (int i = 0; i < WINDOW_SIZE; i++) {
    float d = current[i] - cur_mean;
    cur_var += d * d;
  }
  fv->cur_std = sqrtf(cur_var / WINDOW_SIZE);

  // ─── Frequency-domain: FFT on ax channel ───────────────
  // Simple DFT (not full FFT — good enough for 256 points on ESP32)
  // We compute magnitude spectrum for first 128 bins
  static float fft_mag[WINDOW_SIZE / 2]; // static to avoid stack overflow
  float ax_mean = 0;
  for (int i = 0; i < WINDOW_SIZE; i++)
    ax_mean += buf_ax[i];
  ax_mean /= WINDOW_SIZE;

  // Zero-mean the signal
  static float ax_zm[WINDOW_SIZE]; // static to avoid stack overflow
  for (int i = 0; i < WINDOW_SIZE; i++)
    ax_zm[i] = buf_ax[i] - ax_mean;

  int half = WINDOW_SIZE / 2;

  // Compute magnitude for each frequency bin using DFT
  // Optimization: only compute bins we need (0-50Hz range = bins 0..128)
  for (int k = 0; k < half; k++) {
    float re = 0, im = 0;
    float angle_step = -2.0f * M_PI * k / WINDOW_SIZE;
    for (int n = 0; n < WINDOW_SIZE; n++) {
      float angle = angle_step * n;
      re += ax_zm[n] * cosf(angle);
      im += ax_zm[n] * sinf(angle);
    }
    fft_mag[k] = sqrtf(re * re + im * im);
  }

  // Dominant frequency
  float max_mag = 0;
  int max_bin = 0;
  for (int k = 1; k < half; k++) { // skip DC bin
    if (fft_mag[k] > max_mag) {
      max_mag = fft_mag[k];
      max_bin = k;
    }
  }
  float freq_resolution =
      (float)SAMPLE_RATE_HZ / WINDOW_SIZE; // 0.390625 Hz/bin
  fv->dom_freq = max_bin * freq_resolution;

  // Spectral RMS
  float spec_sq_sum = 0;
  for (int k = 0; k < half; k++)
    spec_sq_sum += fft_mag[k] * fft_mag[k];
  fv->spec_rms = sqrtf(spec_sq_sum / half);

  // Spectral centroid
  float freq_weight_sum = 0, mag_sum = 0;
  for (int k = 0; k < half; k++) {
    float freq = k * freq_resolution;
    freq_weight_sum += freq * fft_mag[k];
    mag_sum += fft_mag[k];
  }
  fv->spec_cent = (mag_sum > 1e-9f) ? freq_weight_sum / mag_sum : 0.0f;

  // Band power — MUST match Python feature_engineering.py exactly!
  // band1: 0–10 Hz   (imbalance, looseness)
  // band2: 10–25 Hz  (misalignment, belt faults)
  // band3: 25–50 Hz  (bearing defects, blade-pass)
  fv->band1 = 0;
  fv->band2 = 0;
  fv->band3 = 0;
  for (int k = 0; k < half; k++) {
    float freq = k * freq_resolution;
    if (freq < 10.0f)
      fv->band1 += fft_mag[k];
    else if (freq < 25.0f)
      fv->band2 += fft_mag[k];
    else if (freq <= 50.0f)
      fv->band3 += fft_mag[k];
    // frequencies > 50Hz are ignored (same as Python)
  }
}

// ═══════════════════════════════════════════════════════════════
// K-MEANS INFERENCE ENGINE
// ═══════════════════════════════════════════════════════════════

AnomalyResult kmeans_infer(const FeatureVector *fv) {
  // Pack features into array
  float raw[N_FEATURES] = {fv->vib_rms,  fv->vib_peak, fv->vib_crest,
                           fv->vib_kurt, fv->cur_rms,  fv->cur_std,
                           fv->dom_freq, fv->spec_rms, fv->spec_cent,
                           fv->band1,    fv->band2,    fv->band3};

// If current sensor is not in the fan circuit, override with training means
// so they contribute zero to the distance after scaling
#if !USE_CURRENT_SENSOR
  raw[4] = SCALER_MEAN[4]; // cur_rms → set to training mean
  raw[5] = SCALER_MEAN[5]; // cur_std → set to training mean
#endif

  // Apply StandardScaler: scaled = (raw - mean) / scale
  float scaled[N_FEATURES];
  for (int j = 0; j < N_FEATURES; j++) {
    scaled[j] = (raw[j] - SCALER_MEAN[j]) / (SCALER_SCALE[j] + 1e-9f);
  }

  // Find nearest centroid (Euclidean distance)
  float min_dist = 1e9f;
  int nearest = 0;
  for (int k = 0; k < KMEANS_N_CLUSTERS; k++) {
    float dist = 0;
    for (int j = 0; j < N_FEATURES; j++) {
      float d = scaled[j] - KMEANS_CENTROIDS[k][j];
      dist += d * d;
    }
    dist = sqrtf(dist);
    if (dist < min_dist) {
      min_dist = dist;
      nearest = k;
    }
  }

  // Compute anomaly score (normalized 0-1)
  AnomalyResult res;
  res.min_distance = min_dist;
  res.score = fminf(min_dist / MAX_EXPECTED_DIST, 1.0f);
  res.nearest_cluster = nearest;

  if (res.score >= ANOMALY_CRIT_THR)
    res.label = LABEL_CRITICAL;
  else if (res.score >= ANOMALY_WARN_THR)
    res.label = LABEL_WARNING;
  else
    res.label = LABEL_NORMAL;

  return res;
}

// ═══════════════════════════════════════════════════════════════
// WiFi & MQTT
// ═══════════════════════════════════════════════════════════════
void setup_wifi() {
  Serial.print("[WiFi] Connecting to ");
  Serial.println(WIFI_SSID);
  Serial.flush(); // Force output before WiFi draws heavy current
  delay(100);

  WiFi.mode(WIFI_STA);
  WiFi.setTxPower(
      WIFI_POWER_8_5dBm); // Reduce TX power to prevent brownout on USB
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  wifi_connect_start = millis();
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (millis() - wifi_connect_start > 30000) {
      Serial.println("\n[WiFi] FAILED — timeout after 30s. Restarting...");
      ESP.restart();
    }
  }

  Serial.println(" Connected!");
  Serial.print("[WiFi] IP: ");
  Serial.println(WiFi.localIP());
}

void mqtt_callback(char *topic, byte *payload, unsigned int length) {
  // Parse incoming command
  char msg[256];
  int len = min((int)length, 255);
  memcpy(msg, payload, len);
  msg[len] = '\0';

  Serial.print("[MQTT] Command received: ");
  Serial.println(msg);

  StaticJsonDocument<256> doc;
  if (deserializeJson(doc, msg) == DeserializationError::Ok) {
    if (doc.containsKey("relay")) {
      bool cmd = doc["relay"].as<bool>();
      relay_state = cmd;
      digitalWrite(RELAY_PIN, relay_state ? HIGH : LOW);
      Serial.print("[RELAY] Set to: ");
      Serial.println(relay_state ? "ON" : "OFF");

      // Publish confirmation
      StaticJsonDocument<128> ack;
      ack["device"] = DEVICE_ID;
      ack["relay"] = relay_state;
      ack["ts"] = millis();
      char buf[128];
      serializeJson(ack, buf);
      mqtt.publish(TOPIC_STATUS, buf);
    }
  }
}

void mqtt_reconnect() {
  if (mqtt.connected())
    return;
  if (millis() - last_mqtt_reconnect < 5000)
    return; // retry every 5s
  last_mqtt_reconnect = millis();

  Serial.print("[MQTT] Connecting to ");
  Serial.print(MQTT_BROKER);
  Serial.print("...");

  // Connect with Last Will and Testament
  String lwt_topic = String(TOPIC_STATUS);
  String lwt_msg =
      "{\"device\":\"" + String(DEVICE_ID) + "\",\"status\":\"offline\"}";

  bool connected;
  if (strlen(MQTT_USER) > 0) {
    connected = mqtt.connect(DEVICE_ID, MQTT_USER, MQTT_PASS, lwt_topic.c_str(),
                             1, true, lwt_msg.c_str());
  } else {
    connected =
        mqtt.connect(DEVICE_ID, lwt_topic.c_str(), 1, true, lwt_msg.c_str());
  }

  if (connected) {
    Serial.println(" Connected!");
    mqtt.subscribe(TOPIC_COMMAND);

    // Publish birth message
    StaticJsonDocument<256> birth;
    birth["device"] = DEVICE_ID;
    birth["status"] = "online";
    birth["ip"] = WiFi.localIP().toString();
    birth["firmware"] = "stage2-inference-v1.0";
    char buf[256];
    serializeJson(birth, buf);
    mqtt.publish(TOPIC_STATUS, buf, true); // retained
  } else {
    Serial.print(" Failed (rc=");
    Serial.print(mqtt.state());
    Serial.println("). Retry in 5s...");
  }
}

// ═══════════════════════════════════════════════════════════════
// PUBLISH RESULTS
// ═══════════════════════════════════════════════════════════════
void publish_data(const FeatureVector *fv, const AnomalyResult *ar) {
  if (!mqtt.connected())
    return;

  StaticJsonDocument<512> doc;
  doc["device"] = DEVICE_ID;
  doc["ts"] = millis();
  doc["vib_rms"] = round(fv->vib_rms * 10000) / 10000.0;
  doc["vib_peak"] = round(fv->vib_peak * 10000) / 10000.0;
  doc["vib_crest"] = round(fv->vib_crest * 10000) / 10000.0;
  doc["vib_kurt"] = round(fv->vib_kurt * 10000) / 10000.0;
  doc["cur_rms"] = round(fv->cur_rms * 10000) / 10000.0;
  doc["cur_std"] = round(fv->cur_std * 10000) / 10000.0;
  doc["dom_freq"] = round(fv->dom_freq * 100) / 100.0;
  doc["spec_rms"] = round(fv->spec_rms * 10000) / 10000.0;
  doc["spec_cent"] = round(fv->spec_cent * 100) / 100.0;
  doc["band1"] = round(fv->band1 * 100) / 100.0;
  doc["band2"] = round(fv->band2 * 100) / 100.0;
  doc["band3"] = round(fv->band3 * 100) / 100.0;
  doc["anomaly_score"] = round(ar->score * 10000) / 10000.0;
  doc["anomaly_label"] = ar->label;
  doc["min_dist"] = round(ar->min_distance * 100) / 100.0;
  doc["cluster"] = ar->nearest_cluster;
  doc["relay"] = relay_state;
  doc["rssi"] = WiFi.RSSI();

  char payload[512];
  serializeJson(doc, payload);
  mqtt.publish(TOPIC_DATA, payload);

  inference_count++;
}

// ═══════════════════════════════════════════════════════════════
// LED STATUS INDICATOR
// ═══════════════════════════════════════════════════════════════
void update_led() {
  // Normal: slow blink (1Hz), Warning: fast blink (4Hz), Critical: solid ON
  static unsigned long last_toggle = 0;
  static bool led_state = false;
  unsigned long now = millis();

  if (current_label == LABEL_CRITICAL) {
    digitalWrite(LED_PIN, HIGH); // Solid ON
  } else if (current_label == LABEL_WARNING) {
    if (now - last_toggle > 125) { // 4Hz blink
      led_state = !led_state;
      digitalWrite(LED_PIN, led_state);
      last_toggle = now;
    }
  } else {
    if (now - last_toggle > 500) { // 1Hz blink
      led_state = !led_state;
      digitalWrite(LED_PIN, led_state);
      last_toggle = now;
    }
  }
}

// ═══════════════════════════════════════════════════════════════
// SETUP
// ═══════════════════════════════════════════════════════════════
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("════════════════════════════════════════════");
  Serial.println("  HVAC Fan — Stage 2 Inference Engine");
  Serial.println("════════════════════════════════════════════");

  // GPIO setup
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // Fan ON by default
  digitalWrite(LED_PIN, LOW);

  // I2C + MPU6050
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  Serial.print("[INIT] MPU6050... ");
  if (!mpu.begin(0x68, &Wire)) {
    Serial.println("FAILED!");
    Serial.println("[ERROR] MPU6050 not found. Check wiring.");
    while (1) {
      delay(1000);
    }
  }
  Serial.println("OK!");

  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_44_HZ);

  // ADC
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  Serial.println("[INIT] ADC on GPIO 34... OK!");

  // WiFi
  setup_wifi();

  // MQTT
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setCallback(mqtt_callback);
  mqtt.setBufferSize(512); // Increase buffer for JSON payloads
  mqtt_reconnect();

  // Initialize buffer
  memset(buf_ax, 0, sizeof(buf_ax));
  memset(buf_ay, 0, sizeof(buf_ay));
  memset(buf_az, 0, sizeof(buf_az));
  memset(buf_cur, 0, sizeof(buf_cur));

  Serial.println("");
  Serial.println("[INFO] Model: K-Means (3 clusters, 12 features)");
  Serial.print("[INFO] WARN threshold:  ");
  Serial.println(ANOMALY_WARN_THR, 4);
  Serial.print("[INFO] CRIT threshold:  ");
  Serial.println(ANOMALY_CRIT_THR, 4);
  Serial.print("[INFO] Max distance:    ");
  Serial.println(MAX_EXPECTED_DIST, 4);
  Serial.println("[INFO] Window: 256 samples (2.56s), Hop: 128 (50% overlap)");
  Serial.println("[INFO] Publishing to: " TOPIC_DATA);
  Serial.println("[INFO] Subscribing to: " TOPIC_COMMAND);
  Serial.println("");
  Serial.println("[RUN] Inference engine started!");
  Serial.println("════════════════════════════════════════════");

  last_sample_us = micros();
}

// ═══════════════════════════════════════════════════════════════
// MAIN LOOP
// ═══════════════════════════════════════════════════════════════
void loop() {
  // Handle MQTT
  if (!mqtt.connected())
    mqtt_reconnect();
  mqtt.loop();

  // Update LED
  update_led();

  // Sample sensors at 100Hz
  unsigned long now_us = micros();
  if (now_us - last_sample_us >= SAMPLE_PERIOD_US) {
    last_sample_us += SAMPLE_PERIOD_US;

    // Catch up if behind
    if (now_us - last_sample_us > SAMPLE_PERIOD_US * 2) {
      last_sample_us = now_us;
    }

    // Read MPU6050
    sensors_event_t accel, gyro, temp;
    mpu.getEvent(&accel, &gyro, &temp);

    // Read ACS712 (4-sample average)
    int current_raw = 0;
    for (int i = 0; i < 4; i++)
      current_raw += analogRead(CURRENT_ADC_PIN);
    current_raw /= 4;

    // Store in circular buffer
    buf_ax[buf_idx] = accel.acceleration.x;
    buf_ay[buf_idx] = accel.acceleration.y;
    buf_az[buf_idx] = accel.acceleration.z;
    buf_cur[buf_idx] = (float)current_raw;
    buf_idx = (buf_idx + 1) % WINDOW_SIZE;
    samples_collected++;

    // Check if we have a full window and it's time for inference
    if (samples_collected >= WINDOW_SIZE &&
        (samples_collected - WINDOW_SIZE) % HOP_SIZE == 0) {

      // Reorder circular buffer into linear arrays for feature extraction
      // (The buffer is circular, so we need to unwrap it)
      static float linear_ax[WINDOW_SIZE],
          linear_ay[WINDOW_SIZE]; // static: stack overflow fix
      static float linear_az[WINDOW_SIZE], linear_cur[WINDOW_SIZE];
      for (int i = 0; i < WINDOW_SIZE; i++) {
        int idx = (buf_idx + i) % WINDOW_SIZE;
        linear_ax[i] = buf_ax[idx];
        linear_ay[i] = buf_ay[idx];
        linear_az[i] = buf_az[idx];
        linear_cur[i] = buf_cur[idx];
      }

      // Copy linearized data back (feature extraction reads from buf_*)
      memcpy(buf_ax, linear_ax, sizeof(buf_ax));
      memcpy(buf_ay, linear_ay, sizeof(buf_ay));
      memcpy(buf_az, linear_az, sizeof(buf_az));
      memcpy(buf_cur, linear_cur, sizeof(buf_cur));
      buf_idx = 0;

      // ─── FEATURE EXTRACTION ─────────────────────────────
      FeatureVector fv;
      unsigned long t0 = micros();
      extract_features(&fv);
      unsigned long t_feat = micros() - t0;

      // ─── K-MEANS INFERENCE ──────────────────────────────
      AnomalyResult ar = kmeans_infer(&fv);
      unsigned long t_total = micros() - t0;

      current_label = ar.label;
      current_score = ar.score;

      // ─── AUTO-SHUTDOWN on CRITICAL ──────────────────────
      if (ar.label == LABEL_CRITICAL && relay_state) {
        relay_state = false;
        digitalWrite(RELAY_PIN, LOW);
        Serial.println("[ALERT] ⚠ CRITICAL ANOMALY — Auto-shutdown triggered!");
      }
      // ─── AUTO-RECOVERY when back to NORMAL ───────────────
      if (ar.label == LABEL_NORMAL && !relay_state) {
        relay_state = true;
        digitalWrite(RELAY_PIN, HIGH);
        Serial.println("[RECOVERY] ✅ Back to NORMAL — Fan re-enabled.");
      }

      // ─── PUBLISH to MQTT ────────────────────────────────
      publish_data(&fv, &ar);

      // ─── Serial Debug Output ────────────────────────────
      const char *labels[] = {"NORMAL", "WARNING", "CRITICAL"};
      Serial.printf("[INF #%lu] Score=%.4f Label=%s Dist=%.2f Cluster=%d "
                    "Feat=%luus Total=%luus\n",
                    inference_count, ar.score, labels[ar.label],
                    ar.min_distance, ar.nearest_cluster, t_feat, t_total);

      // One-time diagnostic: print all features on first 3 inferences
      if (inference_count <= 3) {
        const char *fnames[] = {"vib_rms",  "vib_peak", "vib_crest",
                                "vib_kurt", "cur_rms",  "cur_std",
                                "dom_freq", "spec_rms", "spec_cent",
                                "band1",    "band2",    "band3"};
        float raw_vals[] = {fv.vib_rms,  fv.vib_peak, fv.vib_crest,
                            fv.vib_kurt, fv.cur_rms,  fv.cur_std,
                            fv.dom_freq, fv.spec_rms, fv.spec_cent,
                            fv.band1,    fv.band2,    fv.band3};
        Serial.println(
            "[DIAG] Feature comparison (raw | mean | scaled | centroid_dist):");
        int nc = ar.nearest_cluster;
        for (int j = 0; j < 12; j++) {
          float scaled =
              (raw_vals[j] - SCALER_MEAN[j]) / (SCALER_SCALE[j] + 1e-9f);
          float cdist = scaled - KMEANS_CENTROIDS[nc][j];
          Serial.printf("  %10s: raw=%10.4f mean=%10.4f scaled=%8.2f "
                        "cent=%8.2f gap=%8.2f\n",
                        fnames[j], raw_vals[j], SCALER_MEAN[j], scaled,
                        KMEANS_CENTROIDS[nc][j], cdist);
        }
      }
    }
  }

  // WiFi reconnect check
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[WiFi] Disconnected! Reconnecting...");
    setup_wifi();
  }
}
