#!/bin/bash
# Run script for Classroom Monitoring System

echo "=========================================="
echo " Starting Classroom Monitor"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "$HOME/classroom_env" ]; then
    echo "Error: Virtual environment not found at ~/classroom_env"
    echo "Please create it or run: bash setup.sh"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source ~/classroom_env/bin/activate

# Check which camera to use
if [ -f /proc/device-tree/model ]; then
    # Running on Raspberry Pi
    pi_model=$(cat /proc/device-tree/model)
    echo "Detected: $pi_model"
    
    if python3 -c "import picamera2" 2>/dev/null; then
        echo "Using Pi Camera AI version..."
        python3 classroom_monitor_picam.py
    else
        echo "picamera2 not found, using generic version..."
        python3 classroom_monitor.py
    fi
else
    # Not on Raspberry Pi
    echo "Using generic camera version..."
    python3 classroom_monitor.py
fi
