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
    # 1) locate
    video_path = REPORTS_DIR / resume_id / f"{question_id}ans.webm"
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found at {video_path}")

    # 2) extract frames
    frames = extract_frames(str(video_path), fps=5)
    if not frames:
        # Fallback: return neutral/empty but DO NOT 500
        print("[ERROR] No frames extracted from video.")
        save_emotion_json(resume_id, question_id, {
            "emotions": [],
            "eye contact": 0,
            "distractions": 0,
            "multi person": False,
            "face absence": 0
        })
        return {"emotions": []}

    # 3) emotions (safe)
    try:
        preds = []
        for fr in frames:
            emo = get_emotion(fr)
            if emo:
                preds.append(emo)
        dominant_emotions = aggregate_emotions(preds) if preds else []
    except Exception as e:
        print("[ERROR] Emotion detection failed:", e)
        dominant_emotions = []

    # 4) integrity metrics (each safe)
    try:
        eye_contact = estimate_eye_contact(frames)
    except Exception as e:
        print("[ERROR] estimate_eye_contact failed:", e)
        eye_contact = 0

    try:
        distractions = count_distractions(frames)
    except Exception as e:
        print("[ERROR] count_distractions failed:", e)
        distractions = 0

    try:
        multi_person = detect_multiple_faces(frames)
    except Exception as e:
        print("[ERROR] detect_multiple_faces failed:", e)
        multi_person = False

    try:
        face_absence = detect_face_absence(frames)
    except Exception as e:
        print("[ERROR] detect_face_absence failed:", e)
        face_absence = 0

    # 5) save json (safe)
    try:
        save_emotion_json(resume_id, question_id, {
            "emotions": dominant_emotions,
            "eye contact": eye_contact,
            "distractions": distractions,
            "multi person": multi_person,
            "face absence": face_absence
        })
    except Exception as e:
        print("[WARN] save_emotion_json failed:", e)

    # 6) return minimal payload
    return {"emotions": dominant_emotions}