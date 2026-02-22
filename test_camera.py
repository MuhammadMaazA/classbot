#!/usr/bin/env python3
"""
Camera Test Script - Verify rpicam/picamera2 integration
Note: Run with: source ~/classroom_env/bin/activate && python3 test_camera.py
"""

import sys
import time

print("=" * 60)
print("CAMERA TEST - Raspberry Pi Camera")
print("=" * 60)

# Test 1: Check if picamera2 is available
print("\n[TEST 1] Checking picamera2 availability...")
try:
    from picamera2 import Picamera2
    print("✓ picamera2 is installed")
    PICAMERA_AVAILABLE = True
except ImportError as e:
    print(f"✗ picamera2 not available: {e}")
    print("  Install with: sudo apt install python3-picamera2")
    PICAMERA_AVAILABLE = False

# Test 2: Check OpenCV
print("\n[TEST 2] Checking OpenCV...")
try:
    import cv2
    print(f"✓ OpenCV version: {cv2.__version__}")
except ImportError as e:
    print(f"✗ OpenCV not available: {e}")
    sys.exit(1)

# Test 3: Initialize Pi Camera
if PICAMERA_AVAILABLE:
    print("\n[TEST 3] Initializing Pi Camera...")
    try:
        picam2 = Picamera2()
        
        # Configure camera
        camera_config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"},
            controls={"FrameRate": 30}
        )
        
        picam2.configure(camera_config)
        picam2.start()
        
        print("✓ Pi Camera started successfully")
        
        # Test 4: Capture frames
        print("\n[TEST 4] Capturing test frames...")
        print("  Press 'q' to quit, 's' to save a test image")
        
        frame_count = 0
        start_time = time.time()
        
        while True:
            # Capture frame
            frame = picam2.capture_array()
            
            # Convert RGB to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            frame_count += 1
            
            # Calculate FPS every second
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"  FPS: {fps:.1f}, Frames: {frame_count}")
            
            # Display info on frame
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to quit, 's' to save", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Show frame
            cv2.imshow('Pi Camera Test', frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # q or ESC
                print("\n✓ Test completed successfully")
                break
            elif key == ord('s'):  # Save test image
                filename = f"test_capture_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"  Saved: {filename}")
        
        # Cleanup
        picam2.stop()
        cv2.destroyAllWindows()
        
        print("\n" + "=" * 60)
        print("RESULT: All tests passed!")
        print(f"Total frames captured: {frame_count}")
        print(f"Average FPS: {frame_count / (time.time() - start_time):.1f}")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
else:
    print("\n✗ Cannot run camera test - picamera2 not available")
    sys.exit(1)
