from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import os
from pathlib import Path
from video.video_controller import analyze_video_for_question

router = APIRouter(tags=["Video"])

@router.post("/video-upload")
async def upload_video(resume_id = Form(...), question_id: str = Form(...), video: UploadFile = File(...)):
    try:
        # ✅ Ensure folder exists
        user_dir = Path("data" / resume_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        # ✅ Save video file
        filename = f"{question_id}ans.webm"
        file_path = user_dir / filename
        with open(file_path, "wb") as f:
            f.write(await video.read())

        return {"message": "Video uploaded successfully", "path": str(file_path)}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/video-analyze")
async def analyze_video(resume_id: str = Form(...), question_id: str = Form(...)):
    try:
        result = await analyze_video_for_question(resume_id, question_id)
        return {"emotions": result["emotions"]}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

