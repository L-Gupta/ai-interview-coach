# 🧠 AI Interview Coach

An AI-powered virtual interview platform that analyzes your responses — both verbal and non-verbal — to help you improve with personalized feedback, emotion tracking, and a final PDF report.

---

## 🚀 Features

- 🎤 **Voice Transcription & Tone Analysis** (real-time)
- 🎥 **Facial Emotion Detection** with eye contact, distraction, and multi-person monitoring
- 💬 **AI-Generated Interview Questions** based on resume and job role
- ✅ **Experience Validation** using Gemini + resume chunks
- 📊 **Final Summary Report** with accuracy, tone, emotion, integrity, and job fit
- 📄 **Auto-generated PDF Report** with structured feedback and recommendations

---

## 🛠️ Tech Stack

**Frontend**  
- React.js  
- Tailwind / CSS Modules  
- WebRTC (audio + video streams)  
- Axios for API communication

**Backend**  
- FastAPI  
- LangChain + Gemini API  
- Pinecone Vector DB  
- ReportLab for PDF generation

**Others**  
- GitHub for version control  
- Vercel / Render / Firebase for deployment (planned)

---

## 🧪 How It Works

1. **Upload your resume**
2. **Start mock interview** — questions are AI-generated from your resume
3. **Speak and respond** — audio & video are analyzed in real-time
4. **Exit interview** — triggers backend to analyze tone, validate answers, assess job fit
5. **Receive final summary** — JSON + downloadable PDF with full feedback

---

## 📁 Folder Structure

