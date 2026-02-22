#!/usr/bin/env python3
"""
System check script - Verifies the classroom monitoring system is ready to run
"""

import os
import sys
from pathlib import Path

def check_color(passed):
    """Return color code for pass/fail."""
    return "\033[92m✓\033[0m" if passed else "\033[91m✗\033[0m"

def main():
    print("=" * 60)
    print("CLASSROOM MONITORING SYSTEM - System Check")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Check Python version
    print("[1/8] Checking Python version...")
    python_version = sys.version_info
    python_ok = python_version.major == 3 and python_version.minor >= 7
    print(f"  {check_color(python_ok)} Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    if not python_ok:
        print("      WARNING: Python 3.7+ recommended")
    print()
    
    # Check dependencies
    print("[2/8] Checking Python dependencies...")
    deps = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'insightface': 'insightface'
    }
    
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"  {check_color(True)} {package}")
        except ImportError:
            print(f"  {check_color(False)} {package} - MISSING")
            print(f"      Install: pip3 install {package}")
            all_checks_passed = False
    
    # Check optional picamera2
    try:
        import picamera2
        print(f"  {check_color(True)} picamera2 (optional - for Pi Camera)")
    except ImportError:
        print(f"  {check_color(False)} picamera2 (optional - for Pi Camera)")
        print("      Install: sudo apt install python3-picamera2")
    print()
    
    # Check directory structure
    print("[3/8] Checking directory structure...")
    base_dir = Path.home() / "classroom_ai"
    dirs_to_check = {
        'Base directory': base_dir,
        'Known faces': base_dir / "known_faces",
        'Logs': base_dir / "logs"
    }
    
    for name, path in dirs_to_check.items():
        exists = path.exists()
        print(f"  {check_color(exists)} {name}: {path}")
        if not exists and name != 'Logs':
            all_checks_passed = False
    print()
    
    # Check known faces
    print("[4/8] Checking known faces database...")
    known_faces_dir = base_dir / "known_faces"
    
    if known_faces_dir.exists():
        people = [d for d in known_faces_dir.iterdir() if d.is_dir()]
        
        if people:
            print(f"  {check_color(True)} Found {len(people)} people:")
            
            for person_dir in people:
                images = list(person_dir.glob("*.jpg")) + list(person_dir.glob("*.jpeg")) + list(person_dir.glob("*.png"))
                images_ok = len(images) >= 2
                print(f"      {check_color(images_ok)} {person_dir.name}: {len(images)} images")
                
                if len(images) < 2:
                    print(f"          WARNING: At least 2-3 images recommended")
        else:
            print(f"  {check_color(False)} No people found in known_faces/")
            print("      Add folders for each person with their photos")
            all_checks_passed = False
    else:
        print(f"  {check_color(False)} known_faces/ directory not found")
        all_checks_passed = False
    print()
    
    # Check configuration
    print("[5/8] Checking configuration...")
    try:
        import config
        print(f"  {check_color(True)} config.py found")
        print(f"      On-time window: {config.ON_TIME_WINDOW_SECONDS}s")
        print(f"      Camera resolution: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}")
        print(f"      Frame skip: {config.FRAME_SKIP}")
        print(f"      Recognition threshold: {config.RECOGNITION_THRESHOLD}")
    except ImportError:
        print(f"  {check_color(False)} config.py not found")
        all_checks_passed = False
    print()
    
    # Check main scripts
    print("[6/8] Checking main scripts...")
    scripts = [
        'classroom_monitor.py',
        'classroom_monitor_picam.py'
    ]
    
    for script in scripts:
        script_path = Path(script)
        exists = script_path.exists()
        print(f"  {check_color(exists)} {script}")
        if not exists:
            all_checks_passed = False
    print()
    
    # Check camera availability
    print("[7/8] Checking camera...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        camera_ok = cap.isOpened()
        
        if camera_ok:
            print(f"  {check_color(True)} Camera detected")
            
            # Get camera properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"      Default resolution: {width}x{height}")
            
            cap.release()
        else:
            print(f"  {check_color(False)} No camera detected")
            print("      Make sure camera is connected and not in use")
    except Exception as e:
        print(f"  {check_color(False)} Error checking camera: {e}")
    print()
    
    # Check InsightFace model
    print("[8/8] Checking InsightFace model...")
    try:
        import insightface
        app = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
        print(f"  {check_color(True)} InsightFace model loaded")
        print("      Note: First run will download models (~200MB)")
    except Exception as e:
        print(f"  {check_color(False)} Error loading InsightFace: {e}")
        all_checks_passed = False
    print()
    
    # Final summary
    print("=" * 60)
    if all_checks_passed:
        print("✓ ALL CHECKS PASSED - System ready!")
        print()
        print("To start monitoring:")
        print("  bash run.sh")
        print()
        print("Or run directly:")
        print("  python3 classroom_monitor.py         (generic camera)")
        print("  python3 classroom_monitor_picam.py   (Pi Camera)")
    else:
        print("✗ SOME CHECKS FAILED - Please fix the issues above")
        print()
        print("Common fixes:")
        print("  1. Install dependencies: bash setup.sh")
        print("  2. Add face images to known_faces/")
        print("  3. Check camera connection")
    print("=" * 60)

if __name__ == "__main__":
    main()
