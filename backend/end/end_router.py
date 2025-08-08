from fastapi import APIRouter, Request, HTTPException
from .end_controller import finalize_interview, get_summary
from .end_models import SummaryResponse
from pydantic import BaseModel

router = APIRouter(tags=["End interview"])

class ExitRequest(BaseModel):
    role: str

"""Finalizes the interview session, generates report data, and returns summary."""
@router.post("/interview/exit/{resume_id}", response_model=SummaryResponse)
async def exit_interview(resume_id: str, payload: ExitRequest):
    try:
        summary = await finalize_interview(resume_id, payload.role)
        return summary
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation history not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""Returns the stored summary report for a given resume_id."""
@router.get("/interview/summary/{resume_id}", response_model=SummaryResponse)
async def get_interview_summary(resume_id: str):
    return await get_summary(resume_id)
