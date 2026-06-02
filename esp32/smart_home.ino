#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

// ============================================================
// EMOTION RESPONSIVE SMART HOME - ESP8266/ESP32 FIRMWARE
// ============================================================
// This firmware:
// - Connects to WiFi
// - Polls middleware server every 800ms
// - Executes device control commands (PWM, digital I/O)
// - Supports RGB LED, Fan, and LED
// ============================================================

const char* ssid = "mos";                                    // Your WiFi SSID
const char* password = "123456789";                          // Your WiFi Password
const char* serverUrl = "http://192.168.37.165:8000/get_command";  // Server URL

// -------- PIN CONFIGURATION --------
const int LED_PIN = 2;   // D4 - Onboard LED (active LOW)
const int R_PIN = 12;    // D6 - Red channel
const int G_PIN = 13;    // D7 - Green channel
const int B_PIN = 15;    // D8 - Blue channel
const int FAN_PIN = 5;   // D1 - Fan speed (PWM)

WiFiClient client;
String lastState = "";

void setup() {
  Serial.begin(115200);
  delay(100);
  
  Serial.println("\n\n");
  Serial.println("========================================");
  Serial.println("Emotion Smart Home - ESP8266 Firmware");
  Serial.println("========================================\n");

  // Initialize pins
  pinMode(LED_PIN, OUTPUT);
  pinMode(R_PIN, OUTPUT);
  pinMode(G_PIN, OUTPUT);
  pinMode(B_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);

  // Set default states (all off)
  digitalWrite(LED_PIN, HIGH);  // LED off (active LOW)
  analogWrite(R_PIN, 0);
  analogWrite(G_PIN, 0);
  analogWrite(B_PIN, 0);
  analogWrite(FAN_PIN, 0);

  // Connect to WiFi
  connectToWiFi();
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ Connected to WiFi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n✗ Failed to connect to WiFi");
  }
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(client, serverUrl);
    
    Serial.println("\n[Polling] Fetching device states...");
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String payload = http.getString();
      payload.trim();
      Serial.println("Response: " + payload);

      // Parse JSON
      StaticJsonDocument<512> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (!error) {
        // -------- LED CONTROL --------
        const char* ledAction = doc["led"]["action"];
        if (ledAction) {
          int ledState = (strcmp(ledAction, "on") == 0) ? LOW : HIGH;  // active LOW
          digitalWrite(LED_PIN, ledState);
          Serial.printf("🔴 LED: %s\n", ledAction);
        }

        // -------- RGB CONTROL --------
        if (doc["rgb"].is<JsonObject>()) {
          int r = doc["rgb"]["r"] | 0;
          int g = doc["rgb"]["g"] | 0;
          int b = doc["rgb"]["b"] | 0;
          analogWrite(R_PIN, r);
          analogWrite(G_PIN, g);
          analogWrite(B_PIN, b);
          Serial.printf("🌈 RGB: R=%d, G=%d, B=%d\n", r, g, b);
        }

        // -------- FAN CONTROL --------
        if (doc["fan"].is<JsonObject>()) {
          int speed = doc["fan"]["speed"] | 0;
          analogWrite(FAN_PIN, speed);
          
          String speedLabel;
          if (speed == 0) speedLabel = "OFF";
          else if (speed <= 64) speedLabel = "LOW";
          else if (speed <= 128) speedLabel = "MEDIUM";
          else if (speed <= 200) speedLabel = "HIGH";
          else speedLabel = "MAX";
          
          Serial.printf("💨 FAN: Speed=%d (%s)\n", speed, speedLabel.c_str());
        }

      } else {
        Serial.println("[ERROR] JSON parse failed!");
      }

    } else {
      Serial.printf("[ERROR] Connection failed: %d\n", httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("[ERROR] WiFi not connected!");
  }

  // Poll interval: 800ms
  delay(800);
}
