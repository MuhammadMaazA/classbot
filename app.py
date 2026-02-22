from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory store (last 100 readings)
readings = []
MAX_READINGS = 100

@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400

    reading = {
        'timestamp': datetime.utcnow().isoformat(),
        'time':      data.get('time', ''),
        'temp':      data.get('temp', 0),
        'humidity':  data.get('humidity', 0),
        'light':     data.get('light', 0),
        'noise':     data.get('noise', 0),
        'alert':     data.get('alert', False),
        'alertMsg':  data.get('alertMsg', '')
    }
    readings.append(reading)
    if len(readings) > MAX_READINGS:
        readings.pop(0)

    print(f"[{reading['timestamp']}] {reading}")
    return jsonify({'status': 'ok'}), 200

@app.route('/api/latest', methods=['GET'])
def get_latest():
    if not readings:
        return jsonify({'error': 'No data yet'}), 404
    return jsonify(readings[-1])

@app.route('/api/history', methods=['GET'])
def get_history():
    return jsonify(readings)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'running', 'readings': len(readings)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
