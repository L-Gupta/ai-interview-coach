from fastapi import HTTPException
from .end_models import SummaryResponse
from .end_services import (
    gen_expression_report,
    gen_tone_report,
    validate_exp,
    calc_job_fit,
    calc_acc,
    summarize_validation,
    gen_soft_skills_and_suggestions
)
from .end_utils import (
    compile_pdf_report, 
    save_summary_data, 
    load_summary_data, 
    load_conv_history
)

"""Orchestrates the full exit process and returns final summary."""
async def finalize_interview(resume_id: str, role: str) -> SummaryResponse:
    # Load conversation history from file
    conversation_history = await load_conv_history(resume_id)

    # 1. Generate individual reports
    expression_report = await gen_expression_report(resume_id)
    tone_report = await gen_tone_report(resume_id)
    accuracy_scores = await calc_acc(conversation_history)
    validation_results = await validate_exp(resume_id, conversation_history)
    validation_summary = await summarize_validation(validation_results)
    job_fit = await calc_job_fit(resume_id, role, conversation_history)

    # 2. Integrity extraction
    integrity = {
        "distractions": [],
        "unfair_assistance": False
    }
    for q, data in expression_report.get("raw_data", {}).items():
        if data.get("distractions", 0) > 0:
            integrity["distractions"].append(f"{q}: {data['distractions']} distractions")
        if data.get("multi person", False) or data.get("multi_person_flag", False):
            integrity["unfair_assistance"] = True

    # 3. Generate soft skills & suggestions
    softskills = await gen_soft_skills_and_suggestions({
        "tone_summary": tone_report.get("tone_summary", ""),
        "expression_summary": expression_report.get("expression_summary", ""),
        "accuracy_score": accuracy_scores.get("overall", 0),
        "job_fit_score": job_fit.get("score", 0),
        "validation_summary": validation_summary,
        "total_distractions": expression_report.get("total_distractions", 0),
        "average_eye_contact": expression_report.get("average_eye_contact", 0)
    })

    # 4. Final merge into summary
    summary_data = {
        "resume_id": resume_id,
        "expression_report": expression_report,
        "tone_report": tone_report,
        "validation": validation_results,
        "validation_summary": validation_summary,
        "job_fit_score": job_fit.get("score", 0),
        "job_fit_comment": job_fit.get("comment", ""),
        "accuracy_scores": accuracy_scores,
        "integrity": integrity,
        "soft_skills": softskills.get("soft_skills", {}),
        "suggestions": softskills.get("suggestions", []),
    }

    # 5. Generate PDF + save summary
    pdf_url = await compile_pdf_report(summary_data)
    summary_data["pdf_url"] = pdf_url
    await save_summary_data(resume_id, summary_data, pdf_url)

    return SummaryResponse(**summary_data)  

"""Fetch saved summary data from DB or storage and return it."""
async def get_summary(resume_id: str) -> SummaryResponse:
    try:
        summary = await load_summary_data(resume_id)
        return SummaryResponse(**summary)
    except Exception as e:
        print(f"[ERROR] Failed to load summary for {resume_id}:", e)
        raise HTTPException(status_code=500, detail="Failed to load summary")
