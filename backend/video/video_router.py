from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import os
from pathlib import Path
from video.video_controller import analyze_video_for_question

router = APIRouter(tags=["Video"])

REPORTS_DIR = Path("end/reports")

@router.post("/video-upload")
async def upload_video(resume_id: str = Form(...), question_id: str = Form(...), video: UploadFile = File(...)):
    try:
        user_dir = REPORTS_DIR / resume_id
        user_dir.mkdir(parents=True, exist_ok=True)
        file_path = user_dir / f"{question_id}ans.webm"
        with open(file_path, "wb") as f:
            f.write(await video.read())
        return {"message": "Video uploaded successfully", "path": str(file_path)}
    except Exception as e:
        print("[ERROR] Video upload:", e)
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/video-analyze")
async def analyze_video(resume_id: str = Form(...), question_id: str = Form(...)):
    try:
        result = await analyze_video_for_question(resume_id, question_id)
        return {"emotions": result.get("emotions", [])}
    except Exception as e:
        print("[ERROR] Video analyze:", e)
        # Return safe empty emotions instead of 500
        return JSONResponse(status_code=200, content={"emotions": []})