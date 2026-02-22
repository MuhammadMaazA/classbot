#!/bin/bash
# Automated test script for Classroom Monitoring System

echo "=========================================="
echo " Classroom AI - System Test"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test 1: Directory structure
echo -n "[TEST 1] Checking directory structure... "
if [ -d "$HOME/classroom_ai" ]; then
    echo -e "${GREEN}✓${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    echo "  Error: ~/classroom_ai directory not found"
    ((TESTS_FAILED++))
fi

# Test 2: Known faces directory
echo -n "[TEST 2] Checking known_faces directory... "
if [ -d "$HOME/classroom_ai/known_faces" ]; then
    FACE_COUNT=$(find "$HOME/classroom_ai/known_faces" -maxdepth 1 -type d | wc -l)
    FACE_COUNT=$((FACE_COUNT - 1))  # Subtract the parent directory
    if [ $FACE_COUNT -gt 0 ]; then
        echo -e "${GREEN}✓${NC} ($FACE_COUNT people)"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} (no people found)"
        echo "  Warning: Add face images to known_faces/ directory"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}✗${NC}"
    echo "  Error: known_faces directory not found"
    ((TESTS_FAILED++))
fi

# Test 3: Python availability
echo -n "[TEST 3] Checking Python 3... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✓${NC} ($PYTHON_VERSION)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    echo "  Error: Python 3 not found"
    ((TESTS_FAILED++))
fi

# Test 3b: Virtual environment
echo -n "[TEST 3b] Checking virtual environment... "
if [ -d "$HOME/classroom_env" ]; then
    echo -e "${GREEN}✓${NC}"
    ((TESTS_PASSED++))
    # Activate venv for remaining tests
    source "$HOME/classroom_env/bin/activate"
else
    echo -e "${YELLOW}⚠${NC}"
    echo "  Warning: venv not found at ~/classroom_env (run 'bash setup.sh' to create)"
    ((TESTS_PASSED++))  # Not critical yet
fi

# Test 4: OpenCV
echo -n "[TEST 4] Checking OpenCV... "
if python3 -c "import cv2" 2>/dev/null; then
    CV_VERSION=$(python3 -c "import cv2; print(cv2.__version__)" 2>/dev/null)
    echo -e "${GREEN}✓${NC} ($CV_VERSION)"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    echo "  Error: OpenCV not installed"
    echo "  Install: pip3 install opencv-python"
    ((TESTS_FAILED++))
fi

# Test 5: InsightFace
echo -n "[TEST 5] Checking InsightFace... "
if python3 -c "import insightface" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    echo "  Error: InsightFace not installed"
    echo "  Install: pip3 install insightface onnxruntime"
    ((TESTS_FAILED++))
fi

# Test 6: Picamera2 (for Raspberry Pi)
echo -n "[TEST 6] Checking picamera2... "
if python3 -c "import picamera2" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
    ((TESTS_PASSED++))
    CAMERA_TYPE="Pi Camera (picamera2)"
else
    echo -e "${YELLOW}⚠${NC}"
    echo "  Warning: picamera2 not found (will use OpenCV fallback)"
    echo "  Install: sudo apt install python3-picamera2"
    ((TESTS_PASSED++))  # Not critical, we have fallback
    CAMERA_TYPE="Generic (OpenCV)"
fi

# Test 7: Camera hardware (Raspberry Pi)
echo -n "[TEST 7] Checking camera hardware... "
if command -v rpicam-hello &> /dev/null; then
    # Try to detect camera
    if rpicam-hello --list 2>&1 | grep -q "Available cameras"; then
        echo -e "${GREEN}✓${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC}"
        echo "  Warning: No Pi camera detected"
        echo "  Make sure camera is connected and enabled"
        ((TESTS_PASSED++))  # Not critical if using USB camera
    fi
else
    echo -e "${YELLOW}⚠${NC} (rpicam tools not available)"
    ((TESTS_PASSED++))  # Not on Raspberry Pi or using USB camera
fi

# Test 8: Log directory
echo -n "[TEST 8] Checking logs directory... "
if [ -d "$HOME/classroom_ai/logs" ]; then
    echo -e "${GREEN}✓${NC}"
    ((TESTS_PASSED++))
else
    mkdir -p "$HOME/classroom_ai/logs"
    echo -e "${GREEN}✓${NC} (created)"
    ((TESTS_PASSED++))
fi

# Test 9: Required scripts
echo -n "[TEST 9] Checking required scripts... "
if [ -f "$HOME/classroom_ai/classroom_monitor_picam.py" ] && \
   [ -f "$HOME/classroom_ai/config.py" ] && \
   [ -f "$HOME/classroom_ai/run.sh" ]; then
    echo -e "${GREEN}✓${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    echo "  Error: Some required scripts are missing"
    ((TESTS_FAILED++))
fi

# Summary
echo ""
echo "=========================================="
echo " Test Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Failed: ${RED}${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical tests passed!${NC}"
    echo ""
    echo "Camera type: $CAMERA_TYPE"
    echo ""
    echo "Next steps:"
    echo "1. Test camera: python3 test_camera.py"
    echo "2. Run system: bash run.sh"
    echo ""
    echo "See TEST_GUIDE.md for detailed instructions"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Please fix the issues above before running the system."
    echo "Run 'bash setup.sh' to install missing dependencies."
    exit 1
fi
