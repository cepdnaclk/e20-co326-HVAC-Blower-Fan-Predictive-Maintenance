/*
 * HVAC Blower Fan — Stage 1 Data Collector Firmware
 * ==================================================
 * Board:  ESP32 DevKit v1 (WROOM-32)
 * Purpose: Read MPU6050 (vibration) + ACS712 (current) at 100Hz
 *          and print CSV-formatted data over USB Serial.
 *
 * Wiring:
 *   MPU6050 VCC → 3V3      MPU6050 GND → GND
 *   MPU6050 SDA → GPIO 21 (D21)   MPU6050 SCL → GPIO 22 (D22)
 *   ACS712  OUT → GPIO 34 (D34) (via voltage divider if needed)
 *
 * Serial Output Format (at 115200 baud):
 *   DATA:<timestamp_ms>,<ax>,<ay>,<az>,<gx>,<gy>,<gz>,<current_raw>
 */

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>


// ─── Pin Configuration ──────────────────────────────────────────────
#define I2C_SDA_PIN 21     // D21 — default I2C SDA on ESP32 WROOM-32
#define I2C_SCL_PIN 22     // D22 — default I2C SCL on ESP32 WROOM-32
#define CURRENT_ADC_PIN 34 // D34 — ADC1_CH6 (input-only pin)

// ─── Sampling Configuration ─────────────────────────────────────────
#define SAMPLE_RATE_HZ 100 // Target: 100 samples per second
#define SAMPLE_PERIOD_US (1000000 / SAMPLE_RATE_HZ) // 10000 microseconds
#define SERIAL_BAUD 115200

// ─── Globals ────────────────────────────────────────────────────────
Adafruit_MPU6050 mpu;
bool mpu_ready = false;
unsigned long last_sample_time = 0;
unsigned long sample_count = 0;

void setup() {
  // Initialize Serial
  Serial.begin(SERIAL_BAUD);
  while (!Serial) {
    delay(10);
  }

  Serial.println("========================================");
  Serial.println("  HVAC Fan Data Collector — Stage 1");
  Serial.println("========================================");

  // Initialize I2C with custom pins
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);

  // Initialize MPU6050
  Serial.print("[INIT] MPU6050... ");
  if (!mpu.begin(0x68, &Wire)) {
    Serial.println("FAILED!");
    Serial.println("[ERROR] Could not find MPU6050. Check wiring:");
    Serial.println("  - VCC to 3V3");
    Serial.println("  - GND to GND");
    Serial.println("  - SDA to D21 (GPIO 21)");
    Serial.println("  - SCL to D22 (GPIO 22)");
    Serial.println("  - AD0 to GND (address 0x68)");
    while (1) {
      delay(1000);
      Serial.println("[ERROR] MPU6050 not found. Halted.");
    }
  }
  Serial.println("OK!");

  // Configure MPU6050 — optimized for vibration sensing
  mpu.setAccelerometerRange(MPU6050_RANGE_4_G); // ±4g (good for fan vibration)
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);      // ±500 deg/s
  mpu.setFilterBandwidth(MPU6050_BAND_44_HZ); // Low-pass filter to reduce noise

  Serial.println("[INIT] MPU6050 configured:");
  Serial.println("  Accel range: ±4g");
  Serial.println("  Gyro range:  ±500 deg/s");
  Serial.println("  Bandwidth:   44 Hz");

  // Configure ADC for current sensor
  analogReadResolution(12);       // 12-bit ADC (0-4095)
  analogSetAttenuation(ADC_11db); // Full range 0-3.3V

  Serial.print("[INIT] ADC for current sensor on GPIO ");
  Serial.print(CURRENT_ADC_PIN);
  Serial.println("... OK!");

  // Print header info
  Serial.println("");
  Serial.println("[INFO] Sampling at 100 Hz");
  Serial.println("[INFO] Output format: DATA:ts,ax,ay,az,gx,gy,gz,current_raw");
  Serial.println("[INFO] Starting data collection in 3 seconds...");
  Serial.println("");
  delay(3000);

  Serial.println("READY"); // Signal to Python script that we're ready
  last_sample_time = micros();
}

void loop() {
  unsigned long now = micros();

  // Maintain consistent 100Hz sampling rate
  if (now - last_sample_time >= SAMPLE_PERIOD_US) {
    last_sample_time += SAMPLE_PERIOD_US;

    // Catch up if we fell behind (don't accumulate drift)
    if (now - last_sample_time > SAMPLE_PERIOD_US * 2) {
      last_sample_time = now;
    }

    // Read MPU6050
    sensors_event_t accel, gyro, temp;
    mpu.getEvent(&accel, &gyro, &temp);

    // Read ACS712 current sensor (raw ADC value)
    // Averaging 4 rapid readings to reduce ADC noise
    int current_raw = 0;
    for (int i = 0; i < 4; i++) {
      current_raw += analogRead(CURRENT_ADC_PIN);
    }
    current_raw /= 4;

    // Print data line in CSV format
    // Format: DATA:<timestamp_ms>,<ax>,<ay>,<az>,<gx>,<gy>,<gz>,<current_raw>
    Serial.print("DATA:");
    Serial.print(millis());
    Serial.print(",");
    Serial.print(accel.acceleration.x, 4); // 4 decimal places
    Serial.print(",");
    Serial.print(accel.acceleration.y, 4);
    Serial.print(",");
    Serial.print(accel.acceleration.z, 4);
    Serial.print(",");
    Serial.print(gyro.gyro.x, 4);
    Serial.print(",");
    Serial.print(gyro.gyro.y, 4);
    Serial.print(",");
    Serial.print(gyro.gyro.z, 4);
    Serial.print(",");
    Serial.println(current_raw);

    sample_count++;

    // Print progress every 10 seconds (1000 samples)
    if (sample_count % 1000 == 0) {
      Serial.print("# Samples collected: ");
      Serial.print(sample_count);
      Serial.print(" (");
      Serial.print(sample_count / SAMPLE_RATE_HZ);
      Serial.println(" seconds)");
    }
  }
}
