# 🎓 Classroom Dashboard

Modern, real-time monitoring dashboard that displays live classroom analytics

## How It Works

The dashboard works **in conjunction** with the monitoring system:

1. **Camera Monitoring System** (`classroom_monitor_picam.py`)
   - Runs face detection and recognition
   - Detects when students enter (marks attendance)
   - Tracks concentration levels
   - Logs everything to CSV files

2. **Dashboard** (this component)
   - Reads the CSV logs in real-time
   - Displays stats in beautiful web interface
   - Shows environmental sensor data
   - Auto-refreshes every 2 seconds

**Result**: When someone walks in front of the camera → face detected → attendance marked → dashboard updates automatically!

## Features

- **📊 Real-time Stats**: Live attendance & concentration from camera system
- **🌡️ Environmental Monitoring**: Temperature, humidity, noise, light
- **⚡ Auto-Updates**: Refreshes every 2 seconds
- **🎨 Modern UI**: Glassmorphism design with smooth animations
- **📱 Responsive**: Works on all devices
- **🔔 Smart Alerts**: Warnings for low concentration, etc.

## Setup

```bash
cd dashboard
bash setup.sh
```

## Quick Start

**Option 1: Everything Together** (Recommended)
```bash
bash run_with_dashboard.sh
```
This starts both the camera monitoring AND the dashboard together.

**Option 2: Separate Terminals** (More control)

Terminal 1 - Start Dashboard:
```bash
cd dashboard
bash start_dashboard.sh
```

Terminal 2 - Start Camera Monitoring:
```bash
bash run.sh
```

**Then open in browser:**
- Local: **http://localhost:5000**
- Network: **http://192.168.137.60:5000**

## What You'll See

As the monitoring system runs:
- ✅ Someone walks in front of camera → **Total students increases**
- ✅ Face recognized → **Present count goes up**
- ✅ Student looking at camera → **Concentration % increases**
- ✅ Student looking away → **Concentration drops**
- ✅ Environmental sensors update → **Temp/humidity/noise/light refresh**

All in real-time on the dashboard!

## API Documentation

### GET `/api/stats`
Get classroom statistics (attendance + concentration)

**Response:**
```json
{
  "attendance": {
    "total_students": 30,
    "present": 28,
    "on_time": 25,
    "late": 3,
    "attendance_rate": 93.3
  },
  "concentration": {
    "average_concentration": 72.5,
    "focused_students": 22,
    "distracted_students": 6
  }
}
```

### GET `/api/sensors`
Get environmental sensor readings

**Response:**
```json
{
  "temperature": 23.5,
  "humidity": 45.2,
  "noise_level": 55.3,
  "light_level": 487,
  "last_updated": "2026-02-22T14:30:45"
}
```

### POST `/api/sensors/update`
Update sensor data (for your friend's system)

**Request:**
```json
{
  "temperature": 23.5,
  "humidity": 45.2,
  "noise_level": 55.3,
  "light_level": 487
}
```

**Python Example:**
```python
import requests

data = {
    "temperature": 23.5,
    "humidity": 45.2,
    "noise_level": 55.3,
    "light_level": 487
}

response = requests.post(
    "http://PI_IP_ADDRESS:5000/api/sensors/update",
    json=data
)
print(response.json())
```

**curl Example:**
```bash
curl -X POST http://localhost:5000/api/sensors/update \
  -H "Content-Type: application/json" \
  -d '{"temperature": 23.5, "humidity": 45, "noise_level": 55, "light_level": 500}'
```

### GET `/api/alerts`
Get system alerts for concerning metrics

**Response:**
```json
{
  "alerts": [
    {
      "type": "warning",
      "metric": "Concentration",
      "message": "Class concentration is low (35%)",
      "action": "Consider an engagement activity"
    }
  ]
}
```

## Configuration

Edit `dashboard_config.py` to customize:

- Refresh rates
- Alert thresholds
- Display settings
- Port number

## Metric Thresholds

### Concentration Levels
- **Excellent** (Green): ≥75%
- **Good** (Yellow): 50-74%
- **Poor** (Red): <50%

### Alerts Triggered When:
- Concentration < 40%
- Temperature > 28°C
- Noise > 75 dB
- Light < 200 lux

## Integration with Monitoring System

The dashboard automatically reads from:
- `../logs/attendance.csv` - Attendance data
- `../logs/concentration.csv` - Concentration data

Run the main monitoring system alongside:
```bash
# Terminal 1: Start monitoring
bash run.sh

# Terminal 2: Start dashboard
cd dashboard && python dashboard_server.py
```

## Testing Sensor API

Test sensor updates:
```bash
python test_sensors.py
```

## Screenshots

The dashboard features:
- 📊 Large metric cards with progress bars
- 🎨 Glassmorphism design with backdrop blur
- 🌈 Gradient accents and smooth animations
- 📱 Fully responsive grid layout
- ⚡ Real-time updates without page refresh

## Troubleshooting

**Port already in use:**
```python
# Edit dashboard_config.py
DASHBOARD_PORT = 5001  # Change port
```

**Sensor data not showing:**
- Check if POST requests are reaching `/api/sensors/update`
- Ensure `ACCEPT_SENSOR_DATA = True` in config
- Data expires after 60 seconds

**Stats not updating:**
- Ensure monitoring system is running (`bash run.sh`)
- Check log files exist in `logs/` directory
- Verify file paths in `dashboard_config.py`

## Mobile Access

To access from phone/tablet on same network:
1. Get Pi IP: `hostname -I`
2. Open browser: `http://PI_IP:5000`
3. Bookmark for quick access

## Tips

- Set dashboard to auto-start on boot
- Use large display/projector for classroom view
- Adjust refresh rate based on your needs
- Customize color thresholds for your class size
