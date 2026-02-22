#!/bin/bash
# Setup script for Whiteboard OCR Notes System

echo "=========================================="
echo "Whiteboard OCR Notes - Setup"
echo "=========================================="

source ~/classroom_env/bin/activate

echo ""
echo "Installing OCR and image processing libraries..."
echo ""

# Image processing
pip install opencv-python-headless Pillow

# OCR engines
echo "Select OCR engine:"
echo "1. Tesseract (lightweight, fast, good for clear text)"
echo "2. EasyOCR (better accuracy, slower, supports handwriting)"
echo "3. PaddleOCR (best accuracy, Chinese support, moderate speed)"
echo "4. Install all (recommended for testing)"
read -p "Choice (1/2/3/4): " ocr_choice

case $ocr_choice in
  1)
    echo "Installing Tesseract..."
    sudo apt-get install -y tesseract-ocr libtesseract-dev
    pip install pytesseract
    ;;
  2)
    echo "Installing EasyOCR..."
    pip install easyocr
    ;;
  3)
    echo "Installing PaddleOCR..."
    pip install paddlepaddle paddleocr
    ;;
  4)
    echo "Installing all OCR engines..."
    sudo apt-get install -y tesseract-ocr libtesseract-dev
    pip install pytesseract easyocr
    pip install paddlepaddle paddleocr
    ;;
esac

# LLM integration
echo ""
echo "Installing LLM libraries..."
pip install openai google-generativeai anthropic

# Other utilities
pip install python-dotenv

echo ""
echo "✓ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Calibrate whiteboard: python whiteboard_notes/calibrate_whiteboard.py"
echo "2. Test OCR: python whiteboard_notes/test_ocr.py <image.jpg>"
echo "3. Start monitoring: python whiteboard_notes/whiteboard_monitor.py"
echo ""
echo "Optional: Set up API keys in .env file:"
echo "  OPENAI_API_KEY=your_key"
echo "  GOOGLE_API_KEY=your_key"
echo "  ANTHROPIC_API_KEY=your_key"
