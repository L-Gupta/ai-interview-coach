from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os, json
from pathlib import Path

REPORTS_DIR = Path("end/reports") 

"""Generate a PDF report from summary data and return its file path."""
async def compile_pdf_report(summary_data: dict) -> str:
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    file_path = os.path.join(REPORTS_DIR, f"{summary_data['resume_id']}.pdf")

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    y = height - 50

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(200, y, "Interview Summary Report")
    y -= 40

    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Resume ID: {summary_data['resume_id']}")
    y -= 30

    # Emotion Report
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Emotion & Tone Analysis")
    y -= 20
    c.setFont("Helvetica", 12)
    emotion = summary_data.get("emotion_report", {})
    c.drawString(60, y, f"Tone Summary: {emotion.get('tone_summary', 'N/A')}")
    y -= 20
    c.drawString(60, y, f"Expression Summary: {emotion.get('expression_summary', 'N/A')}")
    y -= 40

    # Experience Validation
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Experience Validation")
    y -= 20
    c.setFont("Helvetica", 12)
    validation = summary_data.get("validation", {})
    for q, result in validation.items():
        c.drawString(60, y, f"{q}: {result}")
        y -= 20
        if y < 100:
            c.showPage()
            y = height - 50

    # Job-Fit Score
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Job-Fit Score")
    y -= 20
    c.setFont("Helvetica", 12)
    c.drawString(60, y, f"{summary_data.get('job_fit_score', 0)}%")
    y -= 40

    # Accuracy Scores
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Accuracy Scores")
    y -= 20
    c.setFont("Helvetica", 12)
    accuracy = summary_data.get("accuracy_scores", {})
    for q, score in accuracy.items():
        c.drawString(60, y, f"{q}: {score}%")
        y -= 20
        if y < 100:
            c.showPage()
            y = height - 50

    c.showPage()
    c.save()

    # Return path or URL depending on setup
    return f"/{REPORTS_DIR}/{summary_data['resume_id']}.pdf"

"""Save summary JSON and PDF reference to the same reports directory."""
async def save_summary_data(resume_id: str, summary_data: dict, pdf_url: str):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    summary_data["pdf_url"] = pdf_url

    safe_id = resume_id.replace(" ", "_")
    json_path = REPORTS_DIR / resume_id /f"{safe_id}.json"

    print(f"[DEBUG] Saving summary data to: {json_path}")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=4)

    return str(json_path)

"""Load summary JSON from the reports directory for the given resume_id."""
async def load_summary_data(resume_id: str) -> dict:
    safe_id = resume_id.replace(" ", "_")
    json_path = REPORTS_DIR / resume_id /f"{safe_id}.json"

    print(f"[DEBUG] Loading summary data from: {json_path}")
    if not json_path.exists():
        print("[DEBUG] No summary file found.")
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

"""
Loads the conversation history stored in the conv_history.json file in the resume_id folder
    -resume_id: ID of the resume (used for folder name)
"""
async def load_conv_history(resume_id: str)->str:
    json_path = REPORTS_DIR / resume_id / "conv_history.json"
    if not json_path.exists():
        return ""

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure it's a dictionary {question:answer}
    if isinstance(data, dict):
        lines = []
        for idx, (q, a) in enumerate(data.items(), start=1):
            lines.append(f"question{idx}: {q}")
            lines.append(f"answer{idx}: {a}")
            lines.append("")  # blank line between Q&A
        conversation = "\n".join(lines)
        return conversation
    return ""