#!/bin/bash
# Fix venv to access system packages like picamera2

echo "Fixing virtual environment to access system packages..."
echo ""

# Deactivate if active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Deactivating current venv..."
    deactivate
fi

# Backup the old venv
if [ -d "$HOME/classroom_env" ]; then
    echo "Backing up existing venv..."
    mv "$HOME/classroom_env" "$HOME/classroom_env.bak"
fi

# Create new venv with system-site-packages access
echo "Creating new venv with system package access..."
python3 -m venv ~/classroom_env --system-site-packages

# Activate it
source ~/classroom_env/bin/activate

# Reinstall packages
echo ""
echo "Installing Python packages..."
pip install --upgrade pip
pip install insightface onnxruntime opencv-python numpy

# Test everything
echo ""
echo "Testing packages..."
python3 -c "from picamera2 import Picamera2; print('✓ picamera2 accessible')"
python3 -c "import insightface; print('✓ insightface available')"
python3 -c "import cv2; print('✓ opencv available')"

echo ""
echo "✓ Virtual environment fixed!"
echo ""
echo "You can now run: bash run.sh"
echo ""
echo "Old venv backed up to ~/classroom_env.bak (you can delete it later)"
