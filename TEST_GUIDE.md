# Classroom AI - Testing Guide

This guide will help you test all the implemented features step by step.

## Prerequisites

1. **Raspberry Pi camera** properly connected and working
2. **Python virtual environment** - All packages are installed in venv for isolation

## Quick Start (Fastest Way)

```bash
cd ~/classroom_ai
bash setup.sh          # Creates venv and installs everything
bash run.sh            # Runs the system
```

Or for just camera testing:
```bash
bash quick_test.sh     # Quick camera test with auto-setup
```

## Step 1: Verify Camera Connection

Test the camera using the rpicam command:

```bash
# Test still image capture
rpicam-still -o test.jpg

# Test video preview (5 seconds)
rpicam-hello -t 5000
```

If these work, your camera hardware is properly connected.

## Step 2: Test Python Camera Integration

Run the camera test script to verify picamera2 works with Python:

```bash
cd ~/classroom_ai

# Option 1: Quick test (auto-setup)
bash quick_test.sh

# Option 2: Manual with venv
source venv/bin/activate
python3 test_camera.py
```

**Expected behavior:**
- Should display live camera feed in a window
- FPS counter should update every second
- Press 's' to save a test image
- Press 'q' to quit

**What this tests:**
- picamera2 library installation
- Camera initialization
- Frame capture and conversion
- OpenCV display

## Step 3: Check Known Faces

Verify you have face images set up:

```bash
ls -la ~/classroom_ai/known_faces/
```

**Expected structure:**
```
known_faces/
├── asad/
│   ├── photo1.jpg
│   └── photo2.jpg
├── maaz/
│   ├── photo1.jpg
│   └── photo2.jpg
└── makarim/
    ├── photo1.jpg
    └── photo2.jpg
```

Each person should have 2-5 clear face photos.

## Step 4: Test Face Recognition

Test if the face recognition model is working:

```bash
python3 test_recognition.py
```

This will load the known faces and test the recognition system.

## Step 5: Run the Full System

Now run the complete classroom monitoring system:

```bash
# Using the automatic detection script
bash run.sh

# OR run directly with Pi Camera version
python3 classroom_monitor_picam.py
```

**Expected behavior:**
1. Loads InsightFace model (takes ~5-10 seconds)
2. Loads known faces from known_faces/ directory
3. Starts camera feed
4. Displays window with:
   - Live video feed
   - Face detection boxes
   - Name labels and similarity scores
   - Attendance tracking (on-time/late)
   - Concentration monitoring
   - Stats panel (FPS, attendance count, etc.)

## Step 6: Test Features

### 6.1 Attendance Tracking

**Test on-time marking:**
1. Start the system
2. Within the first 60 seconds (on-time window), step in front of the camera
3. You should see your name labeled as "ON-TIME" in green
4. Check the terminal output for: `[ATTENDANCE] <name> marked as ON-TIME`

**Test late marking:**
1. Wait for 60+ seconds after starting
2. Step in front of the camera
3. You should see your name labeled as "LATE" in yellow
4. Check terminal output for: `[ATTENDANCE] <name> marked as LATE`

### 6.2 Concentration Monitoring

**Test forward detection:**
- Look directly at the camera
- Face box should have a green "FORWARD" indicator
- Arrow should point forward

**Test away detection:**
- Turn your head left/right more than ~25 degrees
- Or tilt up/down more than ~20 degrees
- Face box should have a red "AWAY" indicator
- Arrow should point in the direction you're looking

### 6.3 Multiple People

If you have multiple people:
1. All faces should be detected simultaneously
2. Each person should be labeled with their own name
3. Separate concentration tracking for each person

## Step 7: Check Logs

After running the system, check the generated logs:

```bash
# View attendance log
cat ~/classroom_ai/logs/attendance.csv

# View concentration log
cat ~/classroom_ai/logs/concentration.csv

# Or open with a spreadsheet program
libreoffice ~/classroom_ai/logs/attendance.csv
```

**Attendance log format:**
```
timestamp,name,status,similarity
2026-02-22 10:00:15,asad,on-time,0.876
2026-02-22 10:01:30,maaz,late,0.823
```

**Concentration log format:**
```
timestamp,name,looking_forward,yaw,pitch,roll
2026-02-22 10:00:20,asad,yes,-5.32,3.21,1.45
2026-02-22 10:00:30,asad,no,35.21,-2.45,0.89
```

## Controls

While the system is running:
- **'q' or ESC**: Quit the program
- The system will display a summary on exit

## Troubleshooting

### Issue: "picamera2 not available"

**Solution:**
```bash
sudo apt update
sudo apt install -y python3-picamera2
```

### Issue: "No known faces loaded"

**Solution:**
- Check that known_faces/ directory exists
- Ensure each person has their own subfolder
- Verify images are .jpg, .jpeg, or .png format
- Images should contain clear, frontal face photos

### Issue: Camera not working

1. Check hardware connection:
```bash
rpicam-hello -t 5000
```

2. Check if camera is enabled:
```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

3. Reboot if needed:
```bash
sudo reboot
```

### Issue: Low FPS or lag

**Solutions:**
- Increase FRAME_SKIP in config.py (e.g., from 2 to 3 or 4)
- Reduce camera resolution in config.py
- Close other applications

### Issue: False recognitions

**Solutions:**
- Increase RECOGNITION_THRESHOLD in config.py (e.g., from 0.45 to 0.50)
- Add more varied photos of each person
- Ensure good lighting

## Performance Tips

1. **Optimize for speed:**
   - Edit `config.py`:
   ```python
   FRAME_SKIP = 3  # Process every 3rd frame instead of every 2nd
   CAMERA_WIDTH = 640  # Use lower resolution
   CAMERA_HEIGHT = 480
   ```

2. **Better accuracy:**
   ```python
   FRAME_SKIP = 1  # Process every frame
   RECOGNITION_THRESHOLD = 0.50  # Stricter matching
   ```

3. **Monitor resources:**
   ```bash
   # In another terminal
   htop
   ```

## Expected Performance

On Raspberry Pi 4/5:
- **FPS:** 8-15 fps (with FRAME_SKIP=2)
- **Detection latency:** < 500ms
- **Recognition accuracy:** > 90% with good photos

## Next Steps

After successful testing:

1. **Adjust timing for production:**
   ```python
   # In config.py
   ON_TIME_WINDOW_SECONDS = 1200  # 20 minutes instead of 60 seconds
   ```

2. **Set up autostart (optional):**
   ```bash
   # Add to crontab
   @reboot sleep 30 && cd ~/classroom_ai && bash run.sh
   ```

3. **Regular monitoring:**
   - Check logs daily
   - Review concentration patterns
   - Adjust thresholds as needed

## Summary of What's Implemented

✓ **Face Detection:** Using InsightFace (SCRFD detector)
✓ **Face Recognition:** Embeddings with cosine similarity
✓ **Attendance Tracking:** On-time vs late detection
✓ **Concentration Monitoring:** Head pose analysis (yaw, pitch, roll)
✓ **CSV Logging:** Timestamped records
✓ **Live Visualization:** Real-time display with overlays
✓ **Pi Camera Support:** Native picamera2 integration
✓ **Performance Optimization:** Frame skipping, low latency config

## Support

If you encounter any issues:
1. Check error messages in terminal
2. Verify all dependencies are installed: `bash setup.sh`
3. Test camera independently: `python3 test_camera.py`
4. Check logs for more details
