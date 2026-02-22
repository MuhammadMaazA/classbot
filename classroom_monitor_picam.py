#!/usr/bin/env python3
"""
Classroom Monitoring System - Pi Camera AI Version
Optimized specifically for Raspberry Pi Camera AI module using picamera2

Note: Run with virtual environment activated:
  source ~/classroom_env/bin/activate && python3 classroom_monitor_picam.py
Or use: bash run.sh
"""

import os
import cv2
import numpy as np
import insightface
import time
import csv
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple

# Try to import picamera2
try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    print("Warning: picamera2 not available. Install with: sudo apt install python3-picamera2")

# Import configuration
import config

# ==================== INITIALIZE ====================
os.makedirs(config.LOGS_DIR, exist_ok=True)

# Initialize InsightFace
print("Loading InsightFace model...")
app = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=-1)

# ==================== LOAD KNOWN FACES ====================
def load_known_faces() -> Tuple[List[np.ndarray], List[str]]:
    """Load known face embeddings from the known_faces directory."""
    known_embeddings = []
    known_names = []
    
    print("\nLoading known faces...")
    
    if not os.path.exists(config.KNOWN_FACES_DIR):
        print(f"Warning: {config.KNOWN_FACES_DIR} does not exist!")
        return known_embeddings, known_names
    
    people = [d for d in sorted(os.listdir(config.KNOWN_FACES_DIR)) 
              if os.path.isdir(os.path.join(config.KNOWN_FACES_DIR, d))]
    
    for person in people:
        person_dir = os.path.join(config.KNOWN_FACES_DIR, person)
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
                emb = emb / (np.linalg.norm(emb) + 1e-12)
                person_embeddings.append(emb)
        
        if person_embeddings:
            avg_embedding = np.mean(person_embeddings, axis=0)
            avg_embedding = avg_embedding / (np.linalg.norm(avg_embedding) + 1e-12)
            
            known_embeddings.append(avg_embedding)
            known_names.append(person)
            print(f"  ✓ Loaded {person} ({len(person_embeddings)} images)")
    
    return known_embeddings, known_names


# ==================== ATTENDANCE MODULE ====================
class AttendanceTracker:
    """Tracks attendance with on-time and late arrival detection."""
    
    def __init__(self, on_time_window_seconds: int = None):
        self.on_time_window = on_time_window_seconds or config.ON_TIME_WINDOW_SECONDS
        self.session_start_time = time.time()
        self.tracked_people: Dict[str, dict] = {}
        
        if not os.path.exists(config.ATTENDANCE_LOG):
            with open(config.ATTENDANCE_LOG, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'name', 'status', 'similarity'])
    
    def mark_attendance(self, name: str, similarity: float) -> Tuple[bool, str]:
        """Mark attendance. Returns: (was_new, status)"""
        current_time = time.time()
        elapsed = current_time - self.session_start_time
        
        if name in self.tracked_people:
            return False, self.tracked_people[name]['status']
        
        status = 'on-time' if elapsed <= self.on_time_window else 'late'
        
        self.tracked_people[name] = {
            'first_seen': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': status,
            'similarity': similarity
        }
        
        with open(config.ATTENDANCE_LOG, 'a', newline='') as f:
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
        return len(self.tracked_people)
    
    def get_on_time_count(self) -> int:
        return sum(1 for p in self.tracked_people.values() if p['status'] == 'on-time')
    
    def get_late_count(self) -> int:
        return sum(1 for p in self.tracked_people.values() if p['status'] == 'late')
    
    def get_time_remaining(self) -> int:
        elapsed = time.time() - self.session_start_time
        remaining = max(0, self.on_time_window - elapsed)
        return int(remaining)
    
    def is_on_time_window_active(self) -> bool:
        return self.get_time_remaining() > 0


# ==================== CONCENTRATION MODULE ====================
class ConcentrationTracker:
    """Tracks student concentration based on head pose."""
    
    def __init__(self, log_interval_seconds: int = None):
        self.log_interval = log_interval_seconds or config.CONCENTRATION_LOG_INTERVAL
        self.last_log_time = time.time()
        self.concentration_data: Dict[str, dict] = defaultdict(lambda: {
            'looking_forward_count': 0,
            'looking_away_count': 0,
            'total_detections': 0
        })
        
        if not os.path.exists(config.CONCENTRATION_LOG):
            with open(config.CONCENTRATION_LOG, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'name', 'looking_forward', 'yaw', 'pitch', 'roll'])
    
    def check_head_pose(self, face) -> Tuple[bool, Tuple[float, float, float]]:
        """Check if person is looking forward. Returns: (is_looking_forward, (yaw, pitch, roll))"""
        # Check if pose attribute exists
        if not hasattr(face, 'pose') or face.pose is None:
            return True, (0.0, 0.0, 0.0)
        
        pose = face.pose
        
        # Handle case where pose might be empty or wrong shape
        if pose is None or len(pose) < 3:
            return True, (0.0, 0.0, 0.0)
        
        # InsightFace pose is ALREADY in degrees! Don't convert again
        yaw_deg, pitch_deg, roll_deg = pose[0], pose[1], pose[2]
        
        # Check if looking forward (within threshold)
        is_forward = (abs(yaw_deg) < config.LOOKING_FORWARD_YAW_THRESHOLD and 
                      abs(pitch_deg) < config.LOOKING_FORWARD_PITCH_THRESHOLD)
        
        return is_forward, (yaw_deg, pitch_deg, roll_deg)
    
    def update(self, name: str, is_looking_forward: bool, pose: Tuple[float, float, float]):
        """Update concentration tracking."""
        data = self.concentration_data[name]
        data['total_detections'] += 1
        
        if is_looking_forward:
            data['looking_forward_count'] += 1
        else:
            data['looking_away_count'] += 1
        
        # Debug print every update
        if data['total_detections'] % 30 == 0:  # Every 30 frames
            score = (data['looking_forward_count'] / data['total_detections']) * 100.0
            print(f"[CONC UPDATE] {name}: {data['looking_forward_count']}/{data['total_detections']} = {score:.1f}%")
        
        current_time = time.time()
        if current_time - self.last_log_time >= self.log_interval:
            self._log_to_csv(name, is_looking_forward, pose)
            self.last_log_time = current_time  # Update the last log time
    
    def _log_to_csv(self, name: str, looking_forward: bool, pose: Tuple[float, float, float]):
        """Log concentration data."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        yaw, pitch, roll = pose
        
        with open(config.CONCENTRATION_LOG, 'a', newline='') as f:
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
        """Get concentration percentage (0-100)."""
        data = self.concentration_data[name]
        if data['total_detections'] == 0:
            return 0.0
        return (data['looking_forward_count'] / data['total_detections']) * 100.0
    
    def get_overall_concentration(self) -> float:
        """Get overall classroom concentration."""
        total_forward = sum(d['looking_forward_count'] for d in self.concentration_data.values())
        total_detections = sum(d['total_detections'] for d in self.concentration_data.values())
        
        if total_detections == 0:
            return 0.0
        return (total_forward / total_detections) * 100.0


# ==================== FACE RECOGNITION ====================
# Face tracking cache to maintain identity across frames
# Cache structure: {(x, y): (name, timestamp, embedding)}
face_tracking_cache = {}
TRACKING_CACHE_TIMEOUT = 5.0  # Remember faces for 5 seconds
RELAXED_THRESHOLD_MULTIPLIER = 0.85  # Once recognized, use 85% of threshold
BBOX_DISTANCE_THRESHOLD = 100  # Max distance to consider same face
EMBEDDING_SIMILARITY_MIN = 0.30  # Min similarity to cached embedding to be "same person"

# Pre-calculate threshold (will be set after config is loaded)
RELAXED_RECOGNITION_THRESHOLD = 0.34  # Will be updated in main()

def get_face_position_key(bbox) -> Tuple[int, int]:
    """Get a position key from bounding box (center point)."""
    center_x = int((bbox[0] + bbox[2]) / 2)
    center_y = int((bbox[1] + bbox[3]) / 2)
    return (center_x, center_y)

def find_closest_cached_face(bbox) -> Tuple[str, str, float, np.ndarray]:
    """Find the closest cached face to this bbox. Returns: (cache_key, name, timestamp, embedding)"""
    current_pos = get_face_position_key(bbox)
    closest_key = None
    closest_dist = float('inf')
    
    for cache_key, (name, timestamp, embedding) in face_tracking_cache.items():
        cached_x, cached_y = cache_key
        dist = ((current_pos[0] - cached_x) ** 2 + (current_pos[1] - cached_y) ** 2) ** 0.5
        
        if dist < closest_dist and dist < BBOX_DISTANCE_THRESHOLD:
            closest_dist = dist
            closest_key = cache_key
    
    if closest_key:
        name, timestamp, embedding = face_tracking_cache[closest_key]
        return closest_key, name, timestamp, embedding
    return None, None, None, None

def clean_face_cache():
    """Remove old entries from face tracking cache."""
    current_time = time.time()
    keys_to_remove = []
    for face_key, (name, timestamp, embedding) in face_tracking_cache.items():
        if current_time - timestamp > TRACKING_CACHE_TIMEOUT:
            keys_to_remove.append(face_key)
    for key in keys_to_remove:
        del face_tracking_cache[key]

def recognize_face(face_embedding: np.ndarray, 
                   known_embeddings: List[np.ndarray], 
                   known_names: List[str],
                   bbox) -> Tuple[str, float]:
    """Recognize a face with position-based tracking. Returns: (name, similarity_score)"""
    if not known_embeddings:
        return "unknown", 0.0
    
    face_embedding = face_embedding / (np.linalg.norm(face_embedding) + 1e-12)
    
    best_similarity = -1
    best_name = "unknown"
    
    for known_emb, name in zip(known_embeddings, known_names):
        similarity = float(np.dot(face_embedding, known_emb))
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_name = name
    
    current_time = time.time()
    face_pos_key = get_face_position_key(bbox)
    
    # Normalize current embedding (already normalized above, so just use it)
    face_embedding_normalized = face_embedding
    
    # Use global relaxed threshold
    global RELAXED_RECOGNITION_THRESHOLD
    
    # Check if this face position was recently recognized
    cache_key, cached_name, cached_time, cached_embedding = find_closest_cached_face(bbox)
    
    if cache_key and cached_name and cached_embedding is not None:
        if current_time - cached_time < TRACKING_CACHE_TIMEOUT:
            # SAFETY CHECK: Compare current embedding with cached embedding
            # This ensures it's actually the same person, not just same position
            embedding_similarity = float(np.dot(face_embedding_normalized, cached_embedding))
            
            # Only use cached identity if embeddings are similar enough
            if embedding_similarity >= EMBEDDING_SIMILARITY_MIN:
                # Safety check: only use cached identity if current recognition is similar enough
                # This prevents misidentifying a new person in the same position
                
                # If current recognition matches cached name AND similarity is decent
                if best_name == cached_name and best_similarity >= RELAXED_RECOGNITION_THRESHOLD:
                    # Update cache with new position and embedding
                    if cache_key != face_pos_key:
                        del face_tracking_cache[cache_key]
                    face_tracking_cache[face_pos_key] = (best_name, current_time, face_embedding_normalized)
                    return best_name, best_similarity
                
                # If similarity dropped but still recognizes as SAME person (just lower confidence)
                elif best_name == cached_name and best_similarity >= (RELAXED_RECOGNITION_THRESHOLD * 0.85):
                    # Even lower threshold but MUST be same person
                    if cache_key != face_pos_key:
                        del face_tracking_cache[cache_key]
                    face_tracking_cache[face_pos_key] = (cached_name, current_time, face_embedding_normalized)
                    return cached_name, best_similarity
            
            # Otherwise: Different person (embedding too different) - don't use cache
            # This handles the case where someone new stands in the same spot
    
    # New recognition - use strict threshold
    if best_similarity < config.RECOGNITION_THRESHOLD:
        return "unknown", best_similarity
    
    # Cache this recognition with position and embedding
    face_tracking_cache[face_pos_key] = (best_name, current_time, face_embedding_normalized)
    
    return best_name, best_similarity


# ==================== DISPLAY FUNCTIONS ====================
def draw_info_panel(frame: np.ndarray, 
                    attendance: AttendanceTracker,
                    concentration: ConcentrationTracker,
                    fps: float):
    """Draw information panel."""
    h, w = frame.shape[:2]
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (w - 10, 160), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    color = (255, 255, 255)
    y_offset = 35
    x_start = 20
    
    time_remaining = attendance.get_time_remaining()
    window_status = "ON-TIME WINDOW" if time_remaining > 0 else "LATE ARRIVALS"
    
    cv2.putText(frame, f"Session: {window_status} ({time_remaining}s remaining)", 
                (x_start, y_offset), font, font_scale, color, thickness)
    y_offset += 30
    
    total = attendance.get_count()
    on_time = attendance.get_on_time_count()
    late = attendance.get_late_count()
    
    cv2.putText(frame, f"Total: {total} | On-time: {on_time} | Late: {late}", 
                (x_start, y_offset), font, font_scale, (0, 255, 0), thickness)
    y_offset += 30
    
    overall_conc = concentration.get_overall_concentration()
    conc_color = (0, 255, 0) if overall_conc >= 70 else (0, 165, 255) if overall_conc >= 50 else (0, 0, 255)
    
    cv2.putText(frame, f"Overall Concentration: {overall_conc:.1f}%", 
                (x_start, y_offset), font, font_scale, conc_color, thickness)
    y_offset += 30
    
    cv2.putText(frame, f"FPS: {fps:.1f}", 
                (x_start, y_offset), font, font_scale, (255, 255, 0), thickness)
    
    return frame


def draw_face_info(frame: np.ndarray, 
                   face,
                   name: str,
                   similarity: float,
                   status: str,
                   is_looking_forward: bool):
    """Draw bounding box and info for detected face."""
    box = face.bbox.astype(int)
    
    if name == "unknown":
        box_color = (128, 128, 128)
    elif status == "on-time":
        box_color = (0, 255, 0)
    else:
        box_color = (0, 165, 255)
    
    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), box_color, 2)
    
    if name != "unknown":
        label = f"{name.upper()} ({similarity:.2f})"
        status_label = f"Status: {status.upper()}"
        conc_label = f"Looking: {'FORWARD' if is_looking_forward else 'AWAY'}"
        conc_color = (0, 255, 0) if is_looking_forward else (0, 0, 255)
    else:
        label = f"Unknown (sim: {similarity:.2f})"
        status_label = f"Below threshold ({config.RECOGNITION_THRESHOLD})"
        conc_label = f"Looking: {'FORWARD' if is_looking_forward else 'AWAY'}"
        conc_color = (128, 128, 128)
    
    y_offset = box[1] - 10
    
    (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.rectangle(frame, (box[0], y_offset - label_h - 5), 
                  (box[0] + label_w + 5, y_offset), box_color, -1)
    cv2.putText(frame, label, (box[0], y_offset - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Always show status and concentration info
    if status_label:
        y_offset = box[3] + 20
        cv2.putText(frame, status_label, (box[0], y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, box_color, 1)
    
    if conc_label:
        y_offset = box[3] + 35 if status_label else box[3] + 20
        cv2.putText(frame, conc_label, (box[0], y_offset), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, conc_color, 1)
    
    return frame


# ==================== CAMERA INITIALIZATION ====================
def init_picamera():
    """Initialize Pi Camera using picamera2."""
    if not PICAMERA_AVAILABLE:
        return None
    
    try:
        picam2 = Picamera2()
        
        # Configure for low latency
        camera_config = picam2.create_preview_configuration(
            main={"size": (config.CAMERA_WIDTH, config.CAMERA_HEIGHT), "format": "RGB888"},
            controls={"FrameRate": config.CAMERA_FPS}
        )
        
        picam2.configure(camera_config)
        picam2.start()
        
        print(f"Pi Camera initialized: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.CAMERA_FPS}fps")
        return picam2
    except Exception as e:
        print(f"Failed to initialize Pi Camera: {e}")
        return None


def init_opencv_camera():
    """Initialize camera using OpenCV (fallback)."""
    try:
        cap = cv2.VideoCapture(config.CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
        
        # Set additional properties for lower latency
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        if cap.isOpened():
            print(f"OpenCV camera initialized: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}")
            return cap
        else:
            print("Failed to open OpenCV camera")
            return None
    except Exception as e:
        print(f"Failed to initialize OpenCV camera: {e}")
        return None


# ==================== MAIN SYSTEM ====================
def main():
    """Main monitoring system."""
    print("=" * 60)
    print("CLASSROOM MONITORING SYSTEM - Pi Camera AI Version")
    print("=" * 60)
    
    # Set relaxed recognition threshold
    global RELAXED_RECOGNITION_THRESHOLD
    RELAXED_RECOGNITION_THRESHOLD = config.RECOGNITION_THRESHOLD * RELAXED_THRESHOLD_MULTIPLIER
    
    # Load known faces
    known_embeddings, known_names = load_known_faces()
    
    if not known_names:
        print("\nERROR: No known faces loaded!")
        return
    
    print(f"\nLoaded {len(known_names)} known people: {', '.join(known_names)}")
    
    # Initialize trackers
    attendance = AttendanceTracker()
    concentration = ConcentrationTracker()
    
    # Initialize camera (try Pi Camera first, fallback to OpenCV)
    print(f"\nInitializing camera...")
    picam2 = init_picamera()
    opencv_cap = None
    
    if picam2 is None:
        print("Pi Camera not available, trying OpenCV...")
        opencv_cap = init_opencv_camera()
        if opencv_cap is None:
            print("ERROR: No camera available!")
            return
    
    use_picamera = picam2 is not None
    
    print(f"\nSession started! On-time window: {config.ON_TIME_WINDOW_SECONDS} seconds")
    print("Press 'q' or ESC to quit\n")
    
    frame_count = 0
    fps_start_time = time.time()
    current_fps = 0.0
    
    try:
        while True:
            # Capture frame
            if use_picamera:
                frame = picam2.capture_array()
                # Convert RGB to BGR for OpenCV
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                ret, frame = opencv_cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break
            
            # Frame skipping
            frame_count += 1
            if frame_count % config.FRAME_SKIP != 0:
                continue
            
            # Calculate FPS
            if frame_count % 30 == 0:
                fps_end_time = time.time()
                current_fps = 30 / (fps_end_time - fps_start_time)
                fps_start_time = fps_end_time
                # Clean old face tracking cache entries
                clean_face_cache()
            
            # Face detection and analysis
            faces = app.get(frame)
            
            for face in faces:
                # Recognition with position-based tracking
                name, similarity = recognize_face(
                    face.embedding, 
                    known_embeddings, 
                    known_names,
                    bbox=face.bbox
                )
                
                # Attendance (track all faces, even unknown ones)
                if name != "unknown":
                    was_new, status = attendance.mark_attendance(name, similarity)
                    if was_new:
                        print(f"✓ [ATTENDANCE] {name.upper()} marked as {status.upper()} (similarity: {similarity:.3f})")
                    # Debug: Show current recognition
                    elif frame_count % 90 == 0:  # Every 3 seconds
                        print(f"  [TRACKING] {name.upper()} still recognized (similarity: {similarity:.3f})")
                else:
                    status = "unknown"
                    # Debug: show why face wasn't recognized (only occasionally to avoid spam)
                    if similarity > 0.30 and frame_count % 60 == 0:  # Every 2 seconds
                        print(f"⚠ [UNKNOWN] Face similarity {similarity:.3f} < threshold {config.RECOGNITION_THRESHOLD:.2f}")
                
                # Concentration (track for all faces)
                is_looking_forward, pose = concentration.check_head_pose(face)
                
                if name != "unknown":
                    concentration.update(name, is_looking_forward, pose)
                    # Show pose angles to debug
                    if frame_count % 30 == 0:  # Every second
                        status_str = "✓ FORWARD" if is_looking_forward else "✗ AWAY"
                        print(f"  [POSE] {name}: {status_str} | yaw={pose[0]:.1f}° pitch={pose[1]:.1f}° roll={pose[2]:.1f}° | thresholds: yaw±{config.LOOKING_FORWARD_YAW_THRESHOLD}° pitch±{config.LOOKING_FORWARD_PITCH_THRESHOLD}°")
                    # Summary every 2 seconds
                    if frame_count % 60 == 0:
                        score = concentration.get_concentration_score(name)
                        print(f"  [CONCENTRATION] {name.upper()}: {score:.1f}%")
                
                # Visualization
                frame = draw_face_info(
                    frame, face, name, similarity, status, is_looking_forward
                )
            
            # Draw info panel
            frame = draw_info_panel(frame, attendance, concentration, current_fps)
            
            # Display
            cv2.imshow('Classroom Monitor - Pi Camera AI', frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                print("\nShutting down...")
                break
    
    finally:
        # Cleanup
        if use_picamera:
            picam2.stop()
        else:
            opencv_cap.release()
        cv2.destroyAllWindows()
        
        # Summary
        print("\n" + "=" * 60)
        print("SESSION SUMMARY")
        print("=" * 60)
        print(f"Total people: {attendance.get_count()}")
        print(f"On-time: {attendance.get_on_time_count()}")
        print(f"Late: {attendance.get_late_count()}")
        print(f"Overall concentration: {concentration.get_overall_concentration():.1f}%")
        print(f"\nLogs saved to:")
        print(f"  - {config.ATTENDANCE_LOG}")
        print(f"  - {config.CONCENTRATION_LOG}")
        print("=" * 60)


if __name__ == "__main__":
    main()
