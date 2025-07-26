"""
FastAPI router for generating follow-up interview questions.

Expects a POST request with:
{
    "role": "Frontend Developer",
    "resume_id": "sample_resume",
    "history": [
        {"question": "Tell me about your experience on Project X", "answer": "I worked on..."},
        {"question": "What tech stack did you use?", "answer": "React, Node.js"}
    ]
}

Returns:
{
    "question": "What were some challenges you faced during Project X and how did you overcome them?",
    "namespace": "sample_resume"
}
"""

from fastapi import APIRouter, Request, HTTPException
from ques_gen.ques_next import generate_followup_question

router = APIRouter()

@router.post("/generate-followup")
async def generate_followup_api(request: Request):
    """
    API endpoint to generate a follow-up interview question.
    """
    try:
        data = await request.json()

        role = data.get("role")
        resume_id = data.get("resume_id")
        history = data.get("history", [])

        if not role or not resume_id:
            raise HTTPException(status_code=400, detail="Missing role or resume_id")

        if not isinstance(history, list):
            raise HTTPException(status_code=400, detail="History must be a list of Q&A objects")
        
         # Optional: Validate each history item
        for item in history:
            if "question" not in item or "answer" not in item:
                raise HTTPException(status_code=400, detail="Each history item must have 'question' and 'answer'")
            
        print(f"📥 Received follow-up request: role={role}, resume_id={resume_id}, history_len={len(history)}")

        # Generate follow-up question
        question = generate_followup_question(role=role, namespace=resume_id, history=history)

        print(f"✅ Generated follow-up question for {resume_id}: {question}")

        return {
            "question": question,
            "namespace": resume_id
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ Error in follow-up generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Local test without running FastAPI server
    from ques_next import generate_followup_question

    print("🚀 Testing follow-up question generation...\n")

    # 🔹 Sample input
    role = "Frontend Developer"
    resume_id = "sample_resume"
    history = [
        {"question": "Tell me about your experience on Breeze 2024", "answer": "I led the web development team and handled deployment."},
        {"question": "What tech stack did you use?", "answer": "Next.js, TailwindCSS, Firebase, and Stripe API."}
    ]

    try:
        # 🔍 Call the generator directly
        question = generate_followup_question(role=role, namespace=resume_id, history=history, top_k=5)

        print("🎯 Final Output")
        print("---------------------------")
        print(f"🧠 Follow-up Question: {question}")
        print("---------------------------")

    except Exception as e:
        print(f"❌ Error during test: {e}")
