from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database.session import get_db
from models.database import User, InterviewSession, QuestionAnswer, Resume
from models.schemas import InterviewSessionCreate, InterviewSessionResponse, QuestionResponse, AnswerSubmit
from auth.dependencies import get_current_active_user
from agents.orchestrator import InterviewOrchestrator
from pathlib import Path
import uuid
import shutil

router = APIRouter(prefix="/interview", tags=["Interview"])

# Store active orchestrators in memory (use Redis in production)
active_sessions = {}

@router.post("/start", response_model=InterviewSessionResponse)
async def start_interview(
    session_data: InterviewSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a new interview session"""
    
    # Verify resume exists and belongs to user
    resume = db.query(Resume).filter(
        Resume.resume_id == session_data.resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Create session
    session_id = str(uuid.uuid4())
    new_session = InterviewSession(
        session_id=session_id,
        user_id=current_user.id,
        resume_id=resume.id,
        job_role=session_data.job_role,
        status="active",
        questions_asked=[],
        current_question_index=0,
        agent_memory={}
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    # Initialize orchestrator
    orchestrator = InterviewOrchestrator(
        session_id=session_id,
        resume_id=session_data.resume_id,
        job_role=session_data.job_role
    )
    active_sessions[session_id] = orchestrator
    
    return new_session

@router.get("/{session_id}/question", response_model=QuestionResponse)
async def get_next_question(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the next interview question"""
    
    # Verify session
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.status != "active":
        raise HTTPException(status_code=400, detail="Interview session is not active")
    
    # Get orchestrator
    if session_id not in active_sessions:
        raise HTTPException(status_code=400, detail="Session orchestrator not found. Please restart interview.")
    
    orchestrator = active_sessions[session_id]
    
    # Check if interview is complete
    if orchestrator.is_interview_complete():
        session.status = "completed"
        db.commit()
        raise HTTPException(status_code=400, detail="Interview is complete")
    
    # Generate question
    question_text = orchestrator.get_current_question()
    question_number = len(orchestrator.memory.conversation_history) + 1
    
    return {
        "question_number": question_number,
        "question_text": question_text,
        "session_id": session_id
    }

@router.post("/{session_id}/answer")
async def submit_answer(
    session_id: str,
    question_number: int = Form(...),
    question_text: str = Form(...),
    answer_text: str = Form(...),
    audio_file: UploadFile = File(None),
    video_file: UploadFile = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit an answer with optional audio/video"""
    
    # Verify session
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get orchestrator
    if session_id not in active_sessions:
        raise HTTPException(status_code=400, detail="Session not found")
    
    orchestrator = active_sessions[session_id]
    
    # Save media files
    audio_path = None
    video_path = None
    
    media_dir = Path(f"./reports/{session_id}")
    media_dir.mkdir(parents=True, exist_ok=True)
    
    if audio_file:
        audio_path = media_dir / f"q{question_number}_audio.wav"
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(audio_file.file, f)
    
    if video_file:
        video_path = media_dir / f"q{question_number}_video.webm"
        with open(video_path, "wb") as f:
            shutil.copyfileobj(video_file.file, f)
    
    # Process answer through agents
    analysis_results = orchestrator.process_answer(
        question=question_text,
        answer=answer_text,
        audio_path=str(audio_path) if audio_path else None,
        video_path=str(video_path) if video_path else None
    )
    
    # Save to database
    qa_record = QuestionAnswer(
        session_id=session.id,
        question_number=question_number,
        question_text=question_text,
        answer_text=answer_text,
        audio_file_path=str(audio_path) if audio_path else None,
        video_file_path=str(video_path) if video_path else None,
        audio_analysis=analysis_results.get("audio_analysis"),
        video_analysis=analysis_results.get("video_analysis"),
        integrity_flags=analysis_results.get("integrity_check", {}).get("violations_summary", {})
    )
    
    db.add(qa_record)
    session.current_question_index = question_number
    db.commit()
    
    return {
        "status": "success",
        "message": "Answer submitted successfully",
        "analysis": analysis_results,
        "interview_complete": orchestrator.is_interview_complete()
    }

@router.get("/{session_id}/status")
async def get_session_status(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get interview session status"""
    
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id,
        InterviewSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    is_complete = False
    if session_id in active_sessions:
        orchestrator = active_sessions[session_id]
        is_complete = orchestrator.is_interview_complete()
    
    return {
        "session_id": session_id,
        "status": session.status,
        "current_question": session.current_question_index,
        "is_complete": is_complete
    }