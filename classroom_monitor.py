#!/usr/bin/env python3
"""
Classroom Monitoring System
- Attendance tracking with on-time/late detection
- Concentration monitoring (head pose tracking)
- Optimized for Raspberry Pi Camera AI
"""

import os
import cv2
import numpy as np
import insightface
import time
import csv
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

# ==================== CONFIGURATION ====================
BASE_DIR = os.path.expanduser("~/classroom_ai")
KNOWN_FACES_DIR = os.path.join(BASE_DIR, "known_faces")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
ATTENDANCE_LOG = os.path.join(LOGS_DIR, "attendance.csv")
CONCENTRATION_LOG = os.path.join(LOGS_DIR, "concentration.csv")

# Timing configuration (in seconds)
ON_TIME_WINDOW = 60  # First 60 seconds for demo (20 minutes in production)

# Recognition threshold
RECOGNITION_THRESHOLD = 0.45

# Camera optimization settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FRAME_SKIP = 2  # Process every 2nd frame for better performance

# Head pose thresholds (angles in degrees)
LOOKING_FORWARD_YAW_THRESHOLD = 25  # Looking left/right
LOOKING_FORWARD_PITCH_THRESHOLD = 20  # Looking up/down

# ==================== INITIALIZE ====================
os.makedirs(LOGS_DIR, exist_ok=True)

# Initialize InsightFace
print("Loading InsightFace model...")
app = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=-1)  # -1 for CPU

# ==================== LOAD KNOWN FACES ====================
def load_known_faces() -> Tuple[List[np.ndarray], List[str]]:
    """Load known face embeddings from the known_faces directory."""
    known_embeddings = []
    known_names = []
    
    print("\nLoading known faces...")
    
    if not os.path.exists(KNOWN_FACES_DIR):
        print(f"Warning: {KNOWN_FACES_DIR} does not exist!")
        return known_embeddings, known_names
    
    people = [d for d in sorted(os.listdir(KNOWN_FACES_DIR)) 
              if os.path.isdir(os.path.join(KNOWN_FACES_DIR, d))]
    
    for person in people:
        person_dir = os.path.join(KNOWN_FACES_DIR, person)
        images = [f for f in os.listdir(person_dir) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        person_embeddings = []
        
        for img_name in images:
            img_path = os.path.join(person_dir, img_name)
            img = cv2.imread(img_path)
            
            if img is None:
                continue
            
            faces = app.get(img)
            if len(faces) > 0:
                emb = faces[0].embedding
                emb = emb / (np.linalg.norm(emb) + 1e-12)  # Normalize
                person_embeddings.append(emb)
        
        if person_embeddings:
            # Average all embeddings for this person
            avg_embedding = np.mean(person_embeddings, axis=0)
            avg_embedding = avg_embedding / (np.linalg.norm(avg_embedding) + 1e-12)
            
            known_embeddings.append(avg_embedding)
            known_names.append(person)
            print(f"  ✓ Loaded {person} ({len(person_embeddings)} images)")
    
    return known_embeddings, known_names


# ==================== ATTENDANCE MODULE ====================
class AttendanceTracker:
    """Tracks attendance with on-time and late arrival detection."""
    
    def __init__(self, on_time_window_seconds: int = 60):
        self.on_time_window = on_time_window_seconds
        self.session_start_time = time.time()
        self.tracked_people: Dict[str, dict] = {}
        
        # Initialize CSV log file
        if not os.path.exists(ATTENDANCE_LOG):
            with open(ATTENDANCE_LOG, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'name', 'status', 'similarity'])
    
    def mark_attendance(self, name: str, similarity: float) -> Tuple[bool, str]:
        """
        Mark attendance for a person.
        Returns: (was_new, status)
        """
        current_time = time.time()
        elapsed = current_time - self.session_start_time
        
        # Check if person already marked
        if name in self.tracked_people:
            return False, self.tracked_people[name]['status']
        
        # Determine status based on timing
        if elapsed <= self.on_time_window:
            status = 'on-time'
        else:
            status = 'late'
        
        # Record in memory
        self.tracked_people[name] = {
            'first_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': status,
            'similarity': similarity
        }
        
        # Log to CSV
        with open(ATTENDANCE_LOG, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                self.tracked_people[name]['first_seen'],
                name,
                status,
                f"{similarity:.3f}"
            ])
        
        print(f"[ATTENDANCE] {name} marked as {status.upper()} (similarity: {similarity:.3f})")
        return True, status
    
    def get_count(self) -> int:
        """Get total count of unique people seen."""
        return len(self.tracked_people)
    
    def get_on_time_count(self) -> int:
        """Get count of people who arrived on time."""
        return sum(1 for p in self.tracked_people.values() if p['status'] == 'on-time')
    
    def get_late_count(self) -> int:
        """Get count of people who arrived late."""
        return sum(1 for p in self.tracked_people.values() if p['status'] == 'late')
    
    def get_time_remaining(self) -> int:
        """Get seconds remaining in on-time window (returns 0 if expired)."""
        elapsed = time.time() - self.session_start_time
        remaining = max(0, self.on_time_window - elapsed)
        return int(remaining)
    
    def is_on_time_window_active(self) -> bool:
        """Check if we're still in the on-time window."""
        return self.get_time_remaining() > 0


# ==================== CONCENTRATION MODULE ====================
class ConcentrationTracker:
    """Tracks student concentration based on head pose."""
    
    def __init__(self, log_interval_seconds: int = 10):
        self.log_interval = log_interval_seconds
        self.last_log_time = time.time()
        self.concentration_data: Dict[str, dict] = defaultdict(lambda: {
            'looking_forward_count': 0,
            'looking_away_count': 0,
            'total_detections': 0
        })
        
        # Initialize CSV log file
        if not os.path.exists(CONCENTRATION_LOG):
            with open(CONCENTRATION_LOG, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'name', 'looking_forward', 'yaw', 'pitch', 'roll'])
    
    def check_head_pose(self, face) -> Tuple[bool, Tuple[float, float, float]]:
        """
        Check if person is looking forward based on head pose.
        Returns: (is_looking_forward, (yaw, pitch, roll))
        """
        # InsightFace provides pose estimates in the face object
        pose = face.pose
        
        if pose is None:
            return False, (0.0, 0.0, 0.0)
        
        # Convert radians to degrees if needed
        yaw, pitch, roll = pose
        yaw_deg = np.degrees(yaw)
        pitch_deg = np.degrees(pitch)
        roll_deg = np.degrees(roll)
        
        # Check if looking forward
        is_forward = (abs(yaw_deg) < LOOKING_FORWARD_YAW_THRESHOLD and 
                      abs(pitch_deg) < LOOKING_FORWARD_PITCH_THRESHOLD)
        
        return is_forward, (yaw_deg, pitch_deg, roll_deg)
    
    def update(self, name: str, is_looking_forward: bool, pose: Tuple[float, float, float]):
        """Update concentration tracking for a person."""
        data = self.concentration_data[name]
        data['total_detections'] += 1
        
        if is_looking_forward:
            data['looking_forward_count'] += 1
        else:
            data['looking_away_count'] += 1
        
        # Log periodically
        current_time = time.time()
        if current_time - self.last_log_time >= self.log_interval:
            self._log_to_csv(name, is_looking_forward, pose)
    
    def _log_to_csv(self, name: str, looking_forward: bool, pose: Tuple[float, float, float]):
        """Log concentration data to CSV."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        yaw, pitch, roll = pose
        
        with open(CONCENTRATION_LOG, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                name,
                'yes' if looking_forward else 'no',
                f"{yaw:.2f}",
                f"{pitch:.2f}",
                f"{roll:.2f}"
            ])
    
    def get_concentration_score(self, name: str) -> float:
        """Get concentration percentage for a person (0-100)."""
        data = self.concentration_data[name]
        if data['total_detections'] == 0:
            return 0.0
        return (data['looking_forward_count'] / data['total_detections']) * 100.0
    
    def get_overall_concentration(self) -> float:
        """Get overall classroom concentration percentage."""
        total_forward = sum(d['looking_forward_count'] for d in self.concentration_data.values())
        total_detections = sum(d['total_detections'] for d in self.concentration_data.values())
        
        if total_detections == 0:
            return 0.0
        return (total_forward / total_detections) * 100.0


# ==================== FACE RECOGNITION ====================
def recognize_face(face_embedding: np.ndarray, 
                   known_embeddings: List[np.ndarray], 
                   known_names: List[str],
                   threshold: float = RECOGNITION_THRESHOLD) -> Tuple[str, float]:
    """
    Recognize a face using cosine similarity.
    Returns: (name, similarity_score)
    """
    if not known_embeddings:
        return "unknown", 0.0
    
    # Normalize embedding
    face_embedding = face_embedding / (np.linalg.norm(face_embedding) + 1e-12)
    
    best_similarity = -1
    best_name = "unknown"
    
    for known_emb, name in zip(known_embeddings, known_names):
        similarity = float(np.dot(face_embedding, known_emb))
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_name = name
    
    if best_similarity < threshold:
        return "unknown", best_similarity
    
    return best_name, best_similarity


# ==================== VIDEO DISPLAY ====================
def draw_info_panel(frame: np.ndarray, 
                    attendance: AttendanceTracker,
                    concentration: ConcentrationTracker,
                    fps: float):
    """Draw information panel on the frame."""
    h, w = frame.shape[:2]
    
    # Create semi-transparent overlay for info panel
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (w - 10, 160), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
    
    # Text settings
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    color = (255, 255, 255)
    y_offset = 35
    x_start = 20
    
    # Session info
    time_remaining = attendance.get_time_remaining()
    window_status = "ON-TIME WINDOW" if time_remaining > 0 else "LATE ARRIVALS"
    
    cv2.putText(frame, f"Session: {window_status} ({time_remaining}s remaining)", 
                (x_start, y_offset), font, font_scale, color, thickness)
    y_offset += 30
    
    # Attendance stats
    total = attendance.get_count()
    on_time = attendance.get_on_time_count()
    late = attendance.get_late_count()
    
    cv2.putText(frame, f"Total: {total} | On-time: {on_time} | Late: {late}", 
                (x_start, y_offset), font, font_scale, (0, 255, 0), thickness)
    y_offset += 30
    
    # Concentration stats
    overall_conc = concentration.get_overall_concentration()
    conc_color = (0, 255, 0) if overall_conc >= 70 else (0, 165, 255) if overall_conc >= 50 else (0, 0, 255)
    
    cv2.putText(frame, f"Overall Concentration: {overall_conc:.1f}%", 
                (x_start, y_offset), font, font_scale, conc_color, thickness)
    y_offset += 30
    
    # FPS
    cv2.putText(frame, f"FPS: {fps:.1f}", 
                (x_start, y_offset), font, font_scale, (255, 255, 0), thickness)
    
    return frame


def draw_face_info(frame: np.ndarray, 
                   face,
                   name: str,
                   similarity: float,
                   status: str,
                   is_looking_forward: bool):
    """Draw bounding box and info for a detected face."""
    box = face.bbox.astype(int)
    
    # Choose color based on status
    if name == "unknown":
        box_color = (128, 128, 128)  # Gray
    elif status == "on-time":
        box_color = (0, 255, 0)  # Green
    else:
        box_color = (0, 165, 255)  # Orange
    
    # Draw bounding box
    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), box_color, 2)
    
    # Prepare label
    if name != "unknown":
        label = f"{name} ({similarity:.2f})"
        status_label = f"Status: {status}"
        conc_label = f"Looking: {'Forward' if is_looking_forward else 'Away'}"
        conc_color = (0, 255, 0) if is_looking_forward else (0, 0, 255)
    else:
        label = f"Unknown ({similarity:.2f})"
        status_label = ""
        conc_label = ""
        conc_color = (128, 128, 128)
    
    # Draw labels with background
    y_offset = box[1] - 10
    
    # Name and confidence
    (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.rectangle(frame, (box[0], y_offset - label_h - 5), 
                  (box[0] + label_w + 5, y_offset), box_color, -1)
    cv2.putText(frame, label, (box[0], y_offset - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Status (if available)
    if status_label and name != "unknown":
        y_offset = box[3] + 20
        cv2.putText(frame, status_label, (box[0], y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, box_color, 1)
        
        # Concentration (if available)
        y_offset += 15
        cv2.putText(frame, conc_label, (box[0], y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, conc_color, 1)
    
    return frame


# ==================== MAIN SYSTEM ====================
def main():
    """Main monitoring system."""
    print("=" * 60)
    print("CLASSROOM MONITORING SYSTEM")
    print("=" * 60)
    
    # Load known faces
    known_embeddings, known_names = load_known_faces()
    
    if not known_names:
        print("\nERROR: No known faces loaded!")
        print("Please add face images to the known_faces directory.")
        return
    
    print(f"\nLoaded {len(known_names)} known people: {', '.join(known_names)}")
    
    # Initialize trackers
    attendance = AttendanceTracker(on_time_window_seconds=ON_TIME_WINDOW)
    concentration = ConcentrationTracker()
    
    # Initialize camera
    print(f"\nInitializing camera ({CAMERA_WIDTH}x{CAMERA_HEIGHT})...")
    
    # Try Pi Camera first, then fallback to USB camera
    try:
        # For Pi Camera, use different initialization
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, 30)
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return
    
    if not cap.isOpened():
        print("ERROR: Could not open camera!")
        return
    
    print("Camera initialized successfully!")
    print(f"\nSession started! On-time window: {ON_TIME_WINDOW} seconds")
    print("Press 'q' or ESC to quit\n")
    
    # FPS calculation
    frame_count = 0
    fps_start_time = time.time()
    current_fps = 0.0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Failed to grab frame")
                break
            
            # Frame skipping for performance
            frame_count += 1
            if frame_count % FRAME_SKIP != 0:
                continue
            
            # Calculate FPS
            if frame_count % 30 == 0:
                fps_end_time = time.time()
                current_fps = 30 / (fps_end_time - fps_start_time)
                fps_start_time = fps_end_time
            
            # Run face detection and analysis
            faces = app.get(frame)
            
            # Process each detected face
            for face in faces:
                # 1. Face Recognition
                face_embedding = face.embedding
                name, similarity = recognize_face(
                    face_embedding, 
                    known_embeddings, 
                    known_names
                )
                
                # 2. Attendance Tracking
                if name != "unknown":
                    was_new, status = attendance.mark_attendance(name, similarity)
                else:
                    status = "unknown"
                
                # 3. Concentration Tracking
                is_looking_forward, pose = concentration.check_head_pose(face)
                if name != "unknown":
                    concentration.update(name, is_looking_forward, pose)
                
                # 4. Draw visualization
                frame = draw_face_info(
                    frame, face, name, similarity, status, is_looking_forward
                )
            
            # Draw info panel
            frame = draw_info_panel(frame, attendance, concentration, current_fps)
            
            # Display frame
            cv2.imshow('Classroom Monitor', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                print("\nShutting down...")
                break
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Print summary
        print("\n" + "=" * 60)
        print("SESSION SUMMARY")
        print("=" * 60)
        print(f"Total people detected: {attendance.get_count()}")
        print(f"On-time arrivals: {attendance.get_on_time_count()}")
        print(f"Late arrivals: {attendance.get_late_count()}")
        print(f"Overall concentration: {concentration.get_overall_concentration():.1f}%")
        print(f"\nLogs saved to:")
        print(f"  - Attendance: {ATTENDANCE_LOG}")
        print(f"  - Concentration: {CONCENTRATION_LOG}")
        print("=" * 60)


if __name__ == "__main__":
    main()
