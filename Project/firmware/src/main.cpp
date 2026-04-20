#include <Arduino.h>
#include <ArduinoJson.h>
#include "comms/mqtt_manager.h"
#include "sensors/accel_sensor.h"
#include "sensors/current_sensor.h"
#include "control/relay_controller.h"
#include "ml/anomaly_detector.h"

MqttManager mqtt("WIFI_SSID", "WIFI_PASSWORD", "192.168.1.100", 1883);
AccelSensor accel;
CurrentSensor currentSense;
RelayController relay(5);
AnomalyDetector detector;

unsigned long lastMsg = 0;

void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    String message;
    for (unsigned int i = 0; i < length; i++) {
        message += (char)payload[i];
    }
    Serial.println(message);

    if (String(topic) == "hvac_fan01/cmd/relay") {
        if (message == "ON") {
            relay.turnOn();
        } else if (message == "OFF") {
            relay.turnOff();
        }
    }
}

void setup() {
    Serial.begin(115200);
    mqtt.setup();
    mqtt.setCallback(callback);
    
    accel.setup();
    currentSense.setup();
    relay.setup();
}

void loop() {
    mqtt.loop();

    unsigned long now = millis();
    if (now - lastMsg > 2000) {
        lastMsg = now;
        
        float vib = accel.getRMSVibration();
        float curr = currentSense.getRMSCurrent();
        float anomalyScore = detector.computeAnomalyScore(vib, curr);
        
        StaticJsonDocument<200> doc;
        doc["vibration"] = vib;
        doc["current"] = curr;
        doc["anomaly_score"] = anomalyScore;
        
        char jsonBuffer[512];
        serializeJson(doc, jsonBuffer);
        
        mqtt.publish("hvac_fan01/data/sensors", jsonBuffer);
    }
}
