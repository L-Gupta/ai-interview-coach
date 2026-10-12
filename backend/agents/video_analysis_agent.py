"""
Video Analysis Agent - Analyzes facial expressions and emotions
Uses FER (Facial Emotion Recognition) and OpenCV
"""
import cv2
import numpy as np
from fer.fer import FER
from typing import List, Dict, Any
from collections import Counter

class VideoAnalysisAgent:
    def __init__(self):
        self.emotion_detector = FER(mtcnn=False)
        
    def analyze_video(self, video_path: str, sample_rate: int = 5) -> Dict[str, Any]:
        """
        Analyze video for facial expressions and emotions
        Args:
            video_path: Path to video file
            sample_rate: Analyze every Nth frame (default 5 fps)
        Returns:
            Dictionary with emotion analysis results
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {"error": "Could not open video"}
        
        emotions_detected = []
        frame_count = 0
        total_analyzed = 0
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_interval = int(fps / sample_rate)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if frame_count % frame_interval != 0:
                continue
            
            # Detect emotions in frame
            emotion = self._detect_emotion(frame)
            if emotion:
                emotions_detected.append(emotion)
                total_analyzed += 1
        
        cap.release()
        
        if not emotions_detected:
            return {
                "dominant_emotions": ["neutral"],
                "emotion_distribution": {"neutral": 1.0},
                "average_confidence": 0.5,
                "engagement_score": 50.0,
                "frames_analyzed": 0
            }
        
        # Analyze emotion distribution
        emotion_counts = Counter(emotions_detected)
        total = len(emotions_detected)
        
        emotion_distribution = {
            emotion: count / total 
            for emotion, count in emotion_counts.items()
        }
        
        # Get dominant emotions (top 3)
        dominant = [emotion for emotion, _ in emotion_counts.most_common(3)]
        
        # Calculate engagement score
        engagement_score = self._calculate_engagement(emotion_distribution)
        
        return {
            "dominant_emotions": dominant,
            "emotion_distribution": emotion_distribution,
            "average_confidence": 0.75,  # Placeholder
            "engagement_score": engagement_score,
            "frames_analyzed": total_analyzed
        }
    
    def _detect_emotion(self, frame: np.ndarray) -> str:
        """Detect dominant emotion in a single frame"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = self.emotion_detector.detect_emotions(rgb_frame)
            
            if result and len(result) > 0 and 'emotions' in result[0]:
                emotions = result[0]['emotions']
                return max(emotions, key=emotions.get)
        except Exception as e:
            print(f"Error detecting emotion: {e}")
        
        return None
    
    def _calculate_engagement(self, emotion_dist: Dict[str, float]) -> float:
        """
        Calculate engagement score (0-100) based on emotions
        Positive emotions = higher engagement
        """
        positive_emotions = ['happy', 'surprise']
        neutral_emotions = ['neutral']
        negative_emotions = ['sad', 'angry', 'fear', 'disgust']
        
        score = 0.0
        
        for emotion, weight in emotion_dist.items():
            if emotion in positive_emotions:
                score += weight * 100
            elif emotion in neutral_emotions:
                score += weight * 50
            # Negative emotions don't add to score
        
        return round(score, 2)