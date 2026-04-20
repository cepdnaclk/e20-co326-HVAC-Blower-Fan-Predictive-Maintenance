#include <WiFi.h>
#include <PubSubClient.h>

// 1. Your WiFi Credentials
const char* ssid = "DialogTharindu4g";
const char* password = "g2dM273d";

// 2. Your Windows PC IP Address (Find using 'ipconfig' in CMD)
const char* mqtt_server = "192.168.8.100"; 

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("WiFi connected");
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP32Client")) {
      Serial.println("Connected to Mosquitto");
    } else {
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  // Simulate MPU6050 data
  int x = random(0, 100);
  int y = random(0, 100);
  int z = random(0, 100);

  // Create JSON string
  String payload = "{\"x\":" + String(x) + ",\"y\":" + String(y) + ",\"z\":" + String(z) + "}";
  
  // Publish to the topic Node-RED is listening to
  client.publish("test/topic", payload.c_str());
  
  Serial.println("Sent: " + payload);
  delay(2000); // Send data every 2 seconds
}