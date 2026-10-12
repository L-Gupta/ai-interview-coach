from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./interview_coach.db"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Services
    GEMINI_API_KEY: str = "your-gemini-api-key"
    DEEPGRAM_API_KEY: str = "your-deepgram-api-key"
    
    # Pinecone
    PINECONE_API_KEY: str = "your-pinecone-api-key"
    PINECONE_ENVIRONMENT: str = "us-east-1-aws"
    PINECONE_INDEX_NAME: str = "interview-index"
    
    # LangSmith (Optional)
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: Optional[str] = None
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "interview-coach"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # App Config
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    PORT: int = 8000
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "./uploads"
    REPORTS_DIR: str = "./reports"
    
    class Config:
        # .env lives at the project root (two levels above backend/core/)
        env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)