# AegisAI Classroom - Project Story

## Inspiration

Traditional classroom management relies on manual attendance and subjective engagement assessment. Teachers constantly juggle between delivering content and monitoring dozens of students. We envisioned an intelligent system that could **autonomously track attendance, measure concentration, and adapt in real-time** - freeing educators to focus on what matters: teaching.

## What it does

**AegisAI Classroom** is a multi-modal AI monitoring system that transforms any classroom into an intelligent learning environment:

- 🎯 **Automatic Attendance**: Face recognition with InsightFace (0.40 threshold) logs students the moment they arrive - no roll call needed
- 🧠 **Live Concentration Tracking**: Head pose estimation monitors engagement by detecting when students look away (±25° yaw, ±20° pitch tolerance)
- 🌡️ **Environmental Intelligence**: ESP32 sensors measure temperature, humidity, light, and noise levels - correlating physical comfort with learning outcomes
- 📊 **Real-time Dashboard**: Glassmorphism UI displays attendance rates, concentration metrics, and environmental data updating every 2 seconds
- 🎮 **Adaptive Engagement**: When class concentration drops below 40%, the system automatically triggers interactive quizzes to re-engage students
- 📝 **Whiteboard OCR**: Automatically captures and digitizes board notes using EasyOCR

## How we built it

**Hardware Stack:**
- Raspberry Pi 5 (4GB) with IMX477 camera module (640x480 @ 30fps)
- ESP32 with AHT20 (temperature/humidity), BMP280 (pressure), LDR (light), analog microphone (noise)
- Custom sensor dashboard with TFT display and I2S audio alerts

**Software Architecture:**
- **Vision Pipeline**: InsightFace buffalo_l model for ArcFace embeddings, MediaPipe for pose estimation
- **Backend**: Python with Flask serving REST APIs, CSV-based logging for persistence
- **Frontend**: Modern dashboard with glassmorphism design, auto-refreshing stats via AJAX
- **IoT Integration**: ESP32 posts sensor data every ~1-2 seconds via HTTP POST to Pi
- **AI Features**: Google Gemini API for quiz generation (with fallback when quota exceeded)

**Key Implementation Details:**
- Face recognition at 0.40 similarity threshold balances accuracy vs false positives
- 30-second attendance window ensures real-time presence tracking
- Concentration uses raw pose angles (fixed double-degree conversion bug)
- Dashboard caches stats for 0.5s to reduce disk I/O

## Challenges we ran into

1. **Network Topology Hell**: ESP32 on WiFi, Pi on Ethernet - spent hours debugging -1 POST errors before realizing they couldn't see each other. Solution: Connected Pi to iPhone WiFi hotspot.

2. **The Degree Disaster**: Concentration showed students at 1799° angles! Discovered MediaPipe returns degrees, but we were calling `np.degrees()` again. Fixed by reading the docs.

3. **Git Catastrophe**: Accidentally pushed `.env` with Google API key to public repo. Had to force-push history rewrite and revoke the key. Lesson: ALWAYS create `.gitignore` first.

4. **CSV Format Chaos**: Dashboard showed stale data because attendance logging used lowercase "on-time" but parser expected uppercase. Fixed with `.lower()` comparisons.

5. **Time Window Tuning**: Initially used all-time attendance data (students from hours ago still showed "present"). Narrowed to 5 minutes, then 30 seconds for real-time accuracy.

## Accomplishments that we're proud of

- ✨ **Zero Manual Intervention**: System runs fully autonomously - just point the camera and go
- 🚀 **Real-time Everything**: Sub-second face recognition, 2-second dashboard updates, immediate sensor sync
- 🎨 **Production-Ready UI**: Not a wireframe - actual glassmorphism design that looks professional
- 🔧 **Hardware-Software Integration**: ESP32 → WiFi → Pi → Dashboard → Browser - entire IoT pipeline working
- 🧪 **Robust Error Handling**: Survived WiFi drops, sensor failures, API quota exhaustion, and Git disasters
- 📈 **Scalable Architecture**: CSV logs + caching means system handles hours of data without lag

## What we learned

**Technical:**
- InsightFace buffalo_l offers excellent speed/accuracy tradeoff for real-time face recognition
- Pose estimation requires careful coordinate system understanding (degrees vs radians vs pixels)
- Time-windowed data drastically improves "liveness" perception in dashboards
- HTTP POST loops without delays can still bottleneck on network latency

**Practical:**
- Network topology matters MORE than code - wrong network = doesn't work, period
- Git hygiene isn't optional - one wrong commit can expose secrets to the world
- User testing reveals invisible bugs (why does it show 3 people when there's only 1?)
- Documentation-driven development keeps complex systems maintainable

**Meta:**
- Multi-modal sensing (vision + environmental) provides richer context than vision alone
- Real-time feedback loops (concentration → quiz) create adaptive learning environments
- Edge computing (Pi + ESP32) beats cloud for privacy-sensitive education data

## What's next for AegisAI Classroom

**Immediate Roadmap:**
- 📱 **Mobile App**: React Native companion for teachers to view stats on smartphones
- 🔔 **Smart Alerts**: Push notifications when concentration drops, absent students, or environmental issues
- 📊 **Analytics Dashboard**: Historical trends - which times/days have best engagement?
- 🎯 **Individual Tracking**: Per-student concentration timelines and personalized interventions

**Future Vision:**
- 🤖 **Predictive AI**: Machine learning to predict disengagement before it happens
- 🌐 **Multi-Room Support**: Scale to entire schools with centralized monitoring
- 🎓 **Learning Outcomes Correlation**: Link engagement metrics to exam performance
- 🔐 **Privacy Mode**: On-device processing with encrypted storage for GDPR/FERPA compliance
- 🎬 **Lecture Recording**: Auto-start recording when concentration is high, tag important moments
- 🌡️ **Climate Auto-Adjust**: API integration with smart HVAC systems for optimal learning conditions

**The Ultimate Goal**: Transform classrooms from passive spaces into intelligent learning ecosystems that adapt to students' needs in real-time, giving teachers superpowers to create better educational experiences.

---

**Built with**: Raspberry Pi, ESP32, Python, Flask, InsightFace, MediaPipe, Arduino, Love, and Too Much Coffee ☕
