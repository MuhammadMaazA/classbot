# Whiteboard OCR Notes - Quick Start

## 🎯 What This Does

1. **Monitors** whiteboard with Pi camera
2. **Detects** when professor writes new content  
3. **Captures** images automatically
4. **Extracts** text using OCR
5. **Generates** organized notes using AI

---

## 📦 Setup (One Time)

```bash
cd ~/classroom_ai
bash whiteboard_notes/setup.sh
```

**Choose OCR engine when prompted:**
- **Tesseract** - Fast, good for printed text (recommended for Pi)
- **EasyOCR** - Better accuracy, handles handwriting
- **PaddleOCR** - Best accuracy, but slower
- **All** - Install everything (for testing)

**Optional: Set up LLM API key**

Create `.env` file in `classroom_ai/` folder:
```bash
echo "GOOGLE_API_KEY=your_key_here" > .env
# OR
echo "OPENAI_API_KEY=your_key_here" > .env
```

Get free API keys:
- Google Gemini: https://makersuite.google.com/app/apikey (recommended - free tier)
- OpenAI: https://platform.openai.com/api-keys

---

## 🚀 Usage

### Option 1: Quick Start (Recommended)
```bash
bash whiteboard_notes/run_monitor.sh
```

### Option 2: Manual Run
```bash
source ~/classroom_env/bin/activate
python whiteboard_notes/whiteboard_monitor.py
```

---

## 🎮 Controls During Monitoring

- **`s`** - Force capture (manual snapshot)
- **`c`** - Clear reference frame (reset motion detection)
- **`q` - Quit

---

## ⚙️ Configuration

Edit `whiteboard_notes/wb_config.py`:

```python
# How often to check for changes (seconds)
CAPTURE_INTERVAL = 30

# How much motion triggers capture (percentage)
MOTION_THRESHOLD = 5.0

# OCR engine: 'tesseract', 'easyocr', 'paddleocr'
OCR_ENGINE = 'tesseract'

# LLM for notes: 'openai', 'gemini', 'anthropic', 'none'
LLM_PROVIDER = 'openai'
```

---

## 📝 Generate Notes from Captured Text

After monitoring session:

```bash
python whiteboard_notes/generate_notes.py
```

This creates: `whiteboard_notes/lecture_notes.md`

---

## 🧪 Test OCR on an Image

```bash
# Take a photo of whiteboard first
python whiteboard_notes/test_ocr.py path/to/image.jpg
```

---

## 📁 Output Files

```
whiteboard_notes/
├── captures/              # Captured images
│   ├── capture_20260222_140530.jpg
│   └── capture_20260222_141005.jpg
├── raw_ocr.txt           # All extracted text
└── lecture_notes.md      # AI-generated notes
```

---

## 🔧 Troubleshooting

### Camera not working
```bash
# Test camera
libcamera-still -o test.jpg
```

### OCR not detecting text
- Increase camera resolution in `wb_config.py`
- Adjust lighting (whiteboard should be well-lit)
- Try different OCR engine
- Test with `test_ocr.py` first

### No motion detected
- Lower `MOTION_THRESHOLD` (try 2.0 or 3.0)
- Press `c` to clear reference frame
- Press `s` to force manual capture

### LLM not working
- Check API key in `.env` file
- Verify internet connection
- Set `LLM_PROVIDER = 'none'` to disable AI processing

---

## 💡 Tips

1. **Position camera** to have clear view of entire whiteboard
2. **Good lighting** is crucial for OCR accuracy
3. **Start monitoring** before lecture begins
4. **Press 's'** to manually capture important content
5. **Generate notes** after class ends

---

## 🎓 Example Workflow

```bash
# 1. Start monitoring before class
bash whiteboard_notes/run_monitor.sh

# 2. Let it run during lecture
# - Auto-captures when prof writes
# - Press 's' for important sections

# 3. Stop with 'q' after class

# 4. Generate organized notes
python whiteboard_notes/generate_notes.py

# 5. View notes
cat whiteboard_notes/lecture_notes.md
```

---

## 📊 System Status

Check captures:
```bash
ls -lh whiteboard_notes/captures/
```

View raw OCR text:
```bash
cat whiteboard_notes/raw_ocr.txt
```

View generated notes:
```bash
cat whiteboard_notes/lecture_notes.md
```
