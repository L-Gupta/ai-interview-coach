from fer import FER
from collections import Counter
import cv2, json
from pathlib import Path

REPORTS_DIR = Path("end/reports")

# Load the model globally to avoid reloading per frame
_emotion_detector = FER(mtcnn=False)

"""Detects the dominant emotion in a single video frame."""
"""
Args:
    frame: A BGR image (as returned by OpenCV)

Returns:
    str: Detected emotion label (e.g., "happy", "neutral") or None
"""
def get_emotion(frame) -> str:   
    try:
        # Convert to RGB (FER expects RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        emotions = _emotion_detector.detect_emotions(rgb_frame)

        if emotions and "emotions" in emotions[0]:
            # Return the emotion with highest confidence
            return max(emotions[0]["emotions"], key=emotions[0]["emotions"].get)

    except Exception as e:
        print(f"[ERROR] get_emotion failed: {e}")

    return None

"""Aggregates the most common emotions from a list of predictions."""
"""
Args:
    emotion_list (list): List of emotion labels (e.g., ["happy", "neutral", "happy"])
    top_n (int): Number of top emotions to return

Returns:
    list: Top `n` most frequent emotions in descending order
"""
def aggregate_emotions(emotion_list: list, top_n: int = 2) -> list:
    
    if not emotion_list:
        return []

    counter = Counter(emotion_list)
    return [emotion for emotion, _ in counter.most_common(top_n)]

"""Saves the full emotion, distraction, and integrity data into emotion.json"""
def save_emotion_json(resume_id: str, question_id: str, analysis_list: dict):
    report_path = REPORTS_DIR / resume_id / "emotion.json"

    # Ensure parent folder exists
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing data or initialize
    try:
        if report_path.exists():
            with open(report_path, "r") as f:
                data = json.load(f)
        else:
            data = {}
    except Exception as e:
        print(f"[WARN] Failed to read emotion.json: {e}")
        data = {}

    data[question_id] = analysis_list

    # Save JSON
    try:
        with open(report_path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to write emotion.json: {e}")

