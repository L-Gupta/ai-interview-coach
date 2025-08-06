from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

import requests
import os
from dotenv import load_dotenv

from fileUpload.file_upload import router as file_router
from ques_gen.question_router import router as question_router
from audio.audio_router import router as audio_router
from end.end_router import router as end_router
from video.video_router import router as video_router

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
app.include_router(audio_router)
app.include_router(question_router, prefix="/question")
app.include_router(end_router)
app.include_router(video_router, prefix="/video")

@app.get("/")
async def root():
    return {"message": "AI Interview Coach API is running!"}

