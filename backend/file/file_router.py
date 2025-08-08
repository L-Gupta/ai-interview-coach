from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from file.file_upload import save_resume_and_init_reports
from file.file_controller import run_pipeline

router = APIRouter(tags=["Resume upload"])

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), resume_id: str = Form(...)):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed.")

    try:
        save_filename = save_resume_and_init_reports(file, resume_id)
        result = run_pipeline(save_filename, resume_id=resume_id)

        return {
            "message": "Resume processed successfully",
            "filename": save_filename,
            "resume_id": resume_id,
            **result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
