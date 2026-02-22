# Classroom AI System - Complete Guide

## 🎓 System Overview

Your complete AI-powered classroom monitoring system with 3 main components:

### 1. **Face Recognition + Attendance** ✅
- Automatic attendance tracking (ON-TIME / LATE)
- Real-time face recognition
- CSV logging

### 2. **Concentration Monitoring** 🔧
- Head pose detection (looking forward/away)
- Per-student concentration scores
- Overall class concentration tracking

### 3. **Whiteboard OCR + Notes** 📝
- Automatic whiteboard capture
- OCR text extraction
- AI-generated lecture notes

### 4. **Interactive Engagement** 🎮 NEW!
- Auto-triggers when concentration < 40%
- AI-generated quizzes from lecture content
- Mobile-friendly web interface
- Instant feedback and analytics

---

## 🚀 Complete Setup

### Install Everything:
```bash
cd ~/classroom_ai

# Core system
bash setup.sh

# Whiteboard OCR
bash whiteboard_notes/setup.sh

# Interactive engagement
bash interactive_polls/setup.sh
```

### Set Up API Key:
```bash
# Get free key: https://makersuite.google.com/app/apikey
echo "GOOGLE_API_KEY=your_key_here" > .env
```

---

## 📋 Quick Usage

### Basic Monitoring (Attendance + Concentration):
```bash
bash run.sh
```

### With Whiteboard OCR:
```bash
# Terminal 1: Face + Concentration monitoring
bash run.sh

# Terminal 2: Whiteboard monitoring
bash whiteboard_notes/run_monitor.sh

# After class: Generate notes
python whiteboard_notes/generate_notes.py
```

### With Interactive Engagement:
```bash
# Terminal 1: Face + Concentration monitoring
bash run.sh

# Terminal 2: Activity trigger (watches concentration)
python interactive_polls/monitor_and_trigger.py
```

### Full System (All Features):
```bash
# Terminal 1: Main monitoring
bash run.sh

# Terminal 2: Whiteboard OCR
bash whiteboard_notes/run_monitor.sh

# Terminal 3: Engagement trigger
python interactive_polls/monitor_and_trigger.py
```

---

## 🎯 Typical Workflow

### Before Class:
1. Start face recognition: `bash run.sh`
2. Position camera for whiteboard view
3. Start whiteboard monitor (optional)
4. Start engagement monitor (optional)

### During Class:
- System tracks attendance automatically
- Monitors concentration in real-time
- Captures whiteboard content as written
- Triggers interactive quiz if concentration drops

### After Class:
- Stop all systems (Ctrl+C)
- Generate notes: `python whiteboard_notes/generate_notes.py`
- Review analytics: Check logs/ and interactive_polls/ folders

---

## 📁 Project Structure

```
classroom_ai/
├── classroom_monitor_picam.py    # Main monitoring system
├── config.py                     # Configuration
├── run.sh                        # Quick start
├── .env                          # API keys (create this)
│
├── known_faces/                  # Face embeddings
│   ├── asad/
│   ├── maaz/
│   └── makarim/
│
├── logs/                         # Attendance + concentration logs
│   ├── attendance.csv
│   └── concentration.csv
│
├── whiteboard_notes/             # OCR system
│   ├── wb_config.py
│   ├── whiteboard_monitor.py
│   ├── generate_notes.py
│   ├── captures/                 # Whiteboard images
│   ├── raw_ocr.txt              # Extracted text
│   └── lecture_notes.md         # AI-generated notes
│
└── interactive_polls/            # Engagement system
    ├── poll_config.py
    ├── quiz_generator.py
    ├── quiz_server.py
    ├── monitor_and_trigger.py
    ├── current_quiz.json        # Active quiz
    └── quiz_results.json        # Student responses
```

---

## ⚙️ Configuration Files

### Main System: `config.py`
```python
RECOGNITION_THRESHOLD = 0.40
LOOKING_FORWARD_YAW_THRESHOLD = 25
LOOKING_FORWARD_PITCH_THRESHOLD = 20
```

### Whiteboard: `whiteboard_notes/wb_config.py`
```python
CAPTURE_INTERVAL = 30
OCR_ENGINE = 'tesseract'
LLM_PROVIDER = 'gemini'
```

### Engagement: `interactive_polls/poll_config.py`
```python
CONCENTRATION_THRESHOLD = 40
NUM_QUESTIONS = 5
QUIZ_DURATION = 180
```

---

## 🔧 Troubleshooting

### Camera not working:
```bash
libcamera-still -o test.jpg
```

### Face not recognized:
- Lower threshold in config.py
- Add more training images to known_faces/
- Check lighting conditions

### Concentration stuck at 0%:
```bash
# Calibrate pose thresholds
bash calibrate.sh
```

### Whiteboard OCR poor quality:
- Improve lighting
- Increase camera resolution
- Try different OCR engine

### Quiz not triggering:
- Check concentration threshold
- Verify cooldown period
- Ensure content is available

---

## 📊 View Results

```bash
# Attendance log
cat logs/attendance.csv

# Concentration log
cat logs/concentration.csv

# Lecture notes
cat whiteboard_notes/lecture_notes.md

# Quiz results
cat interactive_polls/quiz_results.json
```

---

## 🎓 Features Summary

| Feature | Status | Command |
|---------|--------|---------|
| Face Recognition | ✅ Working | `bash run.sh` |
| Attendance Tracking | ✅ Working | Automatic |
| Concentration Monitoring | 🔧 Needs calibration | `bash calibrate.sh` |
| Whiteboard OCR | ✅ Ready | `bash whiteboard_notes/run_monitor.sh` |
| AI Note Generation | ✅ Ready | `python whiteboard_notes/generate_notes.py` |
| Interactive Quizzes | ✅ Ready | `python interactive_polls/monitor_and_trigger.py` |

---

## 🆘 Getting Help

Check detailed docs:
- [Main System](README.md)
- [Whiteboard OCR](whiteboard_notes/QUICKSTART.md)
- [Interactive Engagement](interactive_polls/README.md)

---

## 🎯 Next Steps

1. ✅ Test face recognition
2. 🔧 Calibrate concentration (run `bash calibrate.sh`)
3. ✅ Set up Gemini API key
4. ✅ Test whiteboard OCR
5. ✅ Test interactive quiz
6. 🎓 Run full system during class!

**Ready to go? Start with:** `bash run.sh`
