from fastapi import HTTPException
from .end_models import SummaryResponse
from .end_services import (
    gen_expression_report,
    gen_tone_report,
    calc_acc,
    validate_exp,
    summarize_validation,
    calc_job_fit,
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
        # ---- Conversation history (safe)
        try:
            conversation_history = await load_conv_history(resume_id)
            print("[DEBUG] Loaded conversation history")
        except Exception as e:
            print("[ERROR] load_conv_history failed:", e)
            conversation_history = ""

        # ---- Expression report (safe)
        try:
            expression_report = await gen_expression_report(resume_id)
            print("[DEBUG] Generated expression report")
        except Exception as e:
            print("[ERROR] gen_expression_report failed:", e)
            expression_report = {
                "expression_summary": "Error generating expression report.",
                "dominant_emotions": [],
                "average_eye_contact": 0,
                "total_distractions": 0,
                "total_face_absence": 0,
                "multi_person_flag": False,
                "raw_data": {}
            }

        # ---- Tone report (safe)
        try:
            tone_report = await gen_tone_report(resume_id)
            print("[DEBUG] Generated tone report")
        except Exception as e:
            print("[ERROR] gen_tone_report failed:", e)
            tone_report = {
                "tone_summary": "Error generating tone report.",
                "dominant_tones_per_question": {},
                "raw_data": {}
            }

        # ---- Accuracy (safe)
        try:
            accuracy_scores = await calc_acc(conversation_history)
            print("[DEBUG] Calculated accuracy scores")
        except Exception as e:
            print("[ERROR] calc_acc failed:", e)
            accuracy_scores = {"overall": 0, "comment": "Accuracy calculation failed."}

        # ---- Validation (safe)
        try:
            validation_results = await validate_exp(resume_id, conversation_history)
            print("[DEBUG] Completed experience validation")
        except Exception as e:
            print("[ERROR] validate_exp failed:", e)
            validation_results = {}

        # ---- Validation summary (safe)
        try:
            validation_summary = await summarize_validation(validation_results)
            print("[DEBUG] Summarized validation results")
        except Exception as e:
            print("[ERROR] summarize_validation failed:", e)
            validation_summary = {
                "match_count": 0,
                "exaggerated_count": 0,
                "mismatch_count": 0,
                "vague_count": 0
            }

        # ---- Job fit (safe)
        try:
            job_fit = await calc_job_fit(resume_id, role, conversation_history)
            print("[DEBUG] Calculated job fit")
        except Exception as e:
            print("[ERROR] calc_job_fit failed:", e)
            job_fit = {"score": 0, "comment": "Job fit calculation failed."}

        # ---- Integrity check (safe)
        integrity = {
            "distractions": [],
            "unfair_assistance": False
        }
        try:
            if isinstance(expression_report, dict):
                for q, data in expression_report.get("raw_data", {}).items():
                    if data.get("distractions", 0) > 0:
                        integrity["distractions"].append(f"{q}: {data['distractions']} distractions")
                    if data.get("multi person", False) or data.get("multi_person_flag", False):
                        integrity["unfair_assistance"] = True
        except Exception as e:
            print("[WARN] Integrity aggregation skipped due to error:", e)

        # ---- Soft skills (safe)
        try:
            softskills_raw = await gen_soft_skills_and_suggestions({
                "tone_summary": tone_report.get("tone_summary", "") if isinstance(tone_report, dict) else "",
                "expression_summary": expression_report.get("expression_summary", "") if isinstance(expression_report, dict) else "",
                "accuracy_score": accuracy_scores.get("overall", 0) if isinstance(accuracy_scores, dict) else 0,
                "job_fit_score": job_fit.get("score", 0) if isinstance(job_fit, dict) else 0,
                "validation_summary": validation_summary,
                "total_distractions": expression_report.get("total_distractions", 0) if isinstance(expression_report, dict) else 0,
                "average_eye_contact": expression_report.get("average_eye_contact", 0) if isinstance(expression_report, dict) else 0
            })
            print("[DEBUG] Generated soft skill suggestions")
        except Exception as e:
            print("[ERROR] gen_soft_skills_and_suggestions failed:", e)
            softskills_raw = {"soft_skills": {}, "suggestions": []}

        # Normalize soft_skills mapping + suggestions list
        soft_skills_map = {}
        suggestions_list = []
        if isinstance(softskills_raw, dict):
            # Some implementations return {"soft_skills": {...}, "suggestions": [...]}
            soft_skills_map = softskills_raw.get("soft_skills", {}) if isinstance(softskills_raw.get("soft_skills", {}), dict) else {}
            suggestions_list = softskills_raw.get("suggestions", []) if isinstance(softskills_raw.get("suggestions", []), list) else []
            # Or they may return a flat mapping; handle that gracefully:
            if not soft_skills_map and all(isinstance(v, (int, float, str)) for v in softskills_raw.values() or []):
                soft_skills_map = softskills_raw

        # ---- Final summary object (keys match SummaryResponse model)
        summary_data = {
            "resume_id": resume_id,
            "expression_report": {
                "expression_summary": expression_report.get("expression_summary", ""),
                "dominant_emotions": expression_report.get("dominant_emotions", []),
                "average_eye_contact": expression_report.get("average_eye_contact", 0),
                "total_distractions": expression_report.get("total_distractions", 0),
                "total_face_absence": expression_report.get("total_face_absence", 0),
                "multi_person_flag": expression_report.get("multi_person_flag", False),
                "raw_data": expression_report.get("raw_data", {})
            },
            "tone_report": {
                "tone_summary": tone_report.get("tone_summary", ""),
                "dominant_tones_per_question": tone_report.get("dominant_tones_per_question", {}),
                "raw_data": tone_report.get("raw_data", {})
            },

            # Ensure 'validation' and 'validation_summary' are set
            "validation": validation_summary if validation_summary else {},  # Use empty dict if missing
            "validation_summary": validation_summary if validation_summary else {},  # Ensure this is set too

            "job_fit_score": job_fit.get("score", 0),
            "job_fit_comment": job_fit.get("comment", ""),
            "suggestions": suggestions_list,
            "accuracy_scores": accuracy_scores,
            "soft_skills": soft_skills_map,
            "integrity": integrity if integrity else {},  # Default to empty dict if not populated
            "pdf_url": ""
        }

        # ---- PDF & save (safe)
        pdf_url = ""
        try:
            # pass resume_id so the util can place file correctly even if summary_data is incomplete
            pdf_url = await compile_pdf_report(summary_data)
        except Exception as e:
            print("[ERROR] compile_pdf_report failed:", e)
            pdf_url = ""
        summary_data["pdf_url"] = pdf_url
        try:
            await save_summary_data(resume_id, summary_data, pdf_url)
        except Exception as e:
            print("[ERROR] save_summary_data failed:", e)

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
