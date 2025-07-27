#Emotion detection logic
from transformers import pipeline

emotion_pipeline = pipeline("audio-classification", model="superb/wav2vec2-base-superb-er")

def analyze_emotion(filepath: str):
    result = emotion_pipeline(filepath)
    top_emotion = sorted(result, key=lambda x: -x['score'])[0]
    return {
        "label": top_emotion['label'],
        "score": round(top_emotion['score'], 3)
    }
