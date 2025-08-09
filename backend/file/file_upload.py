import os, re, json
from pathlib import Path
from fastapi import UploadFile

UPLOAD_DIR = Path("file/uploads")
REPORTS_DIR = Path("end/reports")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def _sanitize_resume_id(resume_id: str)->str:
    rid = resume_id.strip().lower().replace(" ", "_")
    return re.sub(r"[^a-z_]", "", rid)


"""Saves the uploaded resume file and initializes empty report files. Returns the saved filename."""
def save_resume_and_init_reports(file: UploadFile, resume_id: str) ->tuple[str, str]: 
    resume_id = _sanitize_resume_id(resume_id)

    ext = Path(file.filename).suffix.lower()
    if ext not in {".pdf", ".docx"}:
        raise ValueError("Only PDF/DOCX files allowed")
    
    save_filename = f"{resume_id}{ext}"
    save_path = UPLOAD_DIR / save_filename
    file.file.seek(0)
    # Save uploaded PDF
    with open(save_path, "wb") as f:
        f.write(file.file.read())

    # Create reports directory
    resume_report_dir = REPORTS_DIR / resume_id
    os.makedirs(resume_report_dir, exist_ok=True)

    for report_name in ["emotion", "tone", "conv_history", "summary"]:
        with open(resume_report_dir / f"{report_name}.json", "w", encoding="utf-8") as f:
            json.dump({}, f)

    print(f"✅ Resume saved to: {save_path}")
    print(f"📁 Report directory: {resume_report_dir}")

    return save_filename, resume_id
