# Interactive Engagement System

## 🎯 Overview

Automatically triggers interactive quizzes/polls when class concentration drops below 40%.

### How It Works:
```
Monitor Concentration → Drops Below 40% → AI Generates Quiz → Students Engage → Boost Attention
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd ~/classroom_ai
source ~/classroom_env/bin/activate
pip install flask qrcode[pil]
```

### 2. Set Up API Key
```bash
echo "GOOGLE_API_KEY=your_key_here" >> .env
```
Get key from: https://makersuite.google.com/app/apikey

### 3. Test System

**Test Quiz Generation:**
```bash
python interactive_polls/quiz_generator.py
```

**Test Web Interface:**
```bash
python interactive_polls/quiz_server.py
```
Open http://localhost:8080 in browser

---

## ⚙️ Configuration

Edit `interactive_polls/poll_config.py`:

```python
# Trigger threshold (%)
CONCENTRATION_THRESHOLD = 40

# Quiz settings
NUM_QUESTIONS = 5
QUIZ_DURATION = 180  # 3 minutes
DIFFICULTY = 'medium'

# Cooldown between activities (seconds)
MIN_TIME_BETWEEN_ACTIVITIES = 600  # 10 minutes
```

---

## 🎮 How to Use During Class

### Option 1: Automatic (Recommended)
The system monitors concentration automatically and triggers when needed.

### Option 2: Manual Trigger
Press a key during monitoring to manually launch quiz.

---

## 📱 Student Access

When quiz is triggered, students see:
1. **Main display**: URL + QR code
2. **Access quiz**: Open URL on phone/laptop
3. **Answer questions**: Interactive, mobile-friendly interface
4. **See results**: Instant feedback

**URL format:** `http://192.168.1.78:8080`

---

## 📊 What Gets Generated

### Quiz Types:
- **Multiple Choice** - Test understanding (points awarded)
- **True/False** - Quick checks (points awarded)
- **Polls** - Opinion questions (no wrong answer)
- **Open-ended** - Discussion starters

### Content Sources:
- Recent whiteboard captures (OCR text)
- Audio transcription (if enabled)
- Last 15 minutes of lecture

### AI Processing:
- Analyzes recent content
- Identifies key concepts
- Generates relevant questions
- Adapts difficulty level
- Makes it engaging and fun

---

## 🎯 Benefits

1. **Re-engage students** when attention drops
2. **Reinforce learning** with immediate review
3. **Interactive break** from lecture format
4. **Gauge understanding** with polls
5. **Boost energy** with gamification
6. **Track participation** and results

---

## 📈 Analytics

View engagement data:
```bash
cat interactive_polls/engagement_analytics.csv
```

View quiz results:
```bash
cat interactive_polls/quiz_results.json
```

---

## 🔧 Troubleshooting

### Students can't access quiz
- Check Pi's IP: `hostname -I`
- Make sure port 8080 is open
- Students must be on same WiFi network

### Quiz not generating
- Check API key in .env file
- Verify internet connection
- Check for lecture content (whiteboard/audio)

### No trigger happening
- Check concentration threshold in config
- Verify cooldown period hasn't been reached
- Check MIN_TIME_BETWEEN_ACTIVITIES setting

---

## 💡 Tips

1. **Test before class** - Run test quiz to ensure everything works
2. **Show QR code** - Display on projector for easy mobile access
3. **Announce trigger** - Let students know an activity is starting
4. **Review results** - Use data to identify confusing topics
5. **Adjust threshold** - Tune based on your class dynamics

---

## 🎓 Example Workflow

```
Class starts → Face recognition running → Concentration tracking
      ↓
Concentration drops to 35%
      ↓
🚨 TRIGGER! System automatically:
   1. Gathers last 15min of whiteboard text
   2. Sends to Gemini AI
   3. Generates 5 engaging questions
   4. Launches web server
   5. Displays URL + QR code
      ↓
Students scan QR code → Access quiz → Answer questions
      ↓
3 minutes later → Results shown → Continue lecture
      ↓
10-minute cooldown before next possible trigger
```

---

## 📁 Files Structure

```
interactive_polls/
├── poll_config.py           # Configuration
├── quiz_generator.py        # AI quiz generation
├── quiz_server.py           # Web interface
├── concentration_trigger.py # Auto-trigger logic
├── current_quiz.json        # Active quiz data
├── quiz_results.json        # Student responses
└── engagement_analytics.csv # Analytics data
```

---

## 🧪 Testing Commands

```bash
# Generate sample quiz
python interactive_polls/quiz_generator.py

# Start web server
python interactive_polls/quiz_server.py

# Test trigger logic
python interactive_polls/concentration_trigger.py

# Test full integration
python classroom_monitor_picam.py --enable-activities
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Set up API key
3. ✅ Test quiz generation
4. ✅ Test web interface
5. ✅ Run with classroom monitor
6. ✅ Monitor and adjust threshold
