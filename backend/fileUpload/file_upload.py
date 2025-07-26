from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from pathlib import Path
from fileUpload.run_resume import run_pipeline
from shutil import copyfile

router = APIRouter()

UPLOAD_DIR = Path("fileUpload/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    filename = Path(file.filename.strip()).name
    if not filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")

    save_path = os.path.join(UPLOAD_DIR, filename)
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:
        result = run_pipeline(filename)
        return {
            "message": "Resume processed successfully",
            "filename": filename,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Manual local testing
def upload_resume_from_local(local_file_path: str):
    from run_resume import run_pipeline
    filename = Path(local_file_path).name

    if not filename.endswith((".pdf", ".docx")):
        raise ValueError("Only PDF and DOCX files are allowed.")

    target_path = UPLOAD_DIR / filename
    copyfile(local_file_path, target_path)

    try:
        result = run_pipeline(filename)
        return {
            "message": "Manual resume processed successfully",
            "filename": filename,
            **result
        }
    except Exception as e:
        raise e
