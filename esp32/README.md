# 📟 ESP8266/ESP32 Firmware Module

## Overview

The **ESP8266/ESP32 Firmware** serves as the hardware control layer of the Emotion Responsive Smart Home system.

It:

- 📶 Connects to the local WiFi network
- 🔄 Polls the Middleware Server every 800ms
- 📥 Retrieves the latest device states
- 💡 Controls onboard LED status
- 🌈 Controls RGB LED lighting
- 💨 Controls fan speed using PWM
- 📊 Provides serial debugging output

The firmware continuously requests the latest commands from the Middleware Server and applies them to connected hardware devices.

---

## Architecture

```text
┌─────────────────────────────────────────────┐
│          ESP8266 / ESP32 Firmware           │
├─────────────────────────────────────────────┤
│                                             │
│  WiFi Manager                               │
│      │                                      │
│      ▼                                      │
│  Connect to Local Network                   │
│      │                                      │
│      ▼                                      │
│  HTTP Client                                │
│      │                                      │
│      ▼                                      │
│  GET /get_command (Every 800ms)             │
│      │                                      │
│      ▼                                      │
│  JSON Parser (ArduinoJson)                  │
│      │                                      │
│      ├──────────────► LED Controller        │
│      ├──────────────► RGB Controller        │
│      └──────────────► Fan Controller        │
│                                             │
└─────────────────────────────────────────────┘
                    │
                    ▼
           Middleware Server
```

---

## Hardware Connections

### Pin Configuration

| Device | GPIO | ESP8266 Pin | Function |
|----------|--------|------------|-----------|
| Onboard LED | GPIO2 | D4 | Digital Output |
| RGB Red | GPIO12 | D6 | PWM Output |
| RGB Green | GPIO13 | D7 | PWM Output |
| RGB Blue | GPIO15 | D8 | PWM Output |
| Fan | GPIO5 | D1 | PWM Output |

---

## Required Libraries

```cpp
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>
```

Install ArduinoJson from the Arduino Library Manager.

---

## Network Configuration

### WiFi Credentials

```cpp
const char* ssid = "mos";
const char* password = "123456789";
```

### Middleware Server

```cpp
const char* serverUrl =
"http://192.168.37.165:8000/get_command";
```

Update the IP address if your server is running on another machine.

---

## Startup Sequence

### Initialize Serial Communication

```cpp
Serial.begin(115200);
```

### Configure GPIO Pins

```cpp
pinMode(LED_PIN, OUTPUT);
pinMode(R_PIN, OUTPUT);
pinMode(G_PIN, OUTPUT);
pinMode(B_PIN, OUTPUT);
pinMode(FAN_PIN, OUTPUT);
```

### Set Default States

```cpp
digitalWrite(LED_PIN, HIGH);
analogWrite(R_PIN, 0);
analogWrite(G_PIN, 0);
analogWrite(B_PIN, 0);
analogWrite(FAN_PIN, 0);
```

All devices start in the OFF state.

### Connect to WiFi

```cpp
connectToWiFi();
```

---

## Communication Flow

### Polling Interval

```cpp
delay(800);
```

The ESP8266 polls the Middleware Server every **800ms**.

### Request

```http
GET /get_command
```

Example:

```http
GET http://192.168.37.165:8000/get_command
```

### Response

```json
{
  "led": {
    "device": "led",
    "action": "on"
  },
  "rgb": {
    "device": "rgb",
    "r": 255,
    "g": 0,
    "b": 0
  },
  "fan": {
    "device": "fan",
    "speed": 200
  }
}
```

---

## Device Control Logic

### LED Control

The onboard LED uses **active LOW logic**.

| Command | GPIO State |
|----------|------------|
| on | LOW |
| off | HIGH |

Example:

```json
{
  "device": "led",
  "action": "on"
}
```

---

### RGB LED Control

Example Command:

```json
{
  "device": "rgb",
  "r": 255,
  "g": 0,
  "b": 0
}
```

Firmware:

```cpp
analogWrite(R_PIN, 255);
analogWrite(G_PIN, 0);
analogWrite(B_PIN, 0);
```

Result:

```text
RGB LED = RED
```

---

### Fan Control

Example:

```json
{
  "device": "fan",
  "speed": 200
}
```

Firmware:

```cpp
analogWrite(FAN_PIN, 200);
```

### Speed Levels

| PWM Value | Level |
|------------|--------|
| 0 | OFF |
| 1-64 | LOW |
| 65-128 | MEDIUM |
| 129-200 | HIGH |
| 201-255 | MAX |

---

## JSON Processing

### Parse JSON

```cpp
StaticJsonDocument<512> doc;
deserializeJson(doc, payload);
```

### Read LED State

```cpp
const char* ledAction =
doc["led"]["action"];
```

### Read RGB Values

```cpp
int r = doc["rgb"]["r"] | 0;
int g = doc["rgb"]["g"] | 0;
int b = doc["rgb"]["b"] | 0;
```

### Read Fan Speed

```cpp
int speed = doc["fan"]["speed"] | 0;
```

---

## Serial Monitor Output

### Successful Startup

```text
========================================
Emotion Smart Home - ESP8266 Firmware
========================================

Connecting to WiFi: mos
........

✓ Connected to WiFi!
IP Address: 192.168.37.200
```

### Device Update

```text
[Polling] Fetching device states...

🔴 LED: on
🌈 RGB: R=255, G=0, B=0
💨 FAN: Speed=200 (HIGH)
```

---

## Installation

### 1. Install ESP8266 Board Package

Arduino IDE:

```text
File → Preferences
Additional Board Manager URLs:
http://arduino.esp8266.com/stable/package_esp8266com_index.json
```

### 2. Select Board

```text
Tools → Board → NodeMCU 1.0 (ESP-12E Module)
```

### 3. Select COM Port

```text
Tools → Port → COMx
```

### 4. Upload Firmware

```text
Sketch → Upload
```

### 5. Open Serial Monitor

```text
115200 Baud
```

---

## Troubleshooting

### WiFi Connection Failed

Check:

- Correct SSID
- Correct password
- Router is online
- ESP8266 is within range

### Cannot Reach Server

Verify:

```bash
curl http://192.168.37.165:8000/ping
```

Expected:

```json
{
  "status": "alive"
}
```

### JSON Parse Failed

Verify:

- Server returns valid JSON
- JSON size is under 512 bytes
- Network connection is stable

### RGB LED Not Working

Check:

- Wiring
- GPIO assignments
- Shared GND connection
- PWM support

### Fan Not Responding

Check:

- PWM pin connection
- Driver transistor/MOSFET
- External power supply

---

## Performance

| Metric | Value |
|----------|---------|
| Poll Interval | 800 ms |
| Request Rate | 1.25/sec |
| JSON Buffer | 512 bytes |
| Baud Rate | 115200 |
| Memory Usage | Low |
| Typical Latency | < 1 second |

---

## Future Improvements

- MQTT communication
- WebSocket support
- OTA firmware updates
- Automatic WiFi reconnection
- Device status reporting
- HTTPS support
- Sensor feedback integration

---

## License

MIT License - See repository for details.

---

## Author

Jonathan-XO - ESP8266/ESP32 Firmware Module

Part of the Emotion-Responsive Smart Home Project

---

For more details, see:

- `ARCHITECTURE.md`
- `server.md`
- `AI_ASSISTANT.md`
- `TROUBLESHOOTING.md`
