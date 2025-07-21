from fastapi import APIRouter, UploadFile, File
from services.parser import extract_text_from_pdf
from services.embedding import embed_and_store
import shutil
import os

router = APIRouter()

@router.post("/upload_resume/")
async def upload_resume(file: UploadFile = File(...)):
    os.makedirs("temp", exist_ok=True)
    file_location = f"temp/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text_from_pdf(file_location)
    os.remove(file_location)

    return {"extracted_text": text[:2000]}

@router.post("/upload_and_embed_resume/")
async def upload_and_embed(file: UploadFile = File(...)):
    os.makedirs("temp", exist_ok=True)
    file_location = f"temp/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text_from_pdf(file_location)
    os.remove(file_location)

    result = embed_and_store(text, namespace="resume")

    return {"message": "Resume parsed and embedded", "details": result}
