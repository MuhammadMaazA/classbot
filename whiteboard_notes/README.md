# Whiteboard OCR Notes System

## Overview
Automatically capture and transcribe whiteboard content during lectures.

## Features
1. **Whiteboard Detection** - Identify whiteboard area in camera frame
2. **Change Detection** - Capture only when new content is written
3. **Text Extraction** - OCR to extract written text
4. **Note Generation** - LLM creates structured notes
5. **Timestamp Tracking** - Know when each capture was taken

## Workflow
```
Camera Feed → Motion Detection → Whiteboard Capture → OCR → LLM Processing → Notes.md
     ↓
   Display with highlights
```

## Installation
```bash
bash whiteboard_notes/setup.sh
```

## Usage

### Basic Mode (Auto-capture)
```bash
python whiteboard_notes/whiteboard_monitor.py
```

### Manual Calibration
```bash
python whiteboard_notes/calibrate_whiteboard.py
```

### Test OCR
```bash
python whiteboard_notes/test_ocr.py test_image.jpg
```

## Configuration
Edit `whiteboard_notes/config.py`:
- Capture interval
- OCR engine (Tesseract, EasyOCR, PaddleOCR)
- LLM provider (OpenAI, Gemini, local)
- Whiteboard detection sensitivity
