from datetime import datetime
#from .audio_recorder import record_audio
#from .audio_transcriber import transcribe_audio
from audio_recorder import record_audio
from audio_transcriber import transcribe_audio
import os
from dotenv import load_dotenv
from pathlib import Path
import requests

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

def main():
    print("🎙️ AI Interview Coach – Voice Input")

    # Step 1: Record audio and get path
    audio_path = record_audio()
    if not audio_path:
        print("❌ Recording failed.")
        return

    # Step 2: Transcribe
    print("🧠 Transcribing audio...")
    transcript = transcribe_audio(audio_path)

    if not transcript:
        print("❌ Transcription failed.")
        return

    print("✅ Transcript:")
    print(transcript)

    # Step 3: Save transcript
    timestamp = os.path.basename(audio_path).replace("recording_", "").replace(".wav", "")
    transcripts_dir = os.path.join(os.path.dirname(__file__), "transcripts")
    os.makedirs(transcripts_dir, exist_ok=True)

    transcript_filename = f"transcript_{timestamp}.txt"
    transcript_path = os.path.join(transcripts_dir, transcript_filename)

    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(transcript)

    print(f"📄 Transcript saved at: {transcript_path}")
    print(f"📁 Audio saved at: {audio_path}")

    # Step 4: Send to backend
    BACKEND_URL = os.getenv("AI_COACH_BACKEND_URL", "http://127.0.0.1:8000/analyze-audio")
    payload = {
        "transcript": transcript,
        "timestamp": datetime.now().isoformat()
    }

    try:
        response = requests.post(BACKEND_URL, json=payload)
        response.raise_for_status()
        next_q = response.json().get("next_question", "")
        print("\n🎯 Gemini Follow-up Question:")
        print(next_q)
    except Exception as e:
        print(f"❌ Failed to send transcript: {e}")

if __name__ == "__main__":
    main()
