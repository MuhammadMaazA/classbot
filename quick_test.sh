#!/bin/bash
# Quick test script - sets up venv and runs camera test

cd ~/classroom_ai

echo "=========================================="
echo " Quick Camera Test with venv"
echo "=========================================="
echo ""

# Create venv if it doesn't exist
if [ ! -d "$HOME/classroom_env" ]; then
    echo "Creating virtual environment at ~/classroom_env..."
    python3 -m venv ~/classroom_env --system-site-packages
    echo ""
fi

# Activate venv
echo "Activating virtual environment..."
source ~/classroom_env/bin/activate
echo ""

# Install dependencies if needed
echo "Checking/installing dependencies..."
pip install -q insightface onnxruntime opencv-python numpy 2>&1 | grep -v "already satisfied" || true
echo ""

# Run camera test
echo "Starting camera test..."
echo "Press 'q' to quit, 's' to save test image"
echo ""
python3 test_camera.py
