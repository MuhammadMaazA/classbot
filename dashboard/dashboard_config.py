"""
Classroom Dashboard Configuration
Real-time monitoring of attendance, concentration, and environmental conditions
"""

import os

# ========== Server Settings ==========
DASHBOARD_PORT = 5000
HOST = '0.0.0.0'  # Accessible from network
DEBUG = False

# ========== Data Sources ==========
# Paths to log files (relative to project root)
ATTENDANCE_LOG = 'logs/attendance.csv'
CONCENTRATION_LOG = 'logs/concentration.csv'

# ========== Refresh Rates ==========
# How often to update data (milliseconds)
FRONTEND_REFRESH_INTERVAL = 2000  # 2 seconds
STATS_CACHE_TIME = 0.5  # Cache stats for 0.5 seconds

# ========== Environmental Sensor API ==========
# Your friend's system will POST sensor data to these endpoints
ACCEPT_SENSOR_DATA = True
SENSOR_DATA_EXPIRY = 60  # Consider data stale after 60 seconds

# ========== Display Settings ==========
# Concentration thresholds for color coding
CONCENTRATION_EXCELLENT = 75  # >= 75% = green
CONCENTRATION_GOOD = 50       # >= 50% = yellow
CONCENTRATION_LOW = 30        # < 30% = red

# Attendance thresholds
ATTENDANCE_GOOD = 80  # >= 80% = green
ATTENDANCE_OK = 60    # >= 60% = yellow

# ========== Alert Settings ==========
# Trigger alerts for concerning metrics
ENABLE_ALERTS = True
ALERT_LOW_CONCENTRATION = 40  # Alert if avg concentration < 40%
ALERT_HIGH_TEMP = 28          # Alert if temp > 28°C
ALERT_HIGH_NOISE = 75         # Alert if noise > 75 dB
ALERT_LOW_LIGHT = 200         # Alert if light < 200 lux

# ========== Storage ==========
OUTPUT_DIR = 'dashboard'
SENSOR_DATA_FILE = f'{OUTPUT_DIR}/sensor_data.json'
DASHBOARD_STATS_FILE = f'{OUTPUT_DIR}/dashboard_stats.json'

os.makedirs(OUTPUT_DIR, exist_ok=True)
