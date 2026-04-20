# 🚀 IoT Docker Project – Real-Time Sensor Monitoring with Grafana

## 📌 Overview

This project demonstrates a complete **IoT data pipeline** using Docker-based services:

* 📡 MQTT (Mosquitto) → Data ingestion
* ⚙️ Node-RED → Data processing
* 🗄️ InfluxDB → Time-series database
* 📊 Grafana → Real-time visualization

The system simulates sensor data (e.g., MPU6050) and displays it live on a dashboard.

---

## 🏗️ Architecture

```
Sensor / Docker Script
        ↓
     MQTT (Mosquitto)
        ↓
     Node-RED
        ↓
     InfluxDB (v2)
        ↓
     Grafana Dashboard
```

---

## 🐳 Docker Setup

### 📁 docker-compose.yml

```yaml
version: '3.8'

services:
  mosquitto:
    image: eclipse-mosquitto:2.0
    container_name: mosquitto
    restart: always
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto/config:/mosquitto/config
      - ./mosquitto/data:/mosquitto/data
      - ./mosquitto/log:/mosquitto/log
    networks:
      - iot-network

  nodered:
    image: nodered/node-red:latest
    container_name: nodered
    restart: always
    ports:
      - "1880:1880"
    volumes:
      - ./nodered:/data
    depends_on:
      - mosquitto
      - influxdb
    networks:
      - iot-network

  influxdb:
    image: influxdb:2.7
    container_name: influxdb
    restart: always
    ports:
      - "8086:8086"
    volumes:
      - ./influxdb:/var/lib/influxdb2
    networks:
      - iot-network

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: always
    ports:
      - "3000:3000"
    networks:
      - iot-network

networks:
  iot-network:
    driver: bridge
```

---

## ▶️ Run the Project

```bash
docker-compose up -d
```

---

## 🌐 Access Services

| Service  | URL                   |
| -------- | --------------------- |
| Node-RED | http://localhost:1880 |
| InfluxDB | http://localhost:8086 |
| Grafana  | http://localhost:3000 |

---

## 🔑 Default Credentials

### Grafana

```
username: admin
password: admin
```

---

## ⚙️ Node-RED Flow

### MQTT Input → JSON → Function → InfluxDB

### Function Node Code:

```javascript
msg.payload = [
  {
    measurement: "mpu6050",
    fields: {
      x: Number(msg.payload.x),
      y: Number(msg.payload.y),
      z: Number(msg.payload.z)
    }
  }
];
return msg;
```

---

## 📡 Send Test Data (Docker)

### One-time test:

```bash
docker exec -it mosquitto mosquitto_pub -h localhost -t test/topic -m "{\"x\":50,\"y\":60,\"z\":70}"
```

### Continuous data (inside container):

```bash
docker exec -it mosquitto sh
```

Then:

```sh
while true; do
  mosquitto_pub -h localhost -t test/topic -m "{\"x\":$((RANDOM%100)),\"y\":$((RANDOM%100)),\"z\":$((RANDOM%100))}";
  sleep 2;
done
```

---

## 🗄️ InfluxDB Setup

* Create bucket: `final`
* Organization: `iot-org`
* Generate API Token
* Use token in Node-RED & Grafana

---

## 📊 Grafana Setup

### Add Data Source:

* Type: InfluxDB
* URL: `http://influxdb:8086`
* Organization: `iot-org`
* Bucket: `final`
* Token: (your generated token)

---

## 📈 Dashboard Query (Flux)

```flux
from(bucket: "final")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "mpu6050")
  |> filter(fn: (r) => r._field == "x" or r._field == "y" or r._field == "z")
  |> aggregateWindow(every: 5s, fn: mean)
```

---

## 🎯 Features

* ✅ Real-time data streaming
* ✅ Time-series storage
* ✅ Live dashboard visualization
* ✅ Docker-based deployment
* ✅ Scalable IoT architecture

---

## ⚠️ Common Issues & Fixes

| Issue                    | Fix                             |
| ------------------------ | ------------------------------- |
| NaN values               | Convert to Number() in Node-RED |
| No data in Grafana       | Check time range                |
| String error in InfluxDB | Ensure numeric fields           |
| MQTT not receiving       | Check topic name                |

---

## 🚀 Future Improvements

* Add real sensor (ESP32 / MPU6050)
* Alerts in Grafana
* Mobile dashboard
* Data analytics & ML

---

## 👨‍💻 Author

**Chalaka Perera**

---

## 📜 License

This project is for docker networking and containerized part of the project.
