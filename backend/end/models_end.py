from pydantic import BaseModel
from typing import Dict

class SummaryResponse(BaseModel):
    resume_id: str
    emotion_report: Dict
    validation: Dict
    job_fit_score: int
    accuracy_scores: Dict
    pdf_url: str
