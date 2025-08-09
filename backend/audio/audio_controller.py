import os, shutil
from pathlib import Path
from fastapi import UploadFile
from .audio_analysis_service import chunk_audio, predict_tone, update_tone_json
from .audio_transcribe_service import update_conv_history_json, transcribe_audio_file

REPORTS_DIR = Path("end/reports")

"""
Handles the tone analysis pipeline:
1. Uses the saved audio file at file_path.
2. Calls chunk_audio() to split into 5-sec segments.
3. Calls predict_tone() to classify each chunk.
4. Updates tone.json with the detected tones.
"""
async def run_audio_analysis(resume_id: str, file_path: str, question_id: str):
    try:
        print(f"🎧 Starting tone analysis for {resume_id} - {question_id}")
        
        # Chunk audio into 5-sec pieces
        chunks = await chunk_audio(file_path, chunk_length=5)
        print(f"📦 {len(chunks)} audio chunks created.")

        # Predict tone
        tone = await predict_tone   (chunks)
        print(f"✅ Predicted tone: {tone}")

        # Update tone.json
        await update_tone_json(resume_id=resume_id, question_id=question_id, tone=tone)

        return {
            "question_id": question_id,
            "tone": tone
        }

    except Exception as e:
        print(f"❌ Error in run_audio_analysis: {e}")
        raise  # Re-raise to surface it to the router


"""
Handles the audio transcription pipeline:
1. Uses the saved audio file at file_path.
2. Calls transcribe_audio_file() to run STT.
3. Updates conv_history.json with the transcript.
"""
async def run_audio_transcribe(resume_id: str, question: str, file_path: str, q_id:str):
    try:
        transcript = await transcribe_audio_file(file_path)
        print(f"📥 Created transcript for {file_path} (resume: {resume_id}, question: {question})")
        if not transcript:
            transcript = ""
            print("⚠️ Transcript empty or failed.")

        await update_conv_history_json(resume_id, question, transcript, q_id)
        print(f"✅ conv_history.json updated for {question}")

        return {
            "question": question,
            "transcript": transcript
        }
    except Exception as e:
        print(f"❌ Error in run_audio_transcribe: {e}")
        return {"question_id":question, "transcript":""}


"""Helper function to save audio files. Used in audio _router.py"""
def save_uploaded_file(file: UploadFile, resume_id: str, filename: str) -> str:
    user_dir = REPORTS_DIR/resume_id
    user_dir.mkdir(parents=True, exist_ok=True)

    file_path = user_dir / filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return str(file_path)