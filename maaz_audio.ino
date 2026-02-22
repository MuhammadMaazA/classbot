#include <Wire.h>
#include <Adafruit_AHTX0.h>
#include <Adafruit_BMP280.h>
#include "driver/i2s.h"
#include "audio.h"
#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include <SPI.h>
#include <WiFi.h>
#include <time.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

// ── Pins ──────────────────────────────────────────────
#define LDR_PIN     14
#define MIC_PIN     13
#define BUZZER_PIN  12
#define I2S_DOUT     4
#define I2S_BCLK     5
#define I2S_LRC      6
#define TFT_CS      38
#define TFT_RST     39
#define TFT_DC      40
#define TFT_MOSI    41
#define TFT_CLK     42

// ── Colors ────────────────────────────────────────────
#define BLACK   0x0000
#define WHITE   0xFFFF
#define CYAN    0x07FF
#define YELLOW  0xFFE0
#define GREEN   0x07E0
#define RED     0xF800
#define ORANGE  0xFD20

// ── WiFi & Backend ────────────────────────────────────
#define WIFI_SSID    "iPhone"
#define WIFI_PASS    "hacklondon"
#define BACKEND_URL  "https://classbot-pxae.onrender.com/api/data"

// ── Alert thresholds ──────────────────────────────────
#define TEMP_MAX    35.0
#define TEMP_MIN    10.0
#define HUM_MAX     80.0
#define HUM_MIN     20.0
#define LIGHT_MIN   5
#define NOISE_MAX   3500

// ── Objects ───────────────────────────────────────────
TwoWire I2C_0 = TwoWire(0);
TwoWire I2C_1 = TwoWire(1);
Adafruit_AHTX0   aht;
Adafruit_BMP280  bmp(&I2C_1);
Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_MOSI, TFT_CLK, TFT_RST);

// ── Buzzer ────────────────────────────────────────────
void alertBuzzer(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(100);
    digitalWrite(BUZZER_PIN, LOW);
    delay(100);
  }
}

// ── Audio ─────────────────────────────────────────────
uint32_t findDataOffset() {
  const uint8_t* wav = (const uint8_t*)ElevenLabs_2026_02_21T23_18_57_Christina_Natural_and_Conversational_pvc_sp81_s100_sb75_se30_b_m2_1_;
  for (uint32_t i = 12; i < 212046 - 8; i++) {
    if (wav[i]=='d' && wav[i+1]=='a' && wav[i+2]=='t' && wav[i+3]=='a')
      return i + 8;
  }
  return 44;
}

void playAudio() {
  uint32_t offset      = findDataOffset();
  const uint8_t* audio = (const uint8_t*)ElevenLabs_2026_02_21T23_18_57_Christina_Natural_and_Conversational_pvc_sp81_s100_sb75_se30_b_m2_1_ + offset;
  uint32_t len         = 212046 - offset;
  size_t   written;
  for (uint32_t i = 0; i < len; i += 1024) {
    uint32_t chunk = min((uint32_t)1024, len - i);
    i2s_write(I2S_NUM_0, audio + i, chunk, &written, portMAX_DELAY);
  }
}

// ── TFT ───────────────────────────────────────────────
void drawLayout() {
  tft.fillScreen(BLACK);
  tft.fillRect(0, 0, 320, 36, CYAN);
  tft.setTextColor(BLACK);
  tft.setTextSize(2);
  tft.setCursor(60, 10);
  tft.print("SENSOR DASHBOARD");

  tft.fillRect(0, 40,  320, 38, 0x1082);
  tft.fillRect(0, 80,  320, 38, BLACK);
  tft.fillRect(0, 120, 320, 38, 0x1082);
  tft.fillRect(0, 160, 320, 38, BLACK);
  tft.fillRect(0, 200, 320, 38, 0x1082);

  tft.setTextSize(2);
  tft.setTextColor(YELLOW);
  tft.setCursor(8, 50);  tft.print("Time:");
  tft.setCursor(8, 90);  tft.print("Temp:");
  tft.setCursor(8, 130); tft.print("Humidity:");
  tft.setCursor(8, 170); tft.print("Light:");
  tft.setCursor(8, 210); tft.print("Noise:");
}

void updateValue(int y, String value, uint16_t color) {
  tft.fillRect(180, y, 136, 28, (y == 40 || y == 120 || y == 200) ? 0x1082 : BLACK);
  tft.setTextColor(color);
  tft.setTextSize(2);
  tft.setCursor(185, y + 5);
  tft.print(value);
}

// ── Backend POST ──────────────────────────────────────
void postToBackend(float temp, float humidity, int light, int noise, bool alert, String alertMsg, char* timeStr) {
  if (WiFi.status() != WL_CONNECTED) return;
  WiFiClientSecure client;
  client.setInsecure();
  HTTPClient http;
  http.begin(client, BACKEND_URL);
  http.setTimeout(30000);
  http.addHeader("Content-Type", "application/json");
  String json = "{";
  json += "\"time\":\"" + String(timeStr) + "\",";
  json += "\"temp\":" + String(temp, 1) + ",";
  json += "\"humidity\":" + String(humidity, 1) + ",";
  json += "\"light\":" + String(light) + ",";
  json += "\"noise\":" + String(noise) + ",";
  json += "\"alert\":" + String(alert ? "true" : "false") + ",";
  json += "\"alertMsg\":\"" + alertMsg + "\"";
  json += "}";
  int code = http.POST(json);
  Serial.printf("Backend POST: %d\n", code);
  http.end();
}

// ── Setup ─────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(1000);
  pinMode(BUZZER_PIN, OUTPUT);

  I2C_0.begin(20, 21);
  I2C_1.begin(8, 9);

  if (!aht.begin(&I2C_1)) Serial.println("AHT20 not found!");
  if (!bmp.begin(0x77))   Serial.println("BMP280 not found!");

  tft.begin();
  tft.setRotation(1);
  drawLayout();

  // WiFi
  tft.setTextColor(GREEN);
  tft.setTextSize(2);
  tft.setCursor(8, 130);
  tft.print("Connecting WiFi...");
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 20) {
    delay(500);
    Serial.print(".");
    tries++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    configTime(0, 0, "pool.ntp.org", "time.google.com");
    setenv("TZ", "GMT0BST,M3.5.0/1,M10.5.0", 1);
    tzset();
    delay(2000); // wait for NTP sync
    Serial.println("NTP synced");
  } else {
    Serial.println("\nWiFi failed!");
  }

  // I2S
  i2s_config_t cfg = {
    .mode                 = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
    .sample_rate          = 44100,
    .bits_per_sample      = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format       = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags     = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count        = 8,
    .dma_buf_len          = 512,
    .use_apll             = false,
    .tx_desc_auto_clear   = true
  };
  i2s_driver_install(I2S_NUM_0, &cfg, 0, NULL);
  i2s_pin_config_t pins = {
    .bck_io_num   = I2S_BCLK,
    .ws_io_num    = I2S_LRC,
    .data_out_num = I2S_DOUT,
    .data_in_num  = I2S_PIN_NO_CHANGE
  };
  i2s_set_pin(I2S_NUM_0, &pins);
  i2s_zero_dma_buffer(I2S_NUM_0);

  playAudio();
  drawLayout();
}

// ── Loop ──────────────────────────────────────────────
void loop() {
  // Time
  struct tm timeinfo;
  char timeOnly[9] = "00:00:00";
  if (getLocalTime(&timeinfo)) {
    sprintf(timeOnly, "%02d:%02d:%02d",
      timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec);
  }

  // Sensors
  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);
  float t = temp.temperature;
  float h = humidity.relative_humidity;
  int lightLevel = analogRead(LDR_PIN);
  int soundLevel = analogRead(MIC_PIN);

  // Alerts
  bool alert = false;
  String alertMsg = "";
  if      (t > TEMP_MAX)          { alert = true; alertMsg = "TEMP HIGH!"; }
  else if (t < TEMP_MIN)          { alert = true; alertMsg = "TEMP LOW!"; }
  else if (h > HUM_MAX)           { alert = true; alertMsg = "HUM HIGH!"; }
  else if (h < HUM_MIN)           { alert = true; alertMsg = "HUM LOW!"; }
  else if (lightLevel < LIGHT_MIN) { alert = true; alertMsg = "TOO DARK!"; }
  else if (soundLevel > NOISE_MAX) { alert = true; alertMsg = "TOO LOUD!"; }

  if (alert) {
    alertBuzzer(3);
    tft.fillRect(0, 242, 320, 38, RED);
    tft.setTextColor(WHITE);
    tft.setTextSize(2);
    tft.setCursor(8, 254);
    tft.print("!! " + alertMsg);
  } else {
    tft.fillRect(0, 242, 320, 38, BLACK);
    digitalWrite(BUZZER_PIN, HIGH);
    delay(50);
    digitalWrite(BUZZER_PIN, LOW);
  }

  // Update TFT
  updateValue(40,  String(timeOnly),      WHITE);
  updateValue(80,  String(t, 1) + " C",   alert && (t > TEMP_MAX || t < TEMP_MIN) ? RED : ORANGE);
  updateValue(120, String(h, 1) + " %",   alert && (h > HUM_MAX  || h < HUM_MIN)  ? RED : CYAN);
  updateValue(160, String(lightLevel),     alert && lightLevel < LIGHT_MIN ? RED : YELLOW);
  updateValue(200, String(soundLevel),     alert && soundLevel > NOISE_MAX ? RED : GREEN);

  // Serial
  Serial.printf("%s | %.1fC | %.1f%% | Light:%d | Noise:%d%s\n",
    timeOnly, t, h, lightLevel, soundLevel,
    alert ? (" !! " + alertMsg).c_str() : "");

  // Post to backend
  postToBackend(t, h, lightLevel, soundLevel, alert, alertMsg, timeOnly);
}