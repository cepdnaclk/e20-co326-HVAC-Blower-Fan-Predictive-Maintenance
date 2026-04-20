#pragma once
#include <Arduino.h>

class CurrentSensor {
public:
    void setup() {
        Serial.println("CurrentSensor initialized");
    }

    float getRMSCurrent() {
        // Stub implementation
        return 2.5f + (random(-5, 5) / 100.0f);
    }
};
