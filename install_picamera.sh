#!/bin/bash
# Install picamera2 (system-wide, required for Pi Camera)

echo "Installing picamera2 for Raspberry Pi Camera..."
sudo apt update
sudo apt install -y python3-picamera2

echo ""
echo "Testing picamera2..."
python3 -c "from picamera2 import Picamera2; print('✓ picamera2 successfully installed')"

echo ""
echo "You can now run: bash run.sh"
