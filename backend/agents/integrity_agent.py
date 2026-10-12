"""
Integrity Agent - Advanced cheating detection system
Detects:
- Multiple faces in frame (someone helping)
- Gaze direction (reading off-screen)
- Suspicious head movements
- Face absence (leaving camera view)
- Reading patterns (eyes moving horizontally repeatedly)
"""
import cv2
import numpy as np
import mediapipe as mp
from typing import List, Dict, Any, Tuple
from collections import deque

class IntegrityAgent:
    def __init__(self):
        # Initialize MediaPipe components
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=2,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Tracking state
        self.gaze_history = deque(maxlen=30)  # Track last 30 frames (1 second at 30fps)
        self.head_pose_history = deque(maxlen=30)
        
    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze a single frame for integrity violations"""
        violations = {
            "multiple_faces": False,
            "gaze_off_screen": False,
            "reading_detected": False,
            "face_absent": False,
            "suspicious_movement": False,
            "details": {}
        }
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 1. Detect multiple faces
        face_detection_results = self.face_detection.process(rgb_frame)
        if face_detection_results.detections:
            num_faces = len(face_detection_results.detections)
            violations["details"]["num_faces"] = num_faces
            if num_faces > 1:
                violations["multiple_faces"] = True
        else:
            violations["face_absent"] = True
            return violations
        
        # 2. Analyze gaze direction and head pose
        face_mesh_results = self.face_mesh.process(rgb_frame)
        if face_mesh_results.multi_face_landmarks:
            landmarks = face_mesh_results.multi_face_landmarks[0]
            
            # Get gaze direction
            gaze_score = self._estimate_gaze_direction(landmarks, frame.shape)
            violations["details"]["gaze_score"] = gaze_score
            self.gaze_history.append(gaze_score)
            
            # Gaze off-screen if consistently looking away
            if len(self.gaze_history) > 15:
                avg_gaze = np.mean(list(self.gaze_history)[-15:])
                if avg_gaze < 0.3:  # Low score = looking away
                    violations["gaze_off_screen"] = True
            
            # Get head pose
            head_pose = self._estimate_head_pose(landmarks, frame.shape)
            violations["details"]["head_pose"] = head_pose
            self.head_pose_history.append(head_pose)
            
            # Detect reading pattern (horizontal eye movement)
            if self._detect_reading_pattern():
                violations["reading_detected"] = True
            
            # Detect suspicious movements
            if self._detect_suspicious_movement():
                violations["suspicious_movement"] = True
        
        return violations
    
    def _estimate_gaze_direction(self, landmarks, frame_shape) -> float:
        """
        Estimate if person is looking at camera
        Returns score 0-1, where 1 = looking directly at camera
        """
        h, w = frame_shape[:2]
        
        # Get eye landmarks (iris centers)
        # Left eye: 468, 469, 470, 471, 472
        # Right eye: 473, 474, 475, 476, 477
        left_iris = landmarks.landmark[468]
        right_iris = landmarks.landmark[473]
        
        # Get eye corners for reference
        left_corner = landmarks.landmark[33]
        right_corner = landmarks.landmark[263]
        
        # Calculate relative iris position
        left_x = (left_iris.x - left_corner.x) * w
        right_x = (right_iris.x - right_corner.x) * w
        
        # Central gaze should have iris near center of eye
        # Score based on how centered the iris is
        center_threshold = 5  # pixels
        left_centered = abs(left_x) < center_threshold
        right_centered = abs(right_x) < center_threshold
        
        if left_centered and right_centered:
            return 1.0
        elif left_centered or right_centered:
            return 0.6
        else:
            # Calculate deviation
            deviation = (abs(left_x) + abs(right_x)) / 2
            score = max(0, 1 - (deviation / 20))
            return score
    
    def _estimate_head_pose(self, landmarks, frame_shape) -> Dict[str, float]:
        """
        Estimate head rotation angles (yaw, pitch, roll)
        """
        h, w = frame_shape[:2]
        
        # Key landmarks for pose estimation
        nose_tip = landmarks.landmark[1]
        chin = landmarks.landmark[152]
        left_eye = landmarks.landmark[33]
        right_eye = landmarks.landmark[263]
        left_ear = landmarks.landmark[234]
        right_ear = landmarks.landmark[454]
        
        # Convert to pixel coordinates
        nose_tip_2d = np.array([nose_tip.x * w, nose_tip.y * h])
        chin_2d = np.array([chin.x * w, chin.y * h])
        left_eye_2d = np.array([left_eye.x * w, left_eye.y * h])
        right_eye_2d = np.array([right_eye.x * w, right_eye.y * h])
        
        # Simplified pose estimation
        # Yaw: horizontal head rotation
        eye_center_x = (left_eye_2d[0] + right_eye_2d[0]) / 2
        nose_x = nose_tip_2d[0]
        yaw = (nose_x - eye_center_x) / (w / 2)  # Normalized -1 to 1
        
        # Pitch: vertical head rotation
        nose_chin_dist = np.linalg.norm(nose_tip_2d - chin_2d)
        pitch = (chin_2d[1] - nose_tip_2d[1]) / h  # Normalized
        
        return {
            "yaw": float(yaw),
            "pitch": float(pitch)
        }
    
    def _detect_reading_pattern(self) -> bool:
        """
        Detect if gaze pattern suggests reading
        Reading = repeated horizontal eye movements
        """
        if len(self.gaze_history) < 20:
            return False
        
        # Analyze gaze variance
        recent_gazes = list(self.gaze_history)[-20:]
        variance = np.var(recent_gazes)
        
        # High variance + low average = likely reading
        avg_gaze = np.mean(recent_gazes)
        if variance > 0.15 and avg_gaze < 0.5:
            return True
        
        return False
    
    def _detect_suspicious_movement(self) -> bool:
        """
        Detect suspicious head movements (looking away frequently)
        """
        if len(self.head_pose_history) < 20:
            return False
        
        recent_poses = list(self.head_pose_history)[-20:]
        
        # Count how many times head turned significantly
        turn_count = 0
        for i in range(1, len(recent_poses)):
            prev_yaw = recent_poses[i-1]["yaw"]
            curr_yaw = recent_poses[i]["yaw"]
            
            # Significant turn if yaw changes > 0.3
            if abs(curr_yaw - prev_yaw) > 0.3:
                turn_count += 1
        
        # More than 5 significant turns in 20 frames is suspicious
        return turn_count > 5
    
    def analyze_video(self, video_path: str, sample_rate: int = 10) -> Dict[str, Any]:
        """
        Analyze entire video and return integrity report
        Args:
            video_path: Path to video file
            sample_rate: Analyze every Nth frame
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": "Could not open video"}
        
        total_frames = 0
        violations_count = {
            "multiple_faces": 0,
            "gaze_off_screen": 0,
            "reading_detected": 0,
            "face_absent": 0,
            "suspicious_movement": 0
        }
        violation_timestamps = []
        
        frame_count = 0
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if frame_count % sample_rate != 0:
                continue
            
            total_frames += 1
            violations = self.analyze_frame(frame)
            
            # Count violations
            has_violation = False
            for key in violations_count.keys():
                if violations.get(key, False):
                    violations_count[key] += 1
                    has_violation = True
            
            # Record timestamp if violation occurred
            if has_violation:
                timestamp = frame_count / fps
                violation_timestamps.append({
                    "timestamp": timestamp,
                    "violations": {k: v for k, v in violations.items() 
                                 if k != "details" and v is True}
                })
        
        cap.release()
        
        # Calculate integrity score (0-100)
        max_possible_violations = total_frames * len(violations_count)
        actual_violations = sum(violations_count.values())
        integrity_score = max(0, 100 - (actual_violations / max_possible_violations * 100)) if max_possible_violations > 0 else 100
        
        return {
            "integrity_score": round(integrity_score, 2),
            "total_frames_analyzed": total_frames,
            "violations_summary": violations_count,
            "violation_timestamps": violation_timestamps[:10],  # Return first 10
            "severity": self._calculate_severity(violations_count, total_frames)
        }
    
    def _calculate_severity(self, violations: Dict[str, int], total_frames: int) -> str:
        """Calculate overall severity of violations"""
        if total_frames == 0:
            return "unknown"
        
        # Check for critical violations
        if violations["multiple_faces"] > 0:
            return "critical"
        
        # Calculate violation rate
        total_violations = sum(violations.values())
        violation_rate = total_violations / total_frames
        
        if violation_rate > 0.5:
            return "high"
        elif violation_rate > 0.25:
            return "medium"
        elif violation_rate > 0.1:
            return "low"
        else:
            return "minimal"
    
    def reset_tracking(self):
        """Reset tracking state between questions"""
        self.gaze_history.clear()
        self.head_pose_history.clear()