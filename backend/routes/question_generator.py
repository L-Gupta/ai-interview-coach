from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from config.settings import settings
from services.parser import parse_resume
import google.generativeai as genai
from services.gemini import generate_response

router = APIRouter()
genai.configure(api_key=settings.GEMINI_API_KEY)

@router.post("/generate")
async def generate_questions(
    resume: UploadFile = File(...), 
    role: str = Form(...)):
    
    try:
        if resume.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            raise HTTPException(status_code=400, detail="Only PDF or DOCX files are supported.")

        contents = await resume.read()
        text = parse_resume(contents, resume.content_type)

        prompt = (
            f"You are an expert interviewer. Based on the resume text below "
            f"and the job role '{role}', generate 5 personalized, role-specific interview questions.\n\n"
            f"Resume:\n{text}"
        )

        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        questions = response.text.strip().split("\n")
        cleaned = [q.lstrip("1234567890.●- ").strip() for q in questions if q.strip()]

        return JSONResponse(content={"questions": cleaned})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/generate-one")
async def generate_single_question(
    resume: UploadFile = File(...), 
    role: str = Form("software engineer")):

    try:
        contents = await resume.read()
        text = parse_resume(contents, resume.content_type)

        prompt = (
            f"As an expert interviewer, generate a single deep, role-specific interview question "
            f"based on the following resume for the role '{role}':\n\n"
            f"{text[:3000]}"
        )

        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
        return {"question": response.text.strip()}
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    
@router.get("/generate-from-role")
async def generate_role_question(role: str = "software engineer"):
    return {"question": generate_response(role)}
