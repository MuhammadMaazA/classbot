"""
Configuration file for Classroom Monitoring System
Adjust these settings based on your needs
"""

import os

# ==================== PATHS ====================
BASE_DIR = os.path.expanduser("~/classroom_ai")
KNOWN_FACES_DIR = os.path.join(BASE_DIR, "known_faces")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
ATTENDANCE_LOG = os.path.join(LOGS_DIR, "attendance.csv")
CONCENTRATION_LOG = os.path.join(LOGS_DIR, "concentration.csv")

# ==================== TIMING ====================
# On-time window in seconds
# For production: 1200 (20 minutes)
# For demo: 60 (1 minute)
ON_TIME_WINDOW_SECONDS = 60

# How often to log concentration data (in seconds)
CONCENTRATION_LOG_INTERVAL = 10

# ==================== RECOGNITION ====================
# Minimum similarity score to recognize a face (0.0-1.0)
# Lower = more lenient, Higher = more strict
# Recommended: 0.35-0.45 for good conditions, 0.25-0.35 for varying conditions
RECOGNITION_THRESHOLD = 0.40

# ==================== CAMERA ====================
# Camera resolution (lower = faster processing)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Frame rate
CAMERA_FPS = 30

# Frame skip (process every Nth frame)
# Higher = faster, but less responsive
FRAME_SKIP = 2  # Process every 2nd frame

# Camera index (usually 0 for built-in camera)
CAMERA_INDEX = 0

# ==================== HEAD POSE ====================
# Thresholds for determining if someone is "looking forward" (in degrees)
LOOKING_FORWARD_YAW_THRESHOLD = 25  # Left/right rotation
LOOKING_FORWARD_PITCH_THRESHOLD = 20  # Up/down rotation

# ==================== DISPLAY ====================
# Show FPS on display
SHOW_FPS = True

# Show concentration info on each face
SHOW_CONCENTRATION = True

# Show attendance status on each face
SHOW_ATTENDANCE_STATUS = True

# ==================== PERFORMANCE ====================
# Use GPU if available (requires CUDA)
USE_GPU = False

# Number of CPU execution providers for InsightFace
# -1 = CPU only
# 0+ = GPU device ID
CTX_ID = -1
