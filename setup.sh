#!/bin/bash
# Quick start script for Classroom Monitoring System

echo "=========================================="
echo " Classroom Monitoring System - Setup"
echo "=========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
echo "Python version: $python_version"

# Check if running on Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    pi_model=$(cat /proc/device-tree/model)
    echo "Device: $pi_model"
fi

echo ""
echo "Installing dependencies..."
echo ""

# Install system dependencies
if command -v apt &> /dev/null; then
    echo "Installing system packages..."
    sudo apt update
    sudo apt install -y python3-pip python3-venv python3-opencv python3-numpy
    
    # Install picamera2 if on Raspberry Pi
    if [ -f /proc/device-tree/model ]; then
        echo "Installing picamera2 for Raspberry Pi..."
        sudo apt install -y python3-picamera2
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$HOME/classroom_env" ]; then
    echo ""
    echo "Creating Python virtual environment at ~/classroom_env..."
    python3 -m venv ~/classroom_env --system-site-packages
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source ~/classroom_env/bin/activate

# Install Python packages in venv
echo ""
echo "Installing Python packages in virtual environment..."
pip install --upgrade pip
pip install opencv-python numpy insightface onnxruntime

echo ""
echo "=========================================="
echo " Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Add face images to known_faces/ directory"
echo "   - Create a folder for each person"
echo "   - Add 2-5 clear photos of each person"
echo ""
echo "2. Run the monitoring system:"
echo "   For Pi Camera AI: python3 classroom_monitor_picam.py"
echo "   For USB/Generic: python3 classroom_monitor.py"
echo ""
echo "3. Press 'q' or ESC to quit"
echo ""
