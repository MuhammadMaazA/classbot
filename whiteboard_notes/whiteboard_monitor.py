#!/usr/bin/env python3
"""
Whiteboard OCR Monitor
Captures whiteboard content, extracts text, and generates notes
"""

import cv2
import numpy as np
from picamera2 import Picamera2
import time
from datetime import datetime
import os
from PIL import Image

import wb_config as config

class WhiteboardMonitor:
    def __init__(self):
        self.last_capture_time = 0
        self.previous_frame = None
        self.capture_count = 0
        self.session_start = datetime.now()
        
        # Initialize camera
        print("Initializing camera...")
        self.picam2 = Picamera2()
        cam_config = self.picam2.create_preview_configuration(
            main={"size": config.CAMERA_RESOLUTION, "format": "RGB888"},
            controls={"FrameRate": config.CAMERA_FPS}
        )
        self.picam2.configure(cam_config)
        self.picam2.start()
        time.sleep(2)
        
        # Initialize OCR
        self.ocr = self._init_ocr()
        
        print("✓ Whiteboard monitor initialized")
    
    def _init_ocr(self):
        """Initialize selected OCR engine"""
        if config.OCR_ENGINE == 'tesseract':
            try:
                import pytesseract
                print(f"✓ Using Tesseract OCR")
                return 'tesseract'
            except ImportError:
                print("❌ Tesseract not installed. Run: sudo apt install tesseract-ocr")
                print("   pip install pytesseract")
                return None
        
        elif config.OCR_ENGINE == 'easyocr':
            try:
                import easyocr
                print("Loading EasyOCR... (this may take a moment)")
                reader = easyocr.Reader([config.OCR_LANGUAGE])
                print("✓ Using EasyOCR")
                return reader
            except ImportError:
                print("❌ EasyOCR not installed. Run: pip install easyocr")
                return None
        
        elif config.OCR_ENGINE == 'paddleocr':
            try:
                from paddleocr import PaddleOCR
                print("Loading PaddleOCR... (this may take a moment)")
                ocr = PaddleOCR(lang=config.OCR_LANGUAGE, use_angle_cls=True)
                print("✓ Using PaddleOCR")
                return ocr
            except ImportError:
                print("❌ PaddleOCR not installed. Run: pip install paddlepaddle paddleocr")
                return None
        
        return None
    
    def preprocess_image(self, image):
        """Enhance image for better OCR"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if config.ENHANCE_CONTRAST:
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
        
        if config.DENOISE:
            # Denoise
            gray = cv2.fastNlMeansDenoising(gray, h=10)
        
        if config.BINARIZE:
            # Adaptive thresholding for better text extraction
            gray = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
        
        return gray
    
    def detect_motion(self, current_frame):
        """Detect if whiteboard content has changed"""
        if self.previous_frame is None:
            self.previous_frame = current_frame.copy()
            return False
        
        # Calculate difference
        diff = cv2.absdiff(self.previous_frame, current_frame)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        
        # Calculate percentage of changed pixels
        changed_pixels = np.sum(thresh > 0)
        total_pixels = thresh.shape[0] * thresh.shape[1]
        change_percentage = (changed_pixels / total_pixels) * 100
        
        return change_percentage > config.MOTION_THRESHOLD
    
    def extract_text(self, image):
        """Extract text using configured OCR engine"""
        if self.ocr is None:
            return "[OCR not available]"
        
        # Preprocess image
        processed = self.preprocess_image(image)
        
        try:
            if config.OCR_ENGINE == 'tesseract':
                import pytesseract
                text = pytesseract.image_to_string(processed, lang=config.OCR_LANGUAGE)
            
            elif config.OCR_ENGINE == 'easyocr':
                results = self.ocr.readtext(processed)
                text = '\n'.join([result[1] for result in results])
            
            elif config.OCR_ENGINE == 'paddleocr':
                results = self.ocr.ocr(processed, cls=True)
                if results and results[0]:
                    text = '\n'.join([line[1][0] for line in results[0]])
                else:
                    text = ""
            
            else:
                text = "[Unknown OCR engine]"
            
            return text.strip()
        
        except Exception as e:
            print(f"❌ OCR Error: {e}")
            return "[OCR failed]"
    
    def save_capture(self, frame, text):
        """Save captured frame and extracted text"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if config.SAVE_IMAGES:
            # Save original image
            img_path = os.path.join(config.OUTPUT_DIR, f'capture_{timestamp}.jpg')
            cv2.imwrite(img_path, frame)
            print(f"  💾 Saved: {img_path}")
        
        # Save raw OCR text
        with open(config.RAW_TEXT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Capture: {timestamp}\n")
            f.write(f"{'='*60}\n")
            f.write(text)
            f.write(f"\n\n")
        
        return timestamp, img_path if config.SAVE_IMAGES else None
    
    def run(self):
        """Main monitoring loop"""
        print("\n" + "="*60)
        print("WHITEBOARD MONITOR")
        print("="*60)
        print(f"Capture interval: {config.CAPTURE_INTERVAL}s")
        print(f"Motion threshold: {config.MOTION_THRESHOLD}%")
        print(f"OCR Engine: {config.OCR_ENGINE}")
        print("="*60)
        print("\nPress 'q' to quit, 's' to force capture, 'c' to clear previous frame")
        print("="*60 + "\n")
        
        frame_count = 0
        
        try:
            while True:
                # Capture frame
                frame = self.picam2.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                frame_count += 1
                
                current_time = time.time()
                time_since_last = current_time - self.last_capture_time
                
                # Check for manual capture
                key = cv2.waitKey(1) & 0xFF
                force_capture = (key == ord('s'))
                
                if key == ord('c'):
                    self.previous_frame = None
                    print("✓ Cleared previous frame reference")
                
                # Detect motion
                has_motion = self.detect_motion(frame)
                
                # Decide whether to capture
                should_capture = (
                    force_capture or
                    (has_motion and time_since_last >= config.CAPTURE_INTERVAL)
                )
                
                if should_capture and time_since_last >= config.MIN_CAPTURE_DELAY:
                    print(f"\n[Frame {frame_count}] 📸 Capturing whiteboard...")
                    
                    # Extract text
                    text = self.extract_text(frame)
                    
                    if text and len(text.strip()) > 10:  # Only save if meaningful text found
                        timestamp, img_path = self.save_capture(frame, text)
                        self.capture_count += 1
                        
                        print(f"  ✓ Extracted {len(text)} characters")
                        print(f"  Preview: {text[:100]}...")
                        
                        # Update state
                        self.last_capture_time = current_time
                        self.previous_frame = frame.copy()
                    else:
                        print("  ⚠ No significant text detected, skipping")
                
                # Display preview
                if config.SHOW_PREVIEW:
                    display = frame.copy()
                    
                    # Add status overlay
                    status_color = (0, 255, 0) if has_motion else (100, 100, 100)
                    cv2.putText(display, f"Captures: {self.capture_count}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
                    cv2.putText(display, f"Motion: {'YES' if has_motion else 'NO'}", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
                    cv2.putText(display, f"Time since last: {int(time_since_last)}s", 
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
                    
                    # Resize for display
                    h, w = display.shape[:2]
                    display = cv2.resize(display, (int(w * config.PREVIEW_SCALE), 
                                                  int(h * config.PREVIEW_SCALE)))
                    
                    cv2.imshow('Whiteboard Monitor', display)
                
                # Quit
                if key == ord('q'):
                    break
                
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n\nStopping...")
        
        finally:
            self.picam2.stop()
            cv2.destroyAllWindows()
            
            print("\n" + "="*60)
            print("SESSION SUMMARY")
            print("="*60)
            print(f"Total captures: {self.capture_count}")
            print(f"Duration: {datetime.now() - self.session_start}")
            print(f"Raw text saved to: {config.RAW_TEXT_FILE}")
            print("="*60)

if __name__ == "__main__":
    monitor = WhiteboardMonitor()
    monitor.run()
