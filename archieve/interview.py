from fastapi import APIRouter
from services.gemini import generate_response
from fastapi import UploadFile, File, Form
from services import resume_parser
from services.gemini import generate_question_with_resume

router = APIRouter()

@router.get("/generate-question")
async def generate_interview_question(role: str = "software engineer"):
    return {"question": generate_response(role)}

@router.post("/upload-resume")
async def upload_resume_and_generate(
    file: UploadFile = File(...),
    role: str = Form("software engineer")):
    
    contents = await file.read()
    
    #.pdf file
    if file.filename.endswith(".pdf"):
        text = resume_parser.extract_text_from_pdf(contents)

    #.docx file
    elif file.filename.endswith(".docx"):
        text = resume_parser.extract_text_from_docx(contents)

    #other file
    else:
        return {"error": "Unsupported file type. Please upload .pdf or .docx"}

    question = generate_question_with_resume(text[:3000], role)  # Limit size for Gemini
    return {"role": role,
            "resume_excerpt": text[:500],
            "generated_question": question}