from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import json

REPORTS_DIR = "reports"

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
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    # Attach PDF URL before saving
    summary_data["pdf_url"] = pdf_url

    json_path = os.path.join(REPORTS_DIR, f"{resume_id}.json")
    with open(json_path, "w") as f:
        json.dump(summary_data, f, indent=4)

    return json_path

"""Load summary JSON from the reports directory for the given resume_id."""
async def load_summary_data(resume_id: str) -> dict:
    json_path = os.path.join(REPORTS_DIR, f"{resume_id}.json")
    if not os.path.exists(json_path):
        return None

    with open(json_path, "r") as f:
        return json.load(f)
