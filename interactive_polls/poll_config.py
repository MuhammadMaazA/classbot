"""
Interactive Poll/Quiz System
Triggers when class concentration drops below threshold
"""

import os

# ========== Concentration Trigger ==========
# Trigger interactive activity when concentration drops below this %
CONCENTRATION_THRESHOLD = 40

# Minimum time between triggers (seconds) - don't spam activities
MIN_TIME_BETWEEN_ACTIVITIES = 600  # 10 minutes

# Wait time after trigger before checking again (seconds)
ACTIVITY_COOLDOWN = 300  # 5 minutes

# ========== Content Sources ==========
# Which lecture content to use for quiz generation
USE_WHITEBOARD_OCR = True  # Use whiteboard captures
USE_AUDIO_TRANSCRIPTION = False  # Use audio transcripts (if available)
USE_RECENT_ONLY = True  # Only use content from last N minutes

# How far back to look for content (minutes)
CONTENT_LOOKBACK_MINUTES = 15

# ========== Quiz Generation ==========
# Quiz type: 'multiple_choice', 'poll', 'open_ended', 'mixed'
QUIZ_TYPE = 'mixed'

# Number of questions to generate
NUM_QUESTIONS = 5

# Difficulty: 'easy', 'medium', 'hard', 'adaptive'
DIFFICULTY = 'medium'

# AI Provider for quiz generation
# Note: Gemini API may have quota limits. Fallback quiz will be used if API fails.
QUIZ_AI_PROVIDER = 'gemini'  # 'gemini', 'openai', 'anthropic', or 'fallback'
QUIZ_AI_MODEL = 'gemini-1.5-flash'  # Model name (API compatibility may vary)
# ========== Web Interface ==========
# Port for web interface
WEB_PORT = 8080

# Auto-open browser when quiz starts
AUTO_OPEN_BROWSER = True

# Quiz duration (seconds) - how long students have to answer
QUIZ_DURATION = 180  # 3 minutes

# Show live results to students?
SHOW_LIVE_RESULTS = True

# Show correct answers after quiz ends?
SHOW_ANSWERS_AFTER = True

# ========== Display ==========
# Show quiz on classroom display/projector?
SHOW_ON_MAIN_DISPLAY = True

# QR code for easy access on phones
GENERATE_QR_CODE = True

# ========== Output ==========
OUTPUT_DIR = 'interactive_polls'
QUIZ_RESULTS_FILE = f'{OUTPUT_DIR}/quiz_results.json'
ANALYTICS_FILE = f'{OUTPUT_DIR}/engagement_analytics.csv'

# Create directories
os.makedirs(OUTPUT_DIR, exist_ok=True)
