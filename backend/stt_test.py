from fastapi import FastAPI, UploadFile, File
from services.audio_handler import save_audio_file
from backend.services.stt_deepgram import transcribe_audio
from services.emotion_model import analyze_emotion
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

app = FastAPI()

@app.post("/analyze-audio/")
async def analyze_audio(file: UploadFile = File(...)):
    filepath = await save_audio_file(file)
    transcript = transcribe_audio(filepath)
    emotion_result = analyze_emotion(filepath)

    return {
        "transcript": transcript,
        "emotion": emotion_result
    }
