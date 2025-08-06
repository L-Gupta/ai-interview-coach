import os
from pathlib import Path
from video.frame_utils import extract_frames
from video.analyze_emotions import get_emotion, aggregate_emotions, save_emotion_json
from video.video_utils import estimate_eye_contact, detect_multiple_faces, detect_face_absence, count_distractions

REPORTS_DIR = Path("end/reports")

"""Runs emotion analysis for a single question's video and returns dominant emotions."""
"""
Args:
    resume_id (str): ID of the interviewee
    question_id (str): e.g., "q1"

Returns:
    dict: { "emotions": ["happy", "neutral"] }
"""
async def analyze_video_for_question(resume_id: str, question_id: str) -> dict:
    # 1. Locate the video file
    video_path = REPORTS_DIR / resume_id / f"{question_id}ans.webm"
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found at {video_path}")

    # 2. Extract frames from the video
    frames = extract_frames(str(video_path), fps=5)
    if not frames:
        raise ValueError("No frames extracted from video.")

    # 3. Detect emotions
    emotion_predictions = [get_emotion(frame) for frame in frames if get_emotion(frame)]
    if not emotion_predictions:
        raise ValueError("No emotions detected in video.")
    dominant_emotions = aggregate_emotions(emotion_predictions)

    # 4. Compute integrity/distraction metrics
    eye_contact = estimate_eye_contact(frames)
    distractions = count_distractions(frames)
    multi_person = detect_multiple_faces(frames)
    face_absence = detect_face_absence(frames)

    # 4. Aggregate dominant emotions
    dominant_emotions = aggregate_emotions(emotion_predictions)

    # 5. Save to emotion.json
    save_emotion_json(resume_id, question_id, {
        "emotions": dominant_emotions,
        "eye contact": eye_contact,
        "distractions": distractions,
        "multi person": multi_person,
        "face absence": face_absence
        }
    )

    # 6. Return the result
    return { "emotions": dominant_emotions }
