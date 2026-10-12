from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interview_sessions = relationship("InterviewSession", back_populates="user")
    resumes = relationship("Resume", back_populates="user")

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(String, unique=True, index=True, nullable=False)  # UUID
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="resumes")
    interview_sessions = relationship("InterviewSession", back_populates="resume")

class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    
    # Interview metadata
    job_role = Column(String, nullable=False)
    status = Column(String, default="active")  # active, completed, abandoned
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Interview data
    questions_asked = Column(JSON, default=list)  # List of questions
    current_question_index = Column(Integer, default=0)
    
    # Agent state
    agent_memory = Column(JSON, default=dict)  # Stores agent's memory/context
    
    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    resume = relationship("Resume", back_populates="interview_sessions")
    qa_pairs = relationship("QuestionAnswer", back_populates="session")
    integrity_logs = relationship("IntegrityLog", back_populates="session")
    final_report = relationship("InterviewReport", back_populates="session", uselist=False)

class QuestionAnswer(Base):
    __tablename__ = "question_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)
    
    # Media files
    audio_file_path = Column(String, nullable=True)
    video_file_path = Column(String, nullable=True)
    
    # Analysis results
    audio_analysis = Column(JSON, nullable=True)  # Tone, emotion from audio
    video_analysis = Column(JSON, nullable=True)  # Facial expressions, eye contact
    integrity_flags = Column(JSON, default=list)  # Cheating detection flags
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="qa_pairs")

class IntegrityLog(Base):
    __tablename__ = "integrity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    
    # Violation types
    violation_type = Column(String, nullable=False)  # multiple_faces, gaze_off_screen, reading_detected
    severity = Column(String, default="low")  # low, medium, high
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="integrity_logs")

class InterviewReport(Base):
    __tablename__ = "interview_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), unique=True, nullable=False)
    
    # Scores
    overall_score = Column(Float, nullable=True)
    job_fit_score = Column(Float, nullable=True)
    accuracy_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Analysis summaries
    tone_summary = Column(Text, nullable=True)
    expression_summary = Column(Text, nullable=True)
    strengths = Column(JSON, default=list)
    weaknesses = Column(JSON, default=list)
    suggestions = Column(JSON, default=list)
    
    # Integrity summary
    integrity_score = Column(Float, default=100.0)
    integrity_violations = Column(JSON, default=list)
    
    # Full report data
    full_report_json = Column(JSON, nullable=True)
    pdf_file_path = Column(String, nullable=True)
    
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="final_report")