#!/usr/bin/env python3
"""
Test OCR on a single image
"""

import sys
import cv2
import numpy as np
import wb_config as config

def preprocess_image(image):
    """Same preprocessing as main monitor"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    if config.ENHANCE_CONTRAST:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
    
    if config.DENOISE:
        gray = cv2.fastNlMeansDenoising(gray, h=10)
    
    if config.BINARIZE:
        gray = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
    
    return gray

def test_ocr(image_path):
    """Test OCR on an image"""
    print(f"Testing OCR on: {image_path}")
    print(f"OCR Engine: {config.OCR_ENGINE}")
    print("="*60)
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Could not load image: {image_path}")
        return
    
    # Preprocess
    processed = preprocess_image(image)
    
    # Run OCR based on engine
    if config.OCR_ENGINE == 'tesseract':
        try:
            import pytesseract
            text = pytesseract.image_to_string(processed, lang=config.OCR_LANGUAGE)
            print(text)
        except ImportError:
            print("❌ Tesseract not installed")
            print("Install: sudo apt install tesseract-ocr")
            print("         pip install pytesseract")
    
    elif config.OCR_ENGINE == 'easyocr':
        try:
            import easyocr
            print("Loading EasyOCR...")
            reader = easyocr.Reader([config.OCR_LANGUAGE])
            results = reader.readtext(processed)
            
            print("\nExtracted Text:")
            print("="*60)
            for (bbox, text, conf) in results:
                print(f"{text} (confidence: {conf:.2f})")
        except ImportError:
            print("❌ EasyOCR not installed")
            print("Install: pip install easyocr")
    
    elif config.OCR_ENGINE == 'paddleocr':
        try:
            from paddleocr import PaddleOCR
            print("Loading PaddleOCR...")
            ocr = PaddleOCR(lang=config.OCR_LANGUAGE, use_angle_cls=True)
            results = ocr.ocr(processed, cls=True)
            
            print("\nExtracted Text:")
            print("="*60)
            if results and results[0]:
                for line in results[0]:
                    text = line[1][0]
                    conf = line[1][1]
                    print(f"{text} (confidence: {conf:.2f})")
        except ImportError:
            print("❌ PaddleOCR not installed")
            print("Install: pip install paddlepaddle paddleocr")
    
    # Show images
    print("\nDisplaying original and processed images...")
    print("Press any key to close windows")
    
    cv2.imshow('Original', image)
    cv2.imshow('Processed', processed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_ocr.py <image_path>")
        print("\nExample:")
        print("  python test_ocr.py whiteboard_notes/captures/capture_20260122_143022.jpg")
        sys.exit(1)
    
    test_ocr(sys.argv[1])
