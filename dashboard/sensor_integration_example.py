#!/usr/bin/env python3
"""
Example integration for external sensor system

Your friend can use this as a template to send sensor data
from their measurement system to the dashboard.
"""

import requests
import time

# ==================== CONFIGURATION ====================
DASHBOARD_URL = "http://192.168.1.XXX:5000"  # Replace with your Pi's IP
UPDATE_INTERVAL = 5  # Send update every 5 seconds
# =======================================================

def send_sensor_data(temperature, humidity, noise_level, light_level):
    """
    Send sensor readings to the dashboard
    
    Args:
        temperature (float): Temperature in Celsius
        humidity (float): Relative humidity (%)
        noise_level (float): Sound level in dB
        light_level (float): Light intensity in lux
    
    Returns:
        bool: True if successful, False otherwise
    """
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "noise_level": noise_level,
        "light_level": light_level
    }
    
    try:
        response = requests.post(
            f"{DASHBOARD_URL}/api/sensors/update",
            json=data,
            timeout=5
        )
        
        if response.status_code == 200:
            print(f"✅ Data sent: T={temperature}°C, H={humidity}%, N={noise_level}dB, L={light_level}lux")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def main():
    """
    Main loop - replace this with your actual sensor reading logic
    """
    print("=" * 60)
    print("Sensor System → Dashboard Integration")
    print("=" * 60)
    print(f"Sending data to: {DASHBOARD_URL}")
    print(f"Update interval: {UPDATE_INTERVAL} seconds")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            # ==================== REPLACE THIS ====================
            # Read from your actual sensors here
            # Example using dummy values:
            
            temperature = 23.5    # Read from temp sensor
            humidity = 45.2       # Read from humidity sensor
            noise_level = 55.3    # Read from sound sensor
            light_level = 487     # Read from light sensor
            
            # ======================================================
            
            # Send to dashboard
            send_sensor_data(temperature, humidity, noise_level, light_level)
            
            # Wait before next update
            time.sleep(UPDATE_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n\nStopped by user.")
            break
        except Exception as e:
            print(f"⚠️  Error: {e}")
            time.sleep(UPDATE_INTERVAL)

# ==================== EXAMPLE INTEGRATIONS ====================

def example_arduino_serial():
    """Example: Reading from Arduino via serial port"""
    import serial
    
    # Open serial connection
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    
    while True:
        # Read line from Arduino
        line = ser.readline().decode('utf-8').strip()
        
        # Parse data (assuming format: "TEMP:23.5,HUM:45,NOISE:55,LIGHT:487")
        try:
            parts = dict(item.split(':') for item in line.split(','))
            
            send_sensor_data(
                temperature=float(parts['TEMP']),
                humidity=float(parts['HUM']),
                noise_level=float(parts['NOISE']),
                light_level=float(parts['LIGHT'])
            )
        except:
            continue
        
        time.sleep(UPDATE_INTERVAL)

def example_mqtt_subscriber():
    """Example: Subscribing to MQTT topics"""
    import paho.mqtt.client as mqtt
    
    sensor_data = {}
    
    def on_message(client, userdata, message):
        topic = message.topic
        value = float(message.payload.decode())
        
        # Map topics to sensor names
        if 'temperature' in topic:
            sensor_data['temperature'] = value
        elif 'humidity' in topic:
            sensor_data['humidity'] = value
        elif 'noise' in topic:
            sensor_data['noise_level'] = value
        elif 'light' in topic:
            sensor_data['light_level'] = value
        
        # Send when all data is available
        if len(sensor_data) == 4:
            send_sensor_data(**sensor_data)
    
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("mqtt.broker.com", 1883)
    client.subscribe("sensors/#")
    client.loop_forever()

def example_rest_api_polling():
    """Example: Polling data from another REST API"""
    while True:
        try:
            # Fetch from your sensor system's API
            response = requests.get("http://sensor-system.local/api/readings")
            data = response.json()
            
            # Forward to dashboard
            send_sensor_data(
                temperature=data['temp'],
                humidity=data['humidity'],
                noise_level=data['noise'],
                light_level=data['light']
            )
        except:
            pass
        
        time.sleep(UPDATE_INTERVAL)

# =============================================================

if __name__ == "__main__":
    # Run the main loop
    main()
    
    # Or use one of the example integrations:
    # example_arduino_serial()
    # example_mqtt_subscriber()
    # example_rest_api_polling()
