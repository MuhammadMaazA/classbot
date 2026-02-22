#!/usr/bin/env python3
"""
Simulate live sensor data for dashboard testing
Generates realistic environmental readings and posts them to the dashboard
"""

import requests
import time
import random
from datetime import datetime

DASHBOARD_URL = "http://localhost:5000/api/sensors/update"
UPDATE_INTERVAL = 2  # seconds

def generate_sensor_data():
    """Generate realistic sensor readings"""
    # Base values with some random variation
    temperature = round(22 + random.uniform(-2, 4), 1)  # 20-26°C
    humidity = round(45 + random.uniform(-10, 15), 1)    # 35-60%
    noise_level = round(50 + random.uniform(-5, 25), 1)  # 45-75 dB
    light_level = round(400 + random.uniform(-100, 200), 0)  # 300-600 lux
    
    return {
        'temperature': temperature,
        'humidity': humidity,
        'noise_level': noise_level,
        'light_level': light_level
    }

def post_sensor_data(data):
    """Post sensor data to dashboard"""
    try:
        response = requests.post(DASHBOARD_URL, json=data, timeout=2)
        if response.status_code == 200:
            print(f"✓ [{datetime.now().strftime('%H:%M:%S')}] Sent: "
                  f"Temp={data['temperature']}°C, "
                  f"Humidity={data['humidity']}%, "
                  f"Noise={data['noise_level']}dB, "
                  f"Light={data['light_level']}lux")
            return True
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to dashboard at {DASHBOARD_URL}")
        print("  Make sure the dashboard is running: bash dashboard/start_dashboard.sh")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("=" * 70)
    print("🌡️  CLASSROOM SENSOR SIMULATOR")
    print("=" * 70)
    print(f"Target: {DASHBOARD_URL}")
    print(f"Update interval: {UPDATE_INTERVAL}s")
    print()
    print("Generating realistic environmental data...")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    try:
        while True:
            data = generate_sensor_data()
            post_sensor_data(data)
            time.sleep(UPDATE_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n")
        print("=" * 70)
        print("Sensor simulator stopped")
        print("=" * 70)

if __name__ == '__main__':
    main()
