#!/usr/bin/env python3
"""
Classroom Dashboard Server
Real-time monitoring with modern UI
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
import csv
from datetime import datetime, timedelta
from collections import defaultdict
import dashboard_config as config

app = Flask(__name__)
CORS(app)

# Get project root directory (parent of dashboard folder)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# In-memory storage for sensor data
sensor_data = {
    'temperature': None,
    'humidity': None,
    'noise_level': None,
    'light_level': None,
    'last_updated': None
}

# Cache for stats to avoid reading files too frequently
stats_cache = {
    'data': None,
    'timestamp': None
}

def read_attendance_stats():
    """Read attendance data and calculate stats"""
    try:
        attendance_file = os.path.join(PROJECT_ROOT, config.ATTENDANCE_LOG)
        if not os.path.exists(attendance_file):
            return {
                'total_students': 0,
                'present': 0,
                'on_time': 0,
                'late': 0,
                'attendance_rate': 0,
                'students': []
            }
        
        students = {}
        with open(attendance_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['name']
                # Always update to keep the LATEST entry per student
                status = row['status'].upper().replace('-', '-')  # "on-time" or "late"
                students[name] = {
                    'name': name,
                    'status': status,
                    'time': row['timestamp']
                }
        
        total = len(students)
        on_time = sum(1 for s in students.values() if 'on-time' in s['status'].lower() or 'on_time' in s['status'].lower())
        late = sum(1 for s in students.values() if 'late' in s['status'].lower())
        present = on_time + late
        
        return {
            'total_students': total,
            'present': present,
            'on_time': on_time,
            'late': late,
            'attendance_rate': round((present / total * 100) if total > 0 else 0, 1),
            'students': list(students.values())
        }
    except Exception as e:
        print(f"Error reading attendance: {e}")
        return {'total_students': 0, 'present': 0, 'on_time': 0, 'late': 0, 'attendance_rate': 0, 'students': []}

def read_concentration_stats():
    """Read concentration data and calculate average"""
    try:
        concentration_file = os.path.join(PROJECT_ROOT, config.CONCENTRATION_LOG)
        if not os.path.exists(concentration_file):
            return {
                'average_concentration': 0,
                'focused_students': 0,
                'distracted_students': 0,
                'recent_readings': []
            }
        
        # Read last 5 minutes of data
        cutoff_time = datetime.now() - timedelta(minutes=5)
        recent_data = []
        
        with open(concentration_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S')
                    if timestamp >= cutoff_time:
                        # Check if student is looking forward
                        looking_forward = row.get('looking_forward', 'no').lower() == 'yes'
                        
                        recent_data.append({
                            'timestamp': row['timestamp'],
                            'name': row.get('name', 'unknown'),
                            'looking_forward': looking_forward
                        })
                except:
                    continue
        
        if not recent_data:
            return {
                'average_concentration': 0,
                'focused_students': 0,
                'distracted_students': 0,
                'recent_readings': []
            }
        
        # Get latest reading per student
        latest_by_student = {}
        for reading in recent_data:
            name = reading['name']
            latest_by_student[name] = reading['looking_forward']
        
        # Calculate metrics
        total_students = len(latest_by_student)
        focused = sum(1 for looking in latest_by_student.values() if looking)
        distracted = total_students - focused
        avg_concentration = round((focused / total_students * 100) if total_students > 0 else 0, 1)
        
        return {
            'average_concentration': avg_concentration,
            'focused_students': focused,
            'distracted_students': distracted,
            'recent_readings': recent_data[-20:]  # Last 20 readings
        }
    except Exception as e:
        print(f"Error reading concentration: {e}")
        return {'average_concentration': 0, 'focused_students': 0, 'distracted_students': 0, 'recent_readings': []}

def get_cached_stats():
    """Get stats with caching"""
    now = datetime.now()
    
    # Return cached data if still valid
    if stats_cache['data'] and stats_cache['timestamp']:
        age = (now - stats_cache['timestamp']).total_seconds()
        if age < config.STATS_CACHE_TIME:
            return stats_cache['data']
    
    # Refresh cache
    attendance = read_attendance_stats()
    concentration = read_concentration_stats()
    
    stats_cache['data'] = {
        'attendance': attendance,
        'concentration': concentration,
        'timestamp': now.isoformat()
    }
    stats_cache['timestamp'] = now
    
    return stats_cache['data']

@app.route('/')
def index():
    """Serve the dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get current classroom stats (attendance + concentration)"""
    stats = get_cached_stats()
    return jsonify(stats)

@app.route('/api/sensors')
def get_sensors():
    """Get current environmental sensor readings"""
    return jsonify(sensor_data)

@app.route('/api/sensors/update', methods=['POST'])
def update_sensors():
    """Receive sensor data from external system"""
    if not config.ACCEPT_SENSOR_DATA:
        return jsonify({'error': 'Sensor data updates disabled'}), 403
    
    try:
        data = request.json
        
        # Update sensor data
        if 'temperature' in data:
            sensor_data['temperature'] = float(data['temperature'])
        if 'humidity' in data:
            sensor_data['humidity'] = float(data['humidity'])
        if 'noise_level' in data:
            sensor_data['noise_level'] = float(data['noise_level'])
        if 'light_level' in data:
            sensor_data['light_level'] = float(data['light_level'])
        
        sensor_data['last_updated'] = datetime.now().isoformat()
        
        # Save to file
        with open(config.SENSOR_DATA_FILE, 'w') as f:
            json.dump(sensor_data, f, indent=2)
        
        return jsonify({'status': 'success', 'data': sensor_data})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/alerts')
def get_alerts():
    """Check for concerning metrics and return alerts"""
    if not config.ENABLE_ALERTS:
        return jsonify({'alerts': []})
    
    alerts = []
    stats = get_cached_stats()
    
    # Check concentration
    if stats['concentration']['average_concentration'] < config.ALERT_LOW_CONCENTRATION:
        alerts.append({
            'type': 'warning',
            'metric': 'Concentration',
            'message': f"Class concentration is low ({stats['concentration']['average_concentration']}%)",
            'action': 'Consider an engagement activity'
        })
    
    # Check environmental conditions
    if sensor_data['temperature'] and sensor_data['temperature'] > config.ALERT_HIGH_TEMP:
        alerts.append({
            'type': 'warning',
            'metric': 'Temperature',
            'message': f"Room temperature is high ({sensor_data['temperature']}°C)",
            'action': 'Adjust climate control'
        })
    
    if sensor_data['noise_level'] and sensor_data['noise_level'] > config.ALERT_HIGH_NOISE:
        alerts.append({
            'type': 'info',
            'metric': 'Noise',
            'message': f"Noise level is elevated ({sensor_data['noise_level']} dB)",
            'action': 'May indicate active discussion'
        })
    
    if sensor_data['light_level'] and sensor_data['light_level'] < config.ALERT_LOW_LIGHT:
        alerts.append({
            'type': 'warning',
            'metric': 'Lighting',
            'message': f"Light level is low ({sensor_data['light_level']} lux)",
            'action': 'Increase lighting'
        })
    
    return jsonify({'alerts': alerts})

if __name__ == '__main__':
    print("=" * 60)
    print("🎓 CLASSROOM DASHBOARD SERVER")
    print("=" * 60)
    print(f"Starting dashboard on http://localhost:{config.DASHBOARD_PORT}")
    print(f"Network access: http://YOUR_PI_IP:{config.DASHBOARD_PORT}")
    print()
    print("API Endpoints:")
    print(f"  GET  /api/stats       - Classroom stats")
    print(f"  GET  /api/sensors     - Environmental sensors")
    print(f"  POST /api/sensors/update - Update sensor data")
    print(f"  GET  /api/alerts      - System alerts")
    print("=" * 60)
    print()
    print("💡 TIP: Start monitoring system to collect data:")
    print("   bash run.sh")
    print("=" * 60)
    
    app.run(host=config.HOST, port=config.DASHBOARD_PORT, debug=config.DEBUG)
