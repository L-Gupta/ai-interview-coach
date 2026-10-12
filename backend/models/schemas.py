from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ============= Auth Schemas =============
class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============= Resume Schemas =============
class ResumeUploadResponse(BaseModel):
    resume_id: str
    filename: str
    uploaded_at: datetime
    processed: bool

# ============= Interview Session Schemas =============
class InterviewSessionCreate(BaseModel):
    resume_id: str
    job_role: str

class InterviewSessionResponse(BaseModel):
    session_id: str
    job_role: str
    status: str
    current_question_index: int
    started_at: datetime
    
    class Config:
        from_attributes = True

class QuestionResponse(BaseModel):
    question_number: int
    question_text: str
    session_id: str

class AnswerSubmit(BaseModel):
    session_id: str
    question_number: int
    answer_text: Optional[str] = None

# ============= Analysis Schemas =============
class AudioAnalysisResult(BaseModel):
    tone: List[str]
    dominant_tone: str
    confidence: float
    emotions: List[str]

class VideoAnalysisResult(BaseModel):
    dominant_emotions: List[str]
    eye_contact_percentage: float
    average_confidence: float
    engagement_score: float

class IntegrityCheckResult(BaseModel):
    multiple_faces_detected: bool
    gaze_off_screen: bool
    reading_detected: bool
    overall_integrity_score: float
    violations: List[Dict[str, Any]]

# ============= Report Schemas =============
class InterviewReportResponse(BaseModel):
    session_id: str
    overall_score: float
    job_fit_score: float
    accuracy_score: float
    communication_score: float
    confidence_score: float
    
    tone_summary: str
    expression_summary: str
    
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    
    integrity_score: float
    integrity_violations: List[Dict[str, Any]]
    
    pdf_url: Optional[str]
    generated_at: datetime
    
    class Config:
        from_attributes = True

# ============= Agent Schemas =============
class AgentDecision(BaseModel):
    """Schema for agent decision-making process"""
    thought: str
    action: str
    action_input: Dict[str, Any]
    observation: Optional[str] = None
    
class AgentState(BaseModel):
    """Schema for tracking agent state"""
    session_id: str
    current_goal: str
    completed_goals: List[str]
    context: Dict[str, Any]
    next_action: Optional[str] = None