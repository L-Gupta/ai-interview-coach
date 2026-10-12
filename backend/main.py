from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from core.config import settings
from database.session import init_db
from api.v1 import auth, interview
from file.agentic_file_router import router as file_router
import os

# Initialize FastAPI app
app = FastAPI(
    title="AI Interview Coach API",
    description="Agentic interview coaching system with advanced cheating detection",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Auth and Interview have internal prefixes, so we add /api/v1 to the base path
app.include_router(auth.router, prefix="/api/v1")
app.include_router(interview.router, prefix="/api/v1")
app.include_router(file_router, prefix="/api/v1/file", tags=["File Processing"])

# Serve static files (for reports/media)
if os.path.exists("./reports"):
    app.mount("/reports", StaticFiles(directory="./reports"), name="reports")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting AI Interview Coach API...")
    init_db()
    print("✅ Database initialized")
    print(f"📡 Server running on port {settings.PORT}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI Interview Coach API v2.0",
        "features": [
            "Agentic question generation",
            "Advanced cheating detection",
            "Audio/Video analysis",
            "Multi-agent orchestration"
        ]
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "agents": "initialized"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )