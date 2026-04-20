#pragma once
#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

class MqttManager {
private:
    const char* ssid;
    const char* password;
    const char* mqtt_server;
    int mqtt_port;
    WiFiClient espClient;
    PubSubClient client;

    void reconnect() {
        while (!client.connected()) {
            Serial.print("Attempting MQTT connection...");
            if (client.connect("ESP32Client")) {
                Serial.println("connected");
                client.subscribe("hvac_fan01/cmd/relay");
            } else {
                Serial.print("failed, rc=");
                Serial.print(client.state());
                Serial.println(" try again in 5 seconds");
                delay(5000);
            }
        }
    }

public:
    MqttManager(const char* ssid, const char* password, const char* server, int port)
        : ssid(ssid), password(password), mqtt_server(server), mqtt_port(port), client(espClient) {}

    void setup() {
        Serial.print("Connecting to WiFi...");
        WiFi.begin(ssid, password);
        while (WiFi.status() != WL_CONNECTED) {
            delay(500);
            Serial.print(".");
        }
        Serial.println("Connected!");

        client.setServer(mqtt_server, mqtt_port);
    }

    void loop() {
        if (!client.connected()) {
            reconnect();
        }
        client.loop();
    }

    void publish(const char* topic, const char* payload) {
        if (client.connected()) {
            client.publish(topic, payload);
        }
    }
    
    void setCallback(MQTT_CALLBACK_SIGNATURE) {
        client.setCallback(callback);
    }
};
