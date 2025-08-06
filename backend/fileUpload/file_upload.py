from fastapi import APIRouter, UploadFile, File, HTTPException
import os, json
from pathlib import Path
from fileUpload.run_resume import run_pipeline
from shutil import copyfile

router = APIRouter(tags=["Resume upload"])

UPLOAD_DIR = Path("fileUpload/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

REPORTS_DIR = Path("end/reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    filename = Path(file.filename.strip()).name
    if not filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")

    #Save uploaded file name into uploads
    save_path = os.path.join(UPLOAD_DIR, filename)
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # ✅ Use filename (without extension) as resume_id
    resume_id = Path(filename).stem
    resume_report_dir = REPORTS_DIR / resume_id
    os.makedirs(resume_report_dir, exist_ok=True)

    # ✅ Create initial JSON files
    emotion_path = resume_report_dir / "emotion.json"
    with open(emotion_path, "w", encoding="utf-8") as f:
        json.dump({}, f)
    tone_path = resume_report_dir / "tone.json"
    with open(tone_path, "w", encoding="utf-8") as f:
        json.dump({}, f)
    conv_history_path = resume_report_dir / "conv_history.json"
    with open(conv_history_path, "w", encoding="utf-8") as f:
        json.dump({}, f)
    summary_path = resume_report_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({}, f)

    try:
        result = run_pipeline(filename)
        return {
            "message": "Resume processed successfully",
            "filename": filename,
            "resume_id" : resume_id,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

