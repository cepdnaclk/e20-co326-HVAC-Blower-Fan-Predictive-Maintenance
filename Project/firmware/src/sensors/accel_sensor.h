#pragma once
#include <Arduino.h>

class AccelSensor {
public:
    void setup() {
        Serial.println("AccelSensor initialized");
    }

    float getRMSVibration() {
        // Stub implementation
        return 1.2f + (random(-10, 10) / 100.0f);
    }
};
