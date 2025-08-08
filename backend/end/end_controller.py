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
import traceback

async def finalize_interview(resume_id: str, role: str) -> SummaryResponse:
    print(f"[DEBUG] Starting finalize_interview for resume_id={resume_id}, role={role}")
    try:
        conversation_history = await load_conv_history(resume_id)
        print("[DEBUG] Loaded conversation history")

        expression_report = await gen_expression_report(resume_id)
        print("[DEBUG] Generated expression report")

        tone_report = await gen_tone_report(resume_id)
        print("[DEBUG] Generated tone report")

        accuracy_scores = await calc_acc(conversation_history)
        print("[DEBUG] Calculated accuracy scores")

        validation_results = await validate_exp(resume_id, conversation_history)
        print("[DEBUG] Completed experience validation")

        validation_summary = await summarize_validation(validation_results)
        print("[DEBUG] Summarized validation results")

        job_fit = await calc_job_fit(resume_id, role, conversation_history)
        print("[DEBUG] Calculated job fit")

        integrity = {
            "distractions": [],
            "unfair_assistance": False
        }
        if isinstance(expression_report, dict):
            for q, data in expression_report.get("raw_data", {}).items():
                if data.get("distractions", 0) > 0:
                    integrity["distractions"].append(f"{q}: {data['distractions']} distractions")
                if data.get("multi person", False) or data.get("multi_person_flag", False):
                    integrity["unfair_assistance"] = True

        softskills = await gen_soft_skills_and_suggestions({
            "tone_summary": tone_report.get("tone_summary", "") if isinstance(tone_report, dict) else "",
            "expression_summary": expression_report.get("expression_summary", "") if isinstance(expression_report, dict) else "",
            "accuracy_score": accuracy_scores.get("overall", 0) if isinstance(accuracy_scores, dict) else 0,
            "job_fit_score": job_fit.get("score", 0) if isinstance(job_fit, dict) else 0,
            "validation_summary": validation_summary,
            "total_distractions": expression_report.get("total_distractions", 0) if isinstance(expression_report, dict) else 0,
            "average_eye_contact": expression_report.get("average_eye_contact", 0) if isinstance(expression_report, dict) else 0
        })
        print("[DEBUG] Generated soft skill suggestions")

        if not isinstance(expression_report, dict):
            print("[ERROR] expression_report is not a dict. Got:", type(expression_report))
            expression_report = {
                "expression_summary": "Error generating expression report.",
                "dominant_emotions": [],
                "average_eye_contact": 0,
                "total_distractions": 0,
                "total_face_absence": 0,
                "multi_person_flag": False,
                "raw_data": {}
            }

        if not isinstance(tone_report, dict):
            print("[ERROR] tone_report is not a dict. Got:", type(tone_report))
            tone_report = {
                "tone_summary": "Error generating tone report.",
                "dominant_tones_per_question": {},
                "raw_data": {}
            }

        if not isinstance(accuracy_scores, dict):
            print("[ERROR] accuracy_scores is not a dict. Got:", type(accuracy_scores))
            accuracy_scores = {}

        if not isinstance(validation_results, dict):
            print("[ERROR] validation_results is not a dict. Got:", type(validation_results))
            validation_results = {}

        if not isinstance(validation_summary, dict):
            print("[ERROR] validation_summary is not a dict. Got:", type(validation_summary))
            validation_summary = {}

        if not isinstance(job_fit, dict):
            job_fit = {}

        if not isinstance(softskills, dict):
            softskills = {
                "soft_skills": {},
                "suggestions": []
            }

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

        pdf_url = await compile_pdf_report(summary_data)
        summary_data["pdf_url"] = pdf_url
        await save_summary_data(resume_id, summary_data, pdf_url)

        print("[DEBUG] Final summary saved and PDF generated.")
        return SummaryResponse(**summary_data)

    except Exception as e:
        print("[CRITICAL] Exception in finalize_interview:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Interview finalization failed.")

  

"""Fetch saved summary data from DB or storage and return it."""
async def get_summary(resume_id: str) -> SummaryResponse:
    try:
        summary = await load_summary_data(resume_id)
        return SummaryResponse(**summary)
    except Exception as e:
        print(f"[ERROR] Failed to load summary for {resume_id}:", e)
        raise HTTPException(status_code=500, detail="Failed to load summary")
