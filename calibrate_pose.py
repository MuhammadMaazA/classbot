#!/usr/bin/env python3
"""
Pose Calibration Tool
Run this to find the right yaw/pitch thresholds for your camera setup
"""

import cv2
import numpy as np
from insightface.app import FaceAnalysis
from picamera2 import Picamera2
import time

def main():
    print("=" * 60)
    print("POSE CALIBRATION TOOL")
    print("=" * 60)
    print("\nThis will help you find the right pose thresholds.")
    print("\nInstructions:")
    print("1. Sit in front of the camera")
    print("2. Look DIRECTLY at the camera for 5 seconds")
    print("3. The tool will show you the typical angles\n")
    
    input("Press Enter to start...")
    
    # Initialize camera
    print("\nInitializing camera...")
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"},
        controls={"FrameRate": 30}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(2)
    
    # Initialize face detection
    print("Loading InsightFace model...")
    app = FaceAnalysis(providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 480))
    
    print("\n" + "=" * 60)
    print("LOOK AT THE CAMERA NOW!")
    print("=" * 60)
    print("Collecting data for 5 seconds...\n")
    
    yaw_values = []
    pitch_values = []
    roll_values = []
    
    start_time = time.time()
    frame_count = 0
    
    while time.time() - start_time < 5:
        frame = picam2.capture_array()
        faces = app.get(frame)
        
        if len(faces) > 0:
            face = faces[0]
            if hasattr(face, 'pose') and face.pose is not None:
                yaw, pitch, roll = face.pose[0], face.pose[1], face.pose[2]
                yaw_values.append(yaw)
                pitch_values.append(pitch)
                roll_values.append(roll)
                frame_count += 1
                print(f"Frame {frame_count}: yaw={yaw:.1f}° pitch={pitch:.1f}° roll={roll:.1f}°")
        
        time.sleep(0.1)
    
    picam2.stop()
    
    if len(yaw_values) == 0:
        print("\n❌ ERROR: No faces detected! Make sure you're in front of the camera.")
        return
    
    # Calculate statistics
    print("\n" + "=" * 60)
    print("RESULTS - Your typical 'looking at camera' angles:")
    print("=" * 60)
    
    yaw_mean = np.mean(yaw_values)
    yaw_std = np.std(yaw_values)
    yaw_max_dev = max(abs(min(yaw_values)), abs(max(yaw_values)))
    
    pitch_mean = np.mean(pitch_values)
    pitch_std = np.std(pitch_values)
    pitch_max_dev = max(abs(min(pitch_values)), abs(max(pitch_values)))
    
    roll_mean = np.mean(roll_values)
    roll_std = np.std(roll_values)
    
    print(f"\nYaw (left/right):")
    print(f"  Average: {yaw_mean:.1f}°")
    print(f"  Range: {min(yaw_values):.1f}° to {max(yaw_values):.1f}°")
    print(f"  Max deviation from 0: {yaw_max_dev:.1f}°")
    
    print(f"\nPitch (up/down):")
    print(f"  Average: {pitch_mean:.1f}°")
    print(f"  Range: {min(pitch_values):.1f}° to {max(pitch_values):.1f}°")
    print(f"  Max deviation from 0: {pitch_max_dev:.1f}°")
    
    print(f"\nRoll (tilt):")
    print(f"  Average: {roll_mean:.1f}°")
    print(f"  Range: {min(roll_values):.1f}° to {max(roll_values):.1f}°")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDED THRESHOLDS:")
    print("=" * 60)
    
    # Add 10° buffer to max deviation
    recommended_yaw = max(30, int(yaw_max_dev + 15))
    recommended_pitch = max(30, int(pitch_max_dev + 15))
    
    print(f"\nLOOKING_FORWARD_YAW_THRESHOLD = {recommended_yaw}")
    print(f"LOOKING_FORWARD_PITCH_THRESHOLD = {recommended_pitch}")
    
    print(f"\nThis allows:")
    print(f"  - Yaw: {-recommended_yaw}° to +{recommended_yaw}° (current: -25° to 25°)")
    print(f"  - Pitch: {-recommended_pitch}° to +{recommended_pitch}° (current: -20° to 20°)")
    
    if abs(pitch_mean) > 15:
        print(f"\n⚠️  NOTE: Your pitch average is {pitch_mean:.1f}°")
        if pitch_mean < 0:
            print("   Camera appears to be positioned BELOW eye level (you look down)")
        else:
            print("   Camera appears to be positioned ABOVE eye level (you look up)")
        print("   Consider adjusting camera position or using offset compensation")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
