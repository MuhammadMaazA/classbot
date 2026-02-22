#!/usr/bin/env python3
"""
Camera Streaming Module for Dashboard
Provides live camera feed with face detection overlays
"""

import cv2
import numpy as np
import insightface
import os
from datetime import datetime
from picamera2 import Picamera2
import sys

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class CameraStreamer:
    def __init__(self):
        self.camera = None
        self.face_app = None
        self.known_embeddings = []
        self.known_names = []
        self.face_positions = {}
        self.last_recognition = {}
        
        self.initialize_camera()
        self.initialize_face_detection()
        self.load_known_faces()
    
    def initialize_camera(self):
        """Initialize Pi Camera"""
        print("Initializing camera...")
        self.camera = Picamera2()
        camera_config = self.camera.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        )
        self.camera.configure(camera_config)
        self.camera.start()
        print("✓ Camera ready")
    
    def initialize_face_detection(self):
        """Initialize InsightFace"""
        print("Loading face detection model...")
        self.face_app = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
        self.face_app.prepare(ctx_id=-1)
        print("✓ Face detection ready")
    
    def load_known_faces(self):
        """Load known face embeddings"""
        print("Loading known faces...")
        
        if not os.path.exists(config.KNOWN_FACES_DIR):
            print(f"Warning: {config.KNOWN_FACES_DIR} not found")
            return
        
        for person_name in os.listdir(config.KNOWN_FACES_DIR):
            person_dir = os.path.join(config.KNOWN_FACES_DIR, person_name)
            
            if not os.path.isdir(person_dir):
                continue
            
            for img_file in os.listdir(person_dir):
                if not img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    continue
                
                img_path = os.path.join(person_dir, img_file)
                img = cv2.imread(img_path)
                
                if img is None:
                    continue
                
                faces = self.face_app.get(img)
                
                if len(faces) > 0:
                    self.known_embeddings.append(faces[0].embedding)
                    self.known_names.append(person_name.upper())
                    print(f"  ✓ Loaded {person_name}")
                    break
        
        print(f"✓ Loaded {len(self.known_names)} known faces")
    
    def recognize_face(self, embedding):
        """Recognize face by comparing embeddings"""
        if len(self.known_embeddings) == 0:
            return "UNKNOWN", 0.0
        
        similarities = []
        for known_emb in self.known_embeddings:
            similarity = np.dot(embedding, known_emb) / (
                np.linalg.norm(embedding) * np.linalg.norm(known_emb)
            )
            similarities.append(similarity)
        
        max_idx = np.argmax(similarities)
        max_similarity = similarities[max_idx]
        
        if max_similarity >= config.RECOGNITION_THRESHOLD:
            return self.known_names[max_idx], max_similarity
        else:
            return "UNKNOWN", max_similarity
    
    def get_frame(self):
        """Capture and process a single frame"""
        # Capture frame
        frame = self.camera.capture_array()
        
        # Detect faces
        faces = self.face_app.get(frame)
        
        # Process each face
        for face in faces:
            # Get face bounding box
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            
            # Recognize face
            name, similarity = self.recognize_face(face.embedding)
            
            # Get head pose
            pose = face.pose
            yaw, pitch, roll = pose[0], pose[1], pose[2]
            
            # Determine looking direction
            is_looking = abs(yaw) <= config.YAW_THRESHOLD and abs(pitch) <= config.PITCH_THRESHOLD
            looking_status = "FOCUSED" if is_looking else "AWAY"
            
            # Choose color based on status
            if name != "UNKNOWN":
                color = (0, 255, 0) if is_looking else (0, 165, 255)  # Green if focused, Orange if away
            else:
                color = (128, 128, 128)  # Gray for unknown
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw name and status
            label = f"{name}"
            if name != "UNKNOWN":
                label += f" ({similarity:.2f})"
            
            # Background for text
            (label_width, label_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x1, y1 - label_height - 10), (x1 + label_width, y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw status below box
            status_label = f"{looking_status}"
            cv2.putText(frame, status_label, (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Add timestamp and face count
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Faces: {len(faces)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    def generate_frames(self):
        """Generator function for streaming frames"""
        while True:
            try:
                frame = self.get_frame()
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
                
                # Yield frame in MJPEG format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            except Exception as e:
                print(f"Streaming error: {e}")
                break
    
    def cleanup(self):
        """Clean up resources"""
        if self.camera:
            self.camera.stop()

# Global instance
_camera_instance = None

def get_camera_streamer():
    """Get or create camera streamer instance"""
    global _camera_instance
    if _camera_instance is None:
        _camera_instance = CameraStreamer()
    return _camera_instance
