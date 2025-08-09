import os, json
from pathlib import Path
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

REPORTS_DIR = Path("end/reports") 

"""Loads summary.json from disk."""
async def load_summary_data(resume_id: str) -> dict:
    try:
        file_path = REPORTS_DIR / resume_id / "summary.json"
        if not file_path.exists():
            raise FileNotFoundError("summary.json not found")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("[ERROR] Failed to load summary.json:", e)
        return {}

"""Loads conversation history file from disk."""
async def load_conv_history(resume_id: str) -> str:
    try:
        file_path = REPORTS_DIR / resume_id / "conv_history.json"
        if not file_path.exists():
            raise FileNotFoundError("conversation_history.json not found")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert to plain Q&A if list of dicts
        if isinstance(data, list):
            return "\n\n".join([f"Q: {x['question']}\nA: {x['answer']}" for x in data])
        elif isinstance(data, dict):
            return "\n\n".join([f"Q: {k}\nA: {v}" for k, v in data.items()])
        elif isinstance(data, str):
            return data
        else:
            return ""

    except Exception as e:
        print("[ERROR] Failed to load conversation_history:", e)
        return ""

"""Writes summary dictionary to disk."""
async def save_summary_data(resume_id: str, summary_data: dict, pdf_url: str = "") -> None:
    try:
        folder = REPORTS_DIR / resume_id
        os.makedirs(folder, exist_ok=True)

        summary_data["pdf_url"] = pdf_url
        save_path = folder / "summary.json"

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)
    except Exception as e:
        print("[ERROR] Failed to save summary.json:", e)

"""Compiles a PDF report from the final summary dictionary."""
async def compile_pdf_report(summary_data: dict) -> str:
    try:
        resume_id = summary_data.get("resume_id") or "unknown"
        save_dir = REPORTS_DIR / resume_id
        os.makedirs(save_dir, exist_ok=True)
        filepath = save_dir / "summary.pdf"

        c = canvas.Canvas(str(filepath), pagesize=A4)
        width, height = A4
        y = height - 50

        def draw_heading(text, size=16, offset=30):
            nonlocal y
            c.setFont("Helvetica-Bold", size)
            c.drawString(50, y, text)
            y -= offset

        def draw_text(label, value, size=12, indent=10, line_gap=20):
            nonlocal y
            c.setFont("Helvetica-Bold", size)
            c.drawString(50 + indent, y, f"{label}:")
            c.setFont("Helvetica", size)
            c.drawString(130 + indent, y, str(value))
            y -= line_gap

        def draw_multiline_text(label, lines, size=12, indent=10, line_gap=16):
            nonlocal y
            c.setFont("Helvetica-Bold", size)
            c.drawString(50 + indent, y, f"{label}:")
            y -= line_gap
            c.setFont("Helvetica", size)
            for line in lines:
                c.drawString(70 + indent, y, f"- {line}")
                y -= line_gap

        # Title
        draw_heading("AI Interview Summary Report", size=18, offset=30)
        draw_text("Generated on", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        # --- Section 1: Expression & Tone
        draw_heading("Expression & Tone Analysis")
        draw_text("Tone Summary", summary_data.get("tone_report", {}).get("tone_summary", "N/A"))
        draw_text("Expression Summary", summary_data.get("expression_report", {}).get("expression_summary", "N/A"))

        # --- Section 2: Accuracy & Validation
        draw_heading("Accuracy & Validation")
        acc = summary_data.get("accuracy_scores", {}) or {}
        draw_text("Accuracy Score", f"{acc.get('overall', 'N/A')}%")
        draw_text("Comment", acc.get("comment", ""))

        val = summary_data.get("validation", {}) or summary_data.get("validation_summary", {}) or {}
        draw_text("Matches", val.get("match_count", 0), indent=20)
        draw_text("Exaggerated", val.get("exaggerated_count", 0), indent=20)
        draw_text("Vague", val.get("vague_count", 0), indent=20)

        # --- Section 3: Job Fit & Soft Skills
        draw_heading("Job Fit & Soft Skills")
        draw_text("Job Fit Score", f"{summary_data.get('job_fit_score', 'N/A')}%")
        draw_text("Comment", summary_data.get("job_fit_comment", ""))

        soft = summary_data.get("soft_skills", {}) or {}
        if isinstance(soft, dict):
            for skill, level in soft.items():
                draw_text(skill.capitalize(), level, indent=10)

        # --- Section 4: Suggestions
        suggestions = summary_data.get("suggestions", [])
        if isinstance(suggestions, list) and suggestions:
            draw_heading("Suggestions")
            draw_multiline_text("Tips", suggestions)

        # Footer
        y = 50
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, y, "This report was auto-generated by the AI Interview Coach system.")
        c.save()

        return f"/end/reports/{resume_id}/summary.pdf"

    except Exception as e:
        print("[ERROR] Failed to compile PDF:", e)
        return ""
