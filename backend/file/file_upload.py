"""
File Upload Utility
Handles saving uploaded resume files and initializing report directories.
"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile
import shutil

UPLOAD_DIR = Path("file/uploads")
REPORTS_DIR = Path("end/reports")

def save_resume_and_init_reports(file: UploadFile, resume_id: str) -> tuple[str, str]:
    """
    Save uploaded resume and create report directories.
    
    Args:
        file: Uploaded file from FastAPI
        resume_id: User-provided resume identifier
        
    Returns:
        tuple: (saved_filename, sanitized_resume_id)
    """
    # Ensure directories exist
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sanitize resume_id
    safe_resume_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in resume_id)
    if not safe_resume_id:
        safe_resume_id = str(uuid.uuid4())
    
    # Get file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".pdf", ".docx"]:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    # Create filename
    save_filename = f"{safe_resume_id}{file_ext}"
    save_path = UPLOAD_DIR / save_filename
    
    # Save file
    with save_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create report directory for this resume
    report_dir = REPORTS_DIR / safe_resume_id
    report_dir.mkdir(exist_ok=True)
    
    print(f"✅ Saved: {save_path}")
    print(f"✅ Report dir: {report_dir}")
    
    return save_filename, safe_resume_id


def get_upload_path(filename: str) -> Path:
    """Get full path to uploaded file."""
    return UPLOAD_DIR / filename


def get_report_dir(resume_id: str) -> Path:
    """Get report directory for resume."""
    return REPORTS_DIR / resume_id
