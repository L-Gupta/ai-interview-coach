from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import shutil, os, subprocess
from .audio_transcriber import transcribe_audio

router = APIRouter()

# ✅ 1. /stt converts audio to transcript
@router.post("/stt")
async def speech_to_text(file: UploadFile = File(...)):
    upload_dir = "audio/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    webm_path = os.path.join(upload_dir, file.filename)

    with open(webm_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Convert WebM -> WAV (16kHz PCM)
    wav_path = webm_path.replace(".webm", ".wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", webm_path,
        "-ar", "16000", "-ac", "1",
        wav_path
    ], check=True)

    transcript = transcribe_audio(wav_path)
    return {"transcript": transcript}

# ✅ 2. /analyze-audio sends transcript to Gemini and returns follow-up
class TranscriptPayload(BaseModel):
    transcript: str
    timestamp: str

@router.post("/analyze-audio")
async def analyze_audio(data: TranscriptPayload):
    print(f"🎤 Received transcript: {data.transcript}")
    # 👉 Placeholder for Gemini call
    next_q = "Tell me about yourself"
    return {"next_question": next_q}
