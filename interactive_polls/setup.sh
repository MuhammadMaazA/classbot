#!/bin/bash
# Setup script for Interactive Engagement System

echo "=========================================="
echo "Interactive Engagement System - Setup"
echo "=========================================="

source ~/classroom_env/bin/activate

echo ""
echo "Installing dependencies..."
pip install flask qrcode[pil] pillow

echo ""
echo "✓ Installation complete!"
echo ""
echo "=========================================="
echo "SETUP CHECKLIST"
echo "=========================================="
echo ""
echo "1. Set up Gemini API key:"
echo "   Get free key from: https://makersuite.google.com/app/apikey"
echo "   Then run: echo 'GOOGLE_API_KEY=your_key' >> .env"
echo ""
echo "2. Test quiz generation:"
echo "   python interactive_polls/quiz_generator.py"
echo ""
echo "3. Test web interface:"
echo "   python interactive_polls/quiz_server.py"
echo "   Open: http://localhost:8080"
echo ""
echo "4. Configure settings (optional):"
echo "   Edit: interactive_polls/poll_config.py"
echo ""
echo "=========================================="
