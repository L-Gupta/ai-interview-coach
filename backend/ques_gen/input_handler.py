from pydantic import BaseModel

class InterviewRequest(BaseModel):
    role: str
    resume_id: str  # used as Pinecone namespace

def extract_inputs(data: dict) -> InterviewRequest:
    return InterviewRequest(**data)
