#pragma once
#include <Arduino.h>

class RelayController {
private:
    int pin;
public:
    RelayController(int relayPin) : pin(relayPin) {}

    void setup() {
        pinMode(pin, OUTPUT);
        digitalWrite(pin, LOW);
        Serial.println("RelayController initialized");
    }

    void turnOn() {
        digitalWrite(pin, HIGH);
        Serial.println("Fan turned ON");
    }

    void turnOff() {
        digitalWrite(pin, LOW);
        Serial.println("Fan turned OFF");
    }
};
