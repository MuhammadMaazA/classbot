#!/usr/bin/env python3
"""
Test script for sensor API
Simulates sensor data updates to test the dashboard
"""

import requests
import time
import random

# Configuration
DASHBOARD_URL = "http://localhost:5000"
UPDATE_INTERVAL = 3  # seconds

def generate_sensor_data():
    """Generate realistic simulated sensor data"""
    return {
        "temperature": round(random.uniform(20, 26), 1),  # 20-26°C
        "humidity": round(random.uniform(35, 65), 1),      # 35-65%
        "noise_level": round(random.uniform(40, 70), 1),   # 40-70 dB
        "light_level": round(random.uniform(300, 600), 0)  # 300-600 lux
    }

def test_single_update():
    """Test a single sensor update"""
    print("Testing single sensor update...")
    
    data = generate_sensor_data()
    print(f"Sending: {data}")
    
    try:
        response = requests.post(
            f"{DASHBOARD_URL}/api/sensors/update",
            json=data,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Success!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Is the dashboard server running?")
        print(f"   Try: python dashboard_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_continuous_updates():
    """Continuously send sensor data (for testing)"""
    print("Starting continuous sensor updates...")
    print(f"Updating every {UPDATE_INTERVAL} seconds")
    print("Press Ctrl+C to stop\n")
    
    try:
        count = 0
        while True:
            count += 1
            data = generate_sensor_data()
            
            print(f"\n[Update #{count}] {time.strftime('%H:%M:%S')}")
            print(f"  🌡️  Temp: {data['temperature']}°C")
            print(f"  💧 Humidity: {data['humidity']}%")
            print(f"  🔊 Noise: {data['noise_level']} dB")
            print(f"  💡 Light: {data['light_level']} lux")
            
            try:
                response = requests.post(
                    f"{DASHBOARD_URL}/api/sensors/update",
                    json=data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    print("  ✅ Sent successfully")
                else:
                    print(f"  ❌ Failed: {response.status_code}")
            
            except requests.exceptions.ConnectionError:
                print("  ❌ Connection failed")
            
            time.sleep(UPDATE_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\nStopped.")

def test_api_endpoints():
    """Test all API endpoints"""
    print("Testing all API endpoints...\n")
    
    endpoints = [
        ("GET", "/api/stats", None),
        ("GET", "/api/sensors", None),
        ("GET", "/api/alerts", None),
        ("POST", "/api/sensors/update", generate_sensor_data())
    ]
    
    for method, endpoint, data in endpoints:
        url = f"{DASHBOARD_URL}{endpoint}"
        print(f"Testing {method} {endpoint}...")
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json=data, timeout=5)
            
            if response.status_code == 200:
                print(f"  ✅ Success")
                print(f"  Response: {response.json()}")
            else:
                print(f"  ❌ Failed: {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection failed")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Classroom Dashboard - Sensor API Tester")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("Select mode:")
        print("  1. Single update test")
        print("  2. Continuous updates (simulation)")
        print("  3. Test all endpoints")
        
        choice = input("\nEnter choice (1-3): ").strip()
        mode = {"1": "single", "2": "continuous", "3": "all"}.get(choice, "single")
    
    print()
    
    if mode == "single":
        test_single_update()
    elif mode == "continuous":
        test_continuous_updates()
    elif mode == "all":
        test_api_endpoints()
    else:
        print(f"Unknown mode: {mode}")
        print("Usage: python test_sensors.py [single|continuous|all]")
