from fastapi import APIRouter, Request
from .end_controller import finalize_interview, get_summary
from .models_end import SummaryResponse

router = APIRouter(tags=["Exit"])

@router.post("/interview/exit/{resume_id}", response_model=SummaryResponse)
async def exit_interview(resume_id: str, request: Request):
    """Finalizes the interview session, generates report data, and returns summary."""
    body = await request.json()
    conversation_history = body.get("conversation_history", [])
    role = body.get("role", "Unknown Role")
    return await finalize_interview(resume_id, conversation_history, role)

@router.get("/interview/summary/{resume_id}", response_model=SummaryResponse)
async def get_interview_summary(resume_id: str):
    """Returns the stored summary report for a given resume_id."""
    return await get_summary(resume_id)