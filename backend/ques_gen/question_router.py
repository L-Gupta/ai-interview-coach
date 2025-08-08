from fastapi import APIRouter, Request, HTTPException
from .question_controller import generate_followup

router = APIRouter(tags=["Question Generation"])

@router.post("/generate-followup")
async def generate_followup_question_api(request: Request):
    try:
        # Extracting data
        data = await request.json()
        role = data.get("role")
        resume_id = data.get("resume_id")

        # Checking if either role or resume_id are missing from the frontend post
        if not role or not resume_id:
            raise HTTPException(status_code=400, detail="Missing role or resume_id")

        # Calling the helper function and returning the followup question
        question = generate_followup(role=role, resume_id=resume_id)
        return {"question": question, "namespace": resume_id}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating follow-up question: {e}")
