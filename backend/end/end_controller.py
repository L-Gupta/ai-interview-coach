from .end_services import gen_emotion_report, validate_exp, calc_job_fit, calc_acc
from .end_utils import compile_pdf_report, save_summary_data, load_summary_data, load_conv_history
from .models_end import SummaryResponse

"""Orchestrates the full exit process and returns final summary."""
async def finalize_interview(resume_id: str,  role: str) -> SummaryResponse:
    # Loads the conversation history for the resume_id as a single string
    conversation_history = await load_conv_history(resume_id)

    # 1. Generate emotion report
    emotion_report = await gen_emotion_report(resume_id)

    # 2. Returns a dictionary of key as questions and values as response from gemini 
    validation_results = await validate_exp(resume_id, conversation_history)

    # 3. Calculates the percentage of how fit the candidate is for the given role based on their answers and resume
    job_fit_score = await calc_job_fit(resume_id, role, conversation_history)

    # 4. Calculates accuracy score by passing the conversation history to gemini and returns a dictionary
    accuracy_scores = await calc_acc(conversation_history)

    # 5. Compile PDF + summary JSON
    summary_data = {
        "resume_id": resume_id,
        "emotion_report": emotion_report,
        "validation": validation_results,
        "job_fit_score": job_fit_score,
        "accuracy_scores": accuracy_scores,
    }

    pdf_url = await compile_pdf_report(summary_data)
    summary_data["pdf_url"] = pdf_url
    await save_summary_data(resume_id, summary_data, pdf_url)

    return SummaryResponse(**summary_data)

"""Fetch saved summary data from DB or storage and return it."""
async def get_summary(resume_id: str) -> SummaryResponse:
    summary_data = await load_summary_data(resume_id)
    if not summary_data:
        # Return empty placeholder if no summary yet
        return SummaryResponse(
            resume_id=resume_id,
            emotion_report={},
            validation={},
            job_fit_score=0,
            accuracy_scores={},
            pdf_url=""
        )
    return SummaryResponse(**summary_data)