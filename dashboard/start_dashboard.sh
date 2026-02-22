#!/bin/bash
# Quick start script for the dashboard

cd "$(dirname "$0")/.."

source ~/classroom_env/bin/activate

echo "🎓 Starting Classroom Dashboard..."
echo ""
echo "Access at:"
echo "  Local:   http://localhost:5000"
echo "  Network: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd dashboard
python dashboard_server.py
