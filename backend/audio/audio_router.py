from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from .audio_controller import run_audio_analysis, run_audio_transcribe, save_uploaded_file

router = APIRouter(tags=["Audio"])

@router.post("/tone-analysis")
async def analyze_audio(file: UploadFile = File(...), resume_id:str = Form(...), question_id: str = Form(...)):
    try:
        # Save the file under qXans.wav
        file_path = save_uploaded_file(file, resume_id, f"{question_id}ans.wav")

        # Call the controller with resume_id, file path and question_id
        result = await run_audio_analysis(resume_id=resume_id, file_path=file_path, question_id=question_id)
        tones = result.get("tone", [])

        # Return the analysis results to the frontend
        return JSONResponse(content={question_id:tones})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@router.post("/audio-transcribe")
async def audio_transcribe(file: UploadFile = File(...), resume_id: str = Form(...), question_id: str = Form(...), question:str = Form(...)):
    try:
        # Save the file under qXans.wav
        file_path = save_uploaded_file(file, resume_id, f"{question_id}ans.wav")

        # Call controller to handle transcription and saving
        result = await run_audio_transcribe(resume_id=resume_id, question=question, file_path=str(file_path), q_id=question_id)

        # Return result from controller directly
        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)