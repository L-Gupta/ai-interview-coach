from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import requests
import os
from dotenv import load_dotenv

from fileUpload.file_upload import router as file_router
from ques_gen.router_ques_first import router as ques_router
from ques_gen.router_ques_next import router as next_router
from audio.audio_router import router as audio_router

load_dotenv()

app = FastAPI(title="AI Interview Coach API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Interview route
app.include_router(file_router, prefix="/file")
app.include_router(audio_router, prefix="/audio")
app.include_router(ques_router, prefix="/question")
app.include_router(next_router, prefix="/question")

@app.get("/")
async def root():
    return {"message": "AI Interview Coach API is running!"}

@app.post("/analyze-audio/")
async def analyze_audio(file: UploadFile = File(...)):
    temp_dir = os.path.join(os.path.dirname(__file__), "audio", "recordings")
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    with open(file_path, "rb") as f:
        audio_data = f.read()

    headers = {
        "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
        "Content-Type": "audio/wav"
    }

    response = requests.post(
        "https://api.deepgram.com/v1/listen",
        headers=headers,
        data=audio_data
    )

    if response.status_code != 200:
        return { "transcript": "Transcription failed." }

    transcript = response.json()['results']['channels'][0]['alternatives'][0]['transcript']
    return { "transcript": transcript }
