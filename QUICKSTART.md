# Quick Start Guide - Classroom Monitoring System

## 🚀 Quick Start (3 steps)

### 1. Check System
```bash
cd ~/classroom_ai
python3 check_system.py
```

### 2. Run Monitoring
```bash
# Auto-detect camera type
bash run.sh

# OR manually choose:
python3 classroom_monitor.py         # Generic camera/USB
python3 classroom_monitor_picam.py   # Raspberry Pi Camera AI
```

### 3. Use the System
- **Session starts automatically** when you run the script
- **First 60 seconds**: People marked as "on-time"
- **After 60 seconds**: People marked as "late"
- **Press 'q' or ESC** to quit

---

## 📊 What You'll See

### Live Video Display:
```
┌─────────────────────────────────────────────┐
│ Session: ON-TIME WINDOW (45s remaining)    │
│ Total: 3 | On-time: 2 | Late: 1            │
│ Overall Concentration: 78.5%               │
│ FPS: 18.2                                  │
├─────────────────────────────────────────────┤
│                                             │
│  [Green Box] = On-time student             │
│  asad (0.82)                               │
│  Status: on-time                           │
│  Looking: Forward                          │
│                                             │
│  [Orange Box] = Late arrival               │
│  maaz (0.76)                               │
│  Status: late                              │
│  Looking: Away                             │
│                                             │
└─────────────────────────────────────────────┘
```

### CSV Logs Generated:

**logs/attendance.csv:**
```csv
timestamp,name,status,similarity
2026-02-21 10:00:05,asad,on-time,0.782
2026-02-21 10:00:15,maaz,on-time,0.823
2026-02-21 10:01:30,makarim,late,0.791
```

**logs/concentration.csv:**
```csv
timestamp,name,looking_forward,yaw,pitch,roll
2026-02-21 10:00:15,asad,yes,5.23,-2.11,1.45
2026-02-21 10:00:25,maaz,no,35.67,8.23,0.91
```

---

## ⚙️ Configuration

Edit [config.py](config.py) to adjust settings:

```python
# Change on-time window to 20 minutes (production)
ON_TIME_WINDOW_SECONDS = 1200

# Make recognition more/less strict
RECOGNITION_THRESHOLD = 0.45  # Lower = lenient, Higher = strict

# Adjust performance
FRAME_SKIP = 2       # Higher = faster, but less responsive
CAMERA_WIDTH = 640   # Lower = faster
CAMERA_HEIGHT = 480
```

---

## 🎯 Key Features

### 1. Smart Attendance
- ✅ Counts each person only once (no duplicates)
- ✅ Time-based status (on-time vs late)
- ✅ Logs timestamp for each arrival
- ✅ Real-time count display

### 2. Concentration Tracking  
- ✅ Detects head pose (looking forward/away)
- ✅ Tracks concentration per student
- ✅ Shows overall classroom concentration
- ✅ Logs concentration events

### 3. Performance Optimized
- ✅ Low latency for Pi Camera AI
- ✅ Frame skipping for speed
- ✅ Efficient face recognition
- ✅ Real-time FPS display

---

## 📝 Understanding the System

### Attendance Logic:
```
1. Camera detects face
2. Face recognition runs
3. If recognized AND NEW person:
   - Check time elapsed
   - If <= 60s: Mark "on-time"
   - If > 60s: Mark "late"
   - Log to attendance.csv
   - Increment count by 1
4. If already seen:
   - Skip (no duplicate counting)
   - Still monitor for concentration
```

### Concentration Logic:
```
1. For each detected face:
2. Analyze head pose (yaw, pitch, roll)
3. Check if angles within thresholds:
   - Yaw (left/right): < 25°
   - Pitch (up/down): < 20°
4. If YES → Looking forward
   If NO → Looking away
5. Update metrics and log periodically
```

---

## 🐛 Troubleshooting

### Camera Not Detected
```bash
# Check available cameras
ls /dev/video*

# Try different camera index in config.py
CAMERA_INDEX = 1  # or 2, 3...

# For Pi Camera, enable it first:
sudo raspi-config
# Interface Options → Camera → Enable
```

### Low Recognition Accuracy
1. **Add more photos** to each person's folder (3-5 recommended)
2. **Lower threshold** in config.py: `RECOGNITION_THRESHOLD = 0.40`
3. **Use clear, well-lit photos** from different angles
4. **Ensure test environment** matches training photos

### Slow Performance / Low FPS
1. **Increase frame skip**: `FRAME_SKIP = 3` or `4`
2. **Lower resolution**: `CAMERA_WIDTH = 320`, `CAMERA_HEIGHT = 240`
3. **Close other apps** to free resources
4. **Reduce known faces** if possible

---

## 📁 File Structure

```
classroom_ai/
├── classroom_monitor.py         ← Main system (generic camera)
├── classroom_monitor_picam.py   ← Pi Camera AI optimized version
├── config.py                    ← Configuration settings
├── check_system.py              ← System verification tool
├── setup.sh                     ← Dependency installer
├── run.sh                       ← Auto-detect and run
├── README.md                    ← Full documentation
│
├── known_faces/                 ← Face database
│   ├── person1/
│   │   ├── photo1.jpg
│   │   └── photo2.jpg
│   └── person2/
│       └── photos...
│
└── logs/                        ← Generated logs
    ├── attendance.csv
    └── concentration.csv
```

---

## 🔧 Advanced Usage

### Change to 20 Minutes for Real Class:
```python
# In config.py
ON_TIME_WINDOW_SECONDS = 1200  # 20 minutes
```

### Enable Button-Start Instead of Auto-Start:
In [classroom_monitor.py](classroom_monitor.py), modify the main loop:
```python
# Wait for 's' key to start session
print("Press 's' to start attendance session...")
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        attendance = AttendanceTracker()  # Start here
        break
```

### Export Data to Excel:
```python
import pandas as pd

# Read CSV
df = pd.read_csv('logs/attendance.csv')

# Export to Excel
df.to_excel('attendance_report.xlsx', index=False)
```

---

## 🎓 For Production Deployment

1. **Adjust timing**: Set `ON_TIME_WINDOW_SECONDS = 1200` (20 min)
2. **Optimize camera**: Set `CAMERA_WIDTH = 1280`, `CAMERA_HEIGHT = 720`
3. **Stricter recognition**: Set `RECOGNITION_THRESHOLD = 0.50`
4. **Test thoroughly**: Run for a full session with real students
5. **Backup logs**: Regularly copy CSV files to secure location
6. **Monitor performance**: Check FPS stays above 10-15

---

## 💡 Tips

1. **Best camera placement**: 
   - Mount at eye level
   - Good lighting (avoid backlighting)
   - Cover classroom entrance
   - 2-4 meters from subjects

2. **Best face photos**:
   - Clear, front-facing
   - Good lighting
   - Multiple angles (front, slight left, slight right)
   - No sunglasses or masks
   - 3-5 photos per person

3. **For best accuracy**:
   - Add photos in similar lighting to classroom
   - Update database periodically with new photos
   - Test with all students before first real use

---

## 📞 Need Help?

1. Run system check: `python3 check_system.py`
2. Check logs in `logs/` directory for errors
3. Review [README.md](README.md) for detailed info
4. Test with single image first: `python3 test_recognition.py`

---

**Happy Monitoring! 🎓📹**
