from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from routes import question_generator  # New merged router
from typing import List
from services.audio_handler import save_audio_file
from services.stt_deepgram import transcribe_audio
from services.emotion_model import analyze_emotion

app = FastAPI(title="AI Interview Coach API", version="1.0.0")

# Allow frontend requests (React on localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Include unified question generator route
app.include_router(question_generator.router, prefix="/questions")

@app.get("/")
async def root():
    return {"message": "AI Interview Coach API is running!"}

@app.post("/analyze-audio/")
async def analyze_audio(file: UploadFile = File(...)):
    #Save file
    filepath = await save_audio_file(file)          

    #Transcribe audio
    try:
        transcript = transcribe_audio(filepath)
    except Exception as e:
        transcript = f"❌ Transcription error: {str(e)}"

    #Analyze emotion
    try:
        emotion_result = analyze_emotion(filepath)
    except Exception as e:
        emotion_result = {"label": "error", "score": 0, "message": str(e)}

    return {
        "transcript": transcript,
        "emotion": emotion_result
    }

# Temporary session store
session_responses = []

@app.post("/submit-answer/")
async def submit_answer(
    question_index: int = Body(...),
    question: str = Body(...),
    transcript: str = Body(...),
    emotion: dict = Body(...)
):
    session_responses.append({
        "question_index": question_index,
        "question": question,
        "transcript": transcript,
        "emotion": emotion
    })
    return {"message": "Answer submitted successfully."}

