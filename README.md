# Classroom AI Monitoring System

A real-time classroom monitoring system using face recognition and head pose detection. Tracks student attendance (on-time vs late arrivals) and monitors concentration levels.

## Features

### 1. **Attendance Tracking**
- **Automatic person counting**: Counts unique individuals entering the camera frame
- **Time-based status**: Marks students as "on-time" or "late" based on arrival time
- **No duplicate counting**: Each person is counted only once, even if they leave and re-enter
- **Configurable time window**: First 60 seconds (demo) or 20 minutes (production) for on-time arrivals
- **CSV logging**: Stores attendance records with timestamps

### 2. **Concentration Monitoring**
- **Head pose tracking**: Detects if students are looking forward or away
- **Real-time metrics**: Shows concentration percentage per student and overall classroom
- **CSV logging**: Records concentration events with head pose angles (yaw, pitch, roll)

### 3. **Performance Optimizations**
- **Low latency**: Optimized for Raspberry Pi Camera AI
- **Frame skipping**: Processes every 2nd frame for better performance
- **Lower resolution**: 640x480 for faster processing
- **Efficient face recognition**: Uses InsightFace with averaged embeddings

### 4. **Visual Display**
- Live video feed with bounding boxes around detected faces
- Name, confidence score, and attendance status for each person
- Concentration indicator (looking forward/away)
- Session statistics panel showing:
  - Time remaining in on-time window
  - Total, on-time, and late arrivals
  - Overall concentration percentage
  - Current FPS

## Directory Structure

```
classroom_ai/
├── classroom_monitor.py      # Main monitoring system
├── config.py                  # Configuration settings
├── recognize_and_log.py       # Original recognition script
├── test_recognition.py        # Test recognition on images
├── known_faces/               # Face database
│   ├── asad/                  # Person 1 folder
│   │   ├── photo1.jpg
│   │   └── photo2.jpg
│   ├── maaz/                  # Person 2 folder
│   └── makarim/               # Person 3 folder
├── logs/                      # Log files
│   ├── attendance.csv         # Attendance records
│   └── concentration.csv      # Concentration records
└── test_images/               # Test images
```

## Setup

### 1. Install Dependencies

```bash
pip install opencv-python numpy insightface
```

### 2. Prepare Known Faces

1. Create a folder for each person in `known_faces/`
2. Add 2-5 clear face photos of each person to their folder
3. Supported formats: `.jpg`, `.jpeg`, `.png`

Example:
```
known_faces/
├── john/
│   ├── john1.jpg
│   └── john2.jpg
└── mary/
    ├── mary1.jpg
    └── mary2.jpg
```

### 3. Configure Settings (Optional)

Edit `config.py` to adjust:
- On-time window duration
- Recognition threshold
- Camera resolution
- Frame skip rate
- Head pose thresholds

## Usage

### Run the Monitoring System

```bash
python3 classroom_monitor.py
```

### Controls

- **Press 'q' or ESC**: Quit the application

### What Happens

1. **Session starts automatically** when you run the script
2. **On-time window**: First 60 seconds (configurable)
   - People detected during this window are marked as "on-time"
   - Count increases by 1 for each new person
3. **After window expires**:
   - People are still detected and recognized
   - Marked as "late" arrivals
   - Count still increases for new people
4. **Concentration tracking** runs continuously:
   - Checks if people are looking forward
   - Updates concentration percentage
5. **Logs are saved** to CSV files in `logs/` directory

## Output Files

### attendance.csv
```csv
timestamp,name,status,similarity
2026-02-21 10:00:05,asad,on-time,0.782
2026-02-21 10:00:15,maaz,on-time,0.823
2026-02-21 10:01:30,makarim,late,0.791
```

### concentration.csv
```csv
timestamp,name,looking_forward,yaw,pitch,roll
2026-02-21 10:00:15,asad,yes,5.23,-2.11,1.45
2026-02-21 10:00:25,maaz,no,35.67,8.23,0.91
```

## Understanding the Display

### Info Panel (Top)
- **Session status**: Shows if on-time window is active and time remaining
- **Total**: Count of all unique people detected
- **On-time**: Count of people who arrived within the time window
- **Late**: Count of people who arrived after the window
- **Overall Concentration**: Average concentration across all students
- **FPS**: Current frames per second

### Face Boxes
- **Green box**: Person recognized and marked on-time
- **Orange box**: Person recognized but marked late
- **Gray box**: Unknown person (not in database)

### Face Labels
- **Top**: Name and confidence score
- **Bottom**: 
  - Status (on-time/late)
  - Concentration (Looking: Forward/Away)

## Configuration Options

### For Demo (Fast Testing)
```python
ON_TIME_WINDOW_SECONDS = 60  # 1 minute
FRAME_SKIP = 2
```

### For Production (Real Classroom)
```python
ON_TIME_WINDOW_SECONDS = 1200  # 20 minutes
FRAME_SKIP = 1  # Process every frame
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
```

### For Better Performance
```python
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FRAME_SKIP = 3  # Process every 3rd frame
RECOGNITION_THRESHOLD = 0.50  # Stricter matching
```

### For Better Accuracy
```python
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
FRAME_SKIP = 1
RECOGNITION_THRESHOLD = 0.40  # More lenient matching
```

## Pi Camera AI Specific Notes

The system is optimized for Raspberry Pi Camera AI:

1. **Low resolution**: 640x480 for faster processing
2. **Frame skipping**: Processes every 2nd frame
3. **CPU execution**: Uses CPUExecutionProvider for InsightFace
4. **Efficient face matching**: Uses averaged embeddings for each person

### For Pi Camera Module

If using Pi Camera Module (not USB), modify camera initialization:

```python
from picamera2 import Picamera2

picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

# In the loop:
frame = picam2.capture_array()
```

## Troubleshooting

### "No known faces loaded!"
- Check that `known_faces/` directory exists
- Make sure each person has their own subfolder
- Verify images are in `.jpg`, `.jpeg`, or `.png` format
- Ensure images contain clear, visible faces

### Low FPS / Slow Performance
- Increase `FRAME_SKIP` in config.py (try 3 or 4)
- Decrease camera resolution (try 320x240)
- Reduce number of known faces
- Close other applications

### Poor Recognition Accuracy
- Add more photos to each person's folder (3-5 recommended)
- Use clear, well-lit photos
- Adjust `RECOGNITION_THRESHOLD` (lower = more lenient)
- Ensure test environment matches training photos

### Camera Not Opening
- Check camera permissions
- Try different `CAMERA_INDEX` values (0, 1, 2...)
- Verify camera is not in use by another application
- For Pi Camera, ensure it's enabled in raspi-config

## Architecture

```
Camera Feed
    │
    ├─> Face Detection (InsightFace)
    │       │
    │       ├─> Face Recognition Module
    │       │       ├─> Compare with known faces
    │       │       └─> Get name & confidence
    │       │
    │       ├─> Attendance Tracking Module
    │       │       ├─> Check if new person
    │       │       ├─> Check timing (on-time vs late)
    │       │       ├─> Update count
    │       │       └─> Log to CSV
    │       │
    │       └─> Concentration Tracking Module
    │               ├─> Analyze head pose
    │               ├─> Check if looking forward
    │               ├─> Update concentration metrics
    │               └─> Log to CSV
    │
    └─> Display with annotations
```

## Future Enhancements

- Dashboard web interface for real-time monitoring
- Database integration (SQLite/PostgreSQL)
- Emotion detection
- Smart alerts for low concentration
- Export reports (PDF/Excel)
- Multi-camera support
- Cloud integration

## License

MIT License - Feel free to use and modify for your needs.
