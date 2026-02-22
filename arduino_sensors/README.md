# Arduino Environmental Sensors → Dashboard Integration

## Overview

This Arduino code reads environmental sensors and posts data to your Raspberry Pi classroom dashboard in real-time.

## Hardware

**Arduino/ESP32 with:**
- **AHT20** - Temperature & Humidity sensor (I2C)
- **BMP280** - Pressure sensor (optional, I2C)
- **LDR** - Light sensor (analog pin 14)
- **Microphone** - Sound level (analog pin 13)

## How It Works

```
Arduino reads sensors every 5 seconds
    ↓
POST to: http://192.168.137.60:5000/api/sensors/update
    ↓
Dashboard receives and displays in real-time
```

## Setup

### 1. Upload Arduino Code

**Option A: Use simplified version** (recommended)
```
Upload: classroom_sensors_dashboard.ino
```

**Option B: Modify existing code**
Edit your `maaz_audio.ino`:

Change:
```cpp
#define BACKEND_URL "https://classbot-pxae.onrender.com/api/data"
```

To:
```cpp
#define BACKEND_URL "http://192.168.137.60:5000/api/sensors/update"
```

And modify the `postToBackend()` function to match dashboard format:
```cpp
String json = "{";
json += "\"temperature\":" + String(temp, 1) + ",";
json += "\"humidity\":" + String(humidity, 1) + ",";
json += "\"noise_level\":" + String(noise, 1) + ",";
json += "\"light_level\":" + String(light, 0);
json += "}";
```

### 2. Configure WiFi

In the Arduino code, update:
```cpp
#define WIFI_SSID    "YOUR_WIFI_SSID"
#define WIFI_PASS    "YOUR_PASSWORD"
#define DASHBOARD_IP "192.168.137.60"  // Your Pi's IP
```

### 3. Connect to Same Network

⚠️ **IMPORTANT**: Arduino and Pi must be on the same WiFi network!

Check Pi IP:
```bash
hostname -I
```

### 4. Test Connection

After uploading, open Serial Monitor (115200 baud):
```
Connecting to WiFi.....
✓ WiFi connected!
IP: 192.168.1.123
Temp: 23.5°C | Humidity: 45.2% | Light: 487 lux | Noise: 55.3 dB
✓ Dashboard updated (HTTP 200)
```

## Data Format

Arduino sends:
```json
{
  "temperature": 23.5,
  "humidity": 45.2,
  "noise_level": 55.3,
  "light_level": 487
}
```

Dashboard displays all 4 metrics in real-time!

## Calibration

### Light Sensor (LDR)
Adjust the mapping based on your LDR:
```cpp
float light_lux = map(lightLevel, 0, 4095, 0, 1000);
//                                         ↑    ↑
//                                      MIN  MAX lux
```

Test in different lighting conditions and adjust MAX.

### Noise Sensor (Microphone)
Adjust the dB range:
```cpp
float noise_db = map(noiseLevel, 0, 4095, 30, 90);
//                                         ↑   ↑
//                                       MIN MAX dB
```

Test in quiet/loud environments and calibrate.

## Troubleshooting

**"WiFi not connected"**
- Check SSID/password
- Ensure 2.4GHz network (ESP32 doesn't support 5GHz)
- Move closer to router

**"POST failed"**
- Verify Pi IP address: `hostname -I`
- Check dashboard is running: http://192.168.137.60:5000
- Ping Pi from Arduino network to test connectivity

**Sensors reading 0 or NaN**
- Check I2C wiring (SDA/SCL)
- Verify sensor addresses (AHT20: 0x38, BMP280: 0x77)
- Run I2C scanner to detect devices

**Wrong values**
- Calibrate light/noise mapping (see above)
- Check analog reference voltage
- Ensure proper sensor power (3.3V for most I2C sensors)

## Pin Configuration

Current setup:
```
LDR_PIN     = 14 (analog input)
MIC_PIN     = 13 (analog input)
I2C_SDA     = 8
I2C_SCL     = 9
```

Adjust in code if using different pins.

## Dashboard View

Once connected, open dashboard to see:
- 🌡️ Temperature in °C
- 💧 Humidity in %
- 🔊 Noise level in dB
- 💡 Light level in lux

All updating every 5 seconds!

## Full System Test

1. Start dashboard: `bash run_with_dashboard.sh`
2. Upload Arduino code
3. Open dashboard: http://192.168.137.60:5000
4. Watch sensors update in real-time
5. Cover LDR → Light level drops
6. Make noise → Noise level spikes
7. Breathe on sensors → Temp/humidity change
