#!/bin/bash
# Start complete classroom monitoring system with dashboard

cd "$(dirname "$0")"

source ~/classroom_env/bin/activate

echo "============================================"
echo "🎓 CLASSROOM MONITORING + DASHBOARD"
echo "============================================"
echo ""

# Get IP address
IP=$(hostname -I | awk '{print $1}')

echo "Starting services..."
echo ""
echo "📹 Camera Monitoring: Runs face detection & logs data"
echo "🌐 Dashboard: http://localhost:5000"
echo "📱 Network: http://$IP:5000"
echo ""
echo "How it works:"
echo "  1. Camera detects faces → logs to CSV"
echo "  2. Dashboard reads CSV → displays live stats"
echo "  3. View dashboard in browser to see real-time updates"
echo ""
echo "Press Ctrl+C to stop all services"
echo "============================================"
echo ""

# Start dashboard in background
cd dashboard
python dashboard_server.py &
DASHBOARD_PID=$!

# Give dashboard time to start
sleep 3

# Start monitoring system in foreground
cd ..
python classroom_monitor_picam.py

# Cleanup when monitoring stops
kill $DASHBOARD_PID 2>/dev/null
echo ""
echo "Services stopped."
