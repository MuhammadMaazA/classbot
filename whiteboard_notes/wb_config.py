"""
Configuration for Whiteboard OCR Notes System
"""

import os

# ========== Camera Settings ==========
CAMERA_RESOLUTION = (1920, 1080)  # Higher resolution for better OCR
CAMERA_FPS = 10  # Lower FPS since we're not doing face detection

# ========== Whiteboard Detection ==========
# Capture interval (seconds) - how often to check for changes
CAPTURE_INTERVAL = 30  # Capture every 30 seconds if content changed

# Motion detection sensitivity (0-100, higher = more sensitive)
MOTION_THRESHOLD = 5.0  # Percentage of frame that must change

# Minimum time between captures (seconds)
MIN_CAPTURE_DELAY = 10  # Don't capture more often than every 10 seconds

# ========== OCR Settings ==========
# OCR Engine: 'tesseract', 'easyocr', 'paddleocr'
OCR_ENGINE = 'tesseract'  # Change based on what you installed

# OCR Language
OCR_LANGUAGE = 'eng'  # 'eng' for English, 'chi_sim' for Chinese, etc.

# Preprocessing
ENHANCE_CONTRAST = True
DENOISE = True
BINARIZE = True  # Convert to black and white for better OCR

# ========== LLM Settings ==========
# LLM Provider: 'openai', 'gemini', 'anthropic', 'local', 'none'
LLM_PROVIDER = 'gemini'  # Using Google Gemini

# Model names
OPENAI_MODEL = 'gpt-4o-mini'  # or 'gpt-4', 'gpt-3.5-turbo'
GEMINI_MODEL = 'gemini-1.5-pro'  # or 'gemini-1.5-flash-002'
ANTHROPIC_MODEL = 'claude-3-haiku-20240307'  # or 'claude-3-sonnet'

# ========== Output Settings ==========
OUTPUT_DIR = 'whiteboard_notes/captures'
NOTES_FILE = 'whiteboard_notes/lecture_notes.md'
RAW_TEXT_FILE = 'whiteboard_notes/raw_ocr.txt'

# Save captured images?
SAVE_IMAGES = True
SAVE_ANNOTATED = True  # Save with detection boxes

# ========== Display Settings ==========
SHOW_PREVIEW = True  # Show live camera feed
PREVIEW_SCALE = 0.5  # Scale factor for display (0.5 = half size)

# ========== Advanced ==========
# Whiteboard color range (HSV) - adjust based on your whiteboard
# White/gray whiteboard
WHITEBOARD_LOWER_HSV = (0, 0, 180)
WHITEBOARD_UPPER_HSV = (180, 30, 255)

# Edge detection for text
CANNY_THRESHOLD1 = 50
CANNY_THRESHOLD2 = 150

# Create directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(NOTES_FILE), exist_ok=True)
