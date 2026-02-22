/*
 * Classroom Sensor Integration - Modified for Local Dashboard
 * Posts sensor data directly to Raspberry Pi dashboard
 * 
 * Connect to same network as Pi and update DASHBOARD_IP below
 */

#include <Wire.h>
#include <Adafruit_AHTX0.h>
#include <Adafruit_BMP280.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ── WiFi & Dashboard ──────────────────────────────────
#define WIFI_SSID       "YOUR_WIFI_SSID"  // Change this
#define WIFI_PASS       "YOUR_WIFI_PASS"  // Change this
#define DASHBOARD_IP    "192.168.137.60"  // Your Pi's IP
#define DASHBOARD_PORT  5000

// ── Pins ──────────────────────────────────────────────
#define LDR_PIN     14
#define MIC_PIN     13

// ── Sensors ───────────────────────────────────────────
TwoWire I2C_1 = TwoWire(1);
Adafruit_AHTX0  aht;
Adafruit_BMP280 bmp(&I2C_1);

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // Initialize I2C
  I2C_1.begin(8, 9);
  
  // Initialize sensors
  if (!aht.begin(&I2C_1)) {
    Serial.println("❌ AHT20 not found!");
  } else {
    Serial.println("✓ AHT20 ready");
  }
  
  if (!bmp.begin(0x77)) {
    Serial.println("❌ BMP280 not found!");
  } else {
    Serial.println("✓ BMP280 ready");
  }
  
  // Connect to WiFi
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 20) {
    delay(500);
    Serial.print(".");
    tries++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi connected!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ WiFi failed!");
  }
}

void loop() {
  // Read sensors
  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);
  
  float temperature = temp.temperature;
  float humidityVal = humidity.relative_humidity;
  int lightLevel = analogRead(LDR_PIN);
  int noiseLevel = analogRead(MIC_PIN);
  
  // Convert noise to dB estimate (rough approximation)
  float noise_db = map(noiseLevel, 0, 4095, 30, 90);
  
  // Convert light to lux estimate (calibrate for your LDR)
  float light_lux = map(lightLevel, 0, 4095, 0, 1000);
  
  // Print to serial
  Serial.printf("Temp: %.1f°C | Humidity: %.1f%% | Light: %.0f lux | Noise: %.0f dB\n",
                temperature, humidityVal, light_lux, noise_db);
  
  // Post to dashboard
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = "http://" + String(DASHBOARD_IP) + ":" + String(DASHBOARD_PORT) + "/api/sensors/update";
    
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    
    // Format: {"temperature": 23.5, "humidity": 45, "noise_level": 55, "light_level": 500}
    String json = "{";
    json += "\"temperature\":" + String(temperature, 1) + ",";
    json += "\"humidity\":" + String(humidityVal, 1) + ",";
    json += "\"noise_level\":" + String(noise_db, 1) + ",";
    json += "\"light_level\":" + String(light_lux, 0);
    json += "}";
    
    int httpCode = http.POST(json);
    
    if (httpCode > 0) {
      Serial.printf("✓ Dashboard updated (HTTP %d)\n", httpCode);
    } else {
      Serial.printf("❌ POST failed: %s\n", http.errorToString(httpCode).c_str());
    }
    
    http.end();
  } else {
    Serial.println("❌ WiFi not connected");
  }
  
  delay(5000);  // Update every 5 seconds
}
