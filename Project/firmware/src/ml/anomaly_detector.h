#pragma once
#include <Arduino.h>
#include <math.h>

class AnomalyDetector {
private:
    float centroid_vib = 1.2f;
    float centroid_curr = 2.5f;

public:
    void setup() {
        Serial.println("AnomalyDetector initialized");
    }

    float computeAnomalyScore(float vib, float curr) {
        // Euclidean distance from normal centroid
        float d_vib = vib - centroid_vib;
        float d_curr = curr - centroid_curr;
        return sqrt((d_vib * d_vib) + (d_curr * d_curr));
    }
};
