#!/bin/bash
# Setup script for Classroom Dashboard

echo "============================================"
echo "Classroom Dashboard Setup"
echo "============================================"

# Activate virtual environment
source ~/classroom_env/bin/activate

echo "📦 Installing dependencies..."
pip install flask flask-cors

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the dashboard:"
echo "  cd dashboard"
echo "  python dashboard_server.py"
echo ""
echo "Then open in browser:"
echo "  http://localhost:5000"
echo ""
echo "For your friend's system to send sensor data:"
echo "  POST http://YOUR_PI_IP:5000/api/sensors/update"
echo "  Content-Type: application/json"
echo '  {"temperature": 23.5, "humidity": 45, "noise_level": 55, "light_level": 500}'
echo ""
