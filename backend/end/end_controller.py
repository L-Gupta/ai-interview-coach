from .end_services import gen_emotion_report,validate_exp,calc_job_fit,calc_acc
from .end_utils import compile_pdf_report, save_summary_data, load_summary_data
from .models_end import SummaryResponse

"""Orchestrates the full exit process and returns final summary."""
async def finalize_interview(resume_id: str, conversation_history: list, role: str) -> SummaryResponse:
    # 1. Generate emotion report
    emotion_report = await gen_emotion_report(resume_id)

    # 2. Experience validation
    validation_results = await validate_exp(resume_id, conversation_history)

    # 3. Job-fit score
    job_fit_score = await calc_job_fit(resume_id, role, conversation_history)

    # 4. Accuracy scores
    accuracy_scores = await calc_acc(resume_id, conversation_history)

    # 5. Compile PDF + summary JSON
    summary_data = {
        "resume_id": resume_id,
        "emotion_report": emotion_report,
        "validation": validation_results,
        "job_fit_score": job_fit_score,
        "accuracy_scores": accuracy_scores,
    }

    pdf_url = await compile_pdf_report(summary_data)
    await save_summary_data(resume_id, summary_data, pdf_url)

    return SummaryResponse(**summary_data, pdf_url=pdf_url)

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