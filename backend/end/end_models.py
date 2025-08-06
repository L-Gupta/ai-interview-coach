from pydantic import BaseModel
from typing import Dict, Optional, List

class SummaryResponse(BaseModel):
    resume_id: str
    expression_report: Dict
    tone_report: Dict
    validation: Dict
    validation_summary: Dict
    job_fit_score: int
    job_fit_comment: Optional[str] = ""
    accuracy_scores: Dict
    integrity: Dict
    soft_skills: Dict
    suggestions: List[str]
    pdf_url: str
