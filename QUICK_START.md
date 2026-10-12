# Quick Start Guide

## ✅ Current Status
- Python 3.12.6 environment ready
- All 120+ packages installed
- FER emotion detection working
- All agents verified

## 🚀 Start Development

### 1. Activate Virtual Environment (if not active)
```powershell
cd C:\Users\laksh\ai-agent-interview-coach\backend
.\venv\Scripts\Activate.ps1
```

### 2. Set Up Environment Variables
Create `.env` in the project root:
```env
SECRET_KEY=your-jwt-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
DEEPGRAM_API_KEY=your-deepgram-api-key
PINECONE_API_KEY=your-pinecone-api-key
```

### 3. Initialize Database
```bash
python -c "from database.session import init_db; init_db()"
```

### 4. Run Backend
```bash
python main.py
# Server: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 5. Install & Run Frontend
```bash
cd ../frontend
npm install
npm run dev
# App: http://localhost:3000
```

## 🧪 Test Agents

```python
# Test FER
from fer.fer import FER
detector = FER(mtcnn=False)
print("FER ready!")

# Test all agents
from agents.interviewer_agent import InterviewerAgent
from agents.integrity_agent import IntegrityAgent
from agents.video_analysis_agent import VideoAnalysisAgent
from agents.audio_analysis_agent import AudioAnalysisAgent
print("All agents ready!")
```

## 📚 API Endpoints

- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login
- `POST /api/interviews/start` - Start interview
- `POST /api/interviews/{id}/submit-answer` - Submit answer
- `GET /api/interviews/{id}/report` - Get report

## 🔍 Troubleshooting

### Import errors?
All LangChain imports use `langchain_classic` or `langchain_core` now.

### FER not working?
Import as `from fer.fer import FER` (not `from fer import FER`)

### Pinecone error?
Package is now `pinecone` v8.0.0 (not `pinecone-client`)

## 📖 Full Details
See `SETUP_SUMMARY.md` for complete information.
