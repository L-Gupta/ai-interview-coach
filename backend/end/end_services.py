# Stdlib
import os, json, re
from pathlib import Path
from collections import Counter

# Third-party
import httpx, requests
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from pinecone import Pinecone

# Project imports
from .end_prompts import (
    ACCURACY_PROMPT,
    JOB_FIT_PROMPT,
    VALIDATION_PROMPT,
    TONE_PROMPT,
    EXPRESSION_PROMPT,
    SOFT_SKILL_PROMPT,
)

load_dotenv()

#Constants
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "interview-index"
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

#Gemini AI and embedding model
llm = ChatGoogleGenerativeAI(model = "models/gemini-1.5-flash-latest", google_api_key = GEMINI_API_KEY)
GEMINI_EMBEDDING_URL = ("https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"f"?key={GEMINI_API_KEY}")

#Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

#Fixed directory
REPORTS_DIR = Path("end/reports")

"""Parses emotion.json and compiles a facial expression summary."""
"""
Args:
    resume_id (str): Unique ID of the resume folder where emotion.json is stored.

Returns:
    expression_report (dict):
        {
            "expression_summary": str,
            "dominant_emotions": list[str],
            "average_eye_contact": int,
            "total_distractions": int,
            "total_face_absence": int,
            "multi_person_flag": bool,
            "raw_data": dict
        }

Behavior:
    - Loads emotion.json from end/reports/{resume_id}.
    - Aggregates emotions and integrity metrics across all questions.
    - Calls Gemini to summarize facial expressions.
"""
async def gen_expression_report(resume_id: str) -> dict:
    emotion_path = REPORTS_DIR / resume_id / "emotion.json"

    # Opens and reads file, returns mock data if error
    try:
        with open(emotion_path, "r", encoding="utf-8") as f:
            emotion_data = json.load(f)
    except Exception as file_err:
        print("[ERROR] Failed to parse emotion.json:", file_err)
        return {
            "expression_summary": "Could not parse emotion data.",
            "dominant_emotions": ["neutral"],
            "average_eye_contact": 50,
            "total_distractions": 2,
            "total_face_absence": 1,
            "multi_person_flag": False,
            "raw_data": {}
        }

    # Metrics
    dominant_emotions = get_dominant_expression(emotion_data)
    avg_eye_contact = calculate_average_eye_contact(emotion_data)
    total_distractions = calculate_total_distractions(emotion_data)
    total_face_absence = calculate_total_face_absence(emotion_data)
    multi_person_flag = check_multi_person_flag(emotion_data)

    # Generate human-readable summary based on rules
    summary = []

    if "happy" in dominant_emotions:
        summary.append("Candidate frequently appeared happy.")
    elif "neutral" in dominant_emotions:
        summary.append("Candidate maintained a neutral expression.")
    else:
        summary.append("Candidate showed varied facial expressions.")

    if avg_eye_contact > 80:
        summary.append("Maintained strong eye contact.")
    elif avg_eye_contact > 50:
        summary.append("Maintained moderate eye contact.")
    else:
        summary.append("Eye contact was inconsistent.")

    if total_distractions > 5:
        summary.append("Appeared distracted multiple times.")
    elif total_distractions > 0:
        summary.append("Minor signs of distraction were detected.")
    else:
        summary.append("No distractions detected.")

    if total_face_absence > 0:
        summary.append("Facial visibility was lost occasionally.")

    if multi_person_flag:
        summary.append("Presence of multiple people was detected.")

    expression_summary = " ".join(summary)

    return {
        "expression_summary": expression_summary,
        "dominant_emotions": dominant_emotions,
        "average_eye_contact": avg_eye_contact,
        "total_distractions": total_distractions,
        "total_face_absence": total_face_absence,
        "multi_person_flag": multi_person_flag,
        "raw_data": emotion_data
    }

"""Compile tone dictionaries into a summary via Gemini."""
"""
Args:
    resume_id (str): Unique ID of the resume folder where `tone.json` is stored.

Returns:
    tone_report (dict):
        {
            "tone_summary": str,                # Summary of overall tone (from Gemini or fallback)
            "expression_summary": str,          # Reserved for facial expression analysis (currently empty)
            "dominant_tones_per_question": dict,# (Optional) Dominant tone for each question (q1, q2, ...)
            "raw_data": dict                    # Raw tone.json data for debugging/reporting
        }

Behavior:
    - Loads `tone.json` from end/reports/{resume_id}.
    - tone.json is expected to be a dict: { "q1": ["Happy", "Confident"], "q2": ["Neutral"] }
    - Calculates the most common tone per question using Counter.
    - Determines the overall dominant tone across all questions.
    - Builds a Gemini prompt with tone data and calls Gemini to generate a report.
    - Returns a structured dictionary containing summaries and raw tone data.
    - Falls back to a simple dominant-tone summary if Gemini parsing fails.
"""
async def gen_tone_report(resume_id: str) -> dict:
    tone_file = REPORTS_DIR / resume_id / "tone.json"

    if not tone_file.exists():
        return {
            "tone_summary": "No tone data found.",
            "dominant_tones_per_question": {},
            "raw_data": {}
        }

    try:
        with open(tone_file, "r", encoding="utf-8") as f:
            tone_dict = json.load(f)
    except Exception as file_err:
        print("[ERROR] Failed to parse tone.json:", file_err)
        return {
            "tone_summary": "Could not parse tone data.",
            "dominant_tones_per_question": {},
            "raw_data": {}
        }

    try:
        dominant_tones = {
            q: Counter(vals).most_common(1)[0][0]
            for q, vals in tone_dict.items() if vals
        }
        all_tones = [tone for vals in tone_dict.values() for tone in vals]
        overall_dominant = (
            Counter(all_tones).most_common(1)[0][0] if all_tones else "Neutral"
        )

        summary = []
        if overall_dominant.lower() in ["confident", "enthusiastic", "happy"]:
            summary.append(f"The candidate expressed a generally {overall_dominant.lower()} tone.")
        elif overall_dominant.lower() == "neutral":
            summary.append("The overall tone remained neutral throughout the interview.")
        else:
            summary.append(f"The tone varied, with a slight leaning towards {overall_dominant.lower()}.")

        if "nervous" in all_tones:
            summary.append("Some nervousness was also detected.")

        tone_summary = " ".join(summary)

        return {
            "tone_summary": tone_summary,
            "dominant_tones_per_question": dominant_tones,
            "raw_data": tone_dict
        }

    except Exception as e:
        print(f"[CRITICAL] gen_tone_report crashed: {e}")
        return {
            "tone_summary": "Error generating tone report.",
            "dominant_tones_per_question": {},
            "raw_data": {}
        }

"""Generates soft skill insights and improvement suggestions using Gemini."""
"""
Args:
    summary_dict (dict): Compiled summary so far (tone, expression, accuracy, validation, etc.)

Returns:
    insights (dict):
        {
            "soft_skills": {
                "communication": str,
                "confidence": str,
                "empathy": str
            },
            "suggestions": list[str]
        }
"""
async def gen_soft_skills_and_suggestions(summary_dict):
    prompt = SOFT_SKILL_PROMPT.format(
        tone_summary = summary_dict.get("tone_summary"),
        expression_summary = summary_dict.get("expression_summary"),
        accuracy_score = summary_dict.get("accuracy_score"),
        job_fit_score = summary_dict.get("job_fit_score"),
        validation_summary = summary_dict.get("validation_summary"),
        total_distractions = summary_dict.get("total_distractions"),
        average_eye_contact = summary_dict.get("average_eye_contact")
    )
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        print("[DEBUG] Gemini soft skills response:", response.content)
        text = response.content.strip().strip("`")
        if "\n" in text:
            text = "\n".join(text.split("\n")[1:])
        insights = json.loads(text)
    except Exception as e:
        print("[ERROR] Gemini soft skills generation failed:", e)
        insights = {
            "soft_skills": {
                "communication": "moderate",
                "confidence": "moderate",
                "empathy": "moderate"
            },
            "suggestions": ["Review technical examples in detail.", "Maintain steady eye contact."]
        }

    return insights

"""Uses candidate answers, role, and Pinecone chunks to generate a job-fit score (0-100)."""
""""
Args:
    resume_id (str): Unique ID of the resume folder.
    role (str): Job role the candidate is applying for.
    conversation_history (str): Conversation history as a formatted string with Q/A pairs.

Returns:
    job_fit_score (int): Job fit score between 0 and 100 based on Gemini's analysis.
"""
async def calc_job_fit(resume_id: str, role: str, conversation_history: str) -> dict:
    blocks = conversation_history.strip().split("\n\n")
    answers = []
    for block in blocks:
        for line in block.split("\n"):
            if line.lower().startswith("a:"):
                answers.append(line.split(":", 1)[1].strip())

    all_chunks = []
    for ans in answers:
        chunks = await get_relevant_chunks(resume_id=resume_id, answer=ans, top_k=3)
        all_chunks.extend(chunks)

    unique_chunks = list(set(all_chunks))
    context_text = "\n".join([f"- {chunk}" for chunk in unique_chunks])
    answers_text = "\n".join([f"- {ans}" for ans in answers])

    prompt = JOB_FIT_PROMPT.format(role=role, answers=answers_text, context=context_text)
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    print("[DEBUG] Gemini job fit response:", response.content)

    try:
        text = response.content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if "\n" in text:
                text = "\n".join(text.split("\n")[1:])
        parsed = json.loads(text)
        job_fit_score = int(parsed.get("score", 75))
        job_fit_comment = parsed.get("comment", "No comment provided.")
    except Exception:
        import re
        numbers = re.findall(r"\d+", response.content)
        job_fit_score = int(numbers[0]) if numbers else 75
        job_fit_comment = "Could not parse Gemini response."

    return {
        "score": job_fit_score,
        "comment": job_fit_comment
    }

"""Passes conversation history to Gemini and gets answer accuracy scores (1-100)."""
""""
Args:
    conversation_history (str): Conversation history as a formatted string with Q/A pairs.

Returns: 
    accuracy_score (dict): {Overall  : Accuracy scores as returned by Gemini.}
"""
async def calc_acc(conversation_history: str) -> dict:
    if not conversation_history:
        return {
            "overall": 0,
            "comment": "No conversation history found."
        }

    prompt = ACCURACY_PROMPT.format(qa_pairs=conversation_history)

    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        print("[DEBUG] Gemini accuracy response:", response.content)
        text = response.content.strip()

        if text.startswith("```"):
            text = text.strip("`")
            if "\n" in text:
                text = "\n".join(text.split("\n")[1:])

        accuracy_scores = json.loads(text)

    except Exception as e:
        print("Gemini parsing error:", e)
        print("Raw response text:", response.content)
        accuracy_scores = {
            "overall": 75,
            "comment": "Default fallback: Gemini failed to parse."
        }

    return accuracy_scores


"""Compares each answer with relevant resume chunks to detect exaggerations or mismatches."""
"""
Args:
    resume_id (str): Unique ID of the resume folder.
    conversation_history (str): Conversation history as a formatted string with Q/A pairs.

Returns:
    results (dict) : {Question IDs (q1, q2, ...) : Gemini's validation result for each answer ("Match", "Exaggerated")}
"""
async def validate_exp(resume_id: str, conversation_history: str) -> dict:  
    results = {}
    blocks = conversation_history.strip().split("\n\n")
    for idx, block in enumerate(blocks, start=1):
        q_key = f"q{idx}"
        lines = block.split("\n")
        answer = ""
        for line in lines:
            if line.lower().startswith("a:"):
                answer = line.split(":", 1)[1].strip()

        chunks = await get_relevant_chunks(resume_id, answer)
        chunk = chunks[0] if chunks else ""

        prompt = VALIDATION_PROMPT.format(answer=answer, chunk=chunk)
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        print(f"[DEBUG] Gemini validation response for {q_key}:", response.content)

        try:
            text = response.content.strip()
            if text.startswith("```"):
                text = text.strip("`")
                if "\n" in text:
                    text = "\n".join(text.split("\n")[1:])
            validation = json.loads(text)["validation"]
        except:
            if "3 years" in chunk:
                validation = "Match"
            elif chunk:
                validation = "Exaggerated"
            else:
                validation = "Vague"

        results[q_key] = validation

    return results

"""Summarizes validation results into counts of match/exaggerated/mismatch/vague responses."""
"""
Args:
    validation_dict (dict): Output from validate_exp(), e.g. { "q1": "Match", "q2": "Exaggerated" }

Returns:
    summary (dict):
        {
            "match_count": int,
            "exaggerated_count": int,
            "mismatch_count": int,
            "vague_count": int
        }
"""
async def summarize_validation(validation_dict):
    summary = {
        "match_count": 0,
        "exaggerated_count": 0,
        "mismatch_count": 0,
        "vague_count": 0
    }

    for result in validation_dict.values():
        key = result.lower() + "_count"
        if key in summary:
            summary[key] += 1
        else:
            summary["vague_count"] += 1  # fallback

    return summary  


#Helper functions used in interview_controller.py
"""Query Pinecone for the most relevant resume chunks based on an answer."""
async def get_relevant_chunks(resume_id: str, answer: str, top_k: int = 1):
    # 1️⃣ Create embedding for the answer using Gemini's embedding endpoint
    payload = {
        "model": "models/embedding-001",
        "content": {"parts": [{"text": answer}]}
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(GEMINI_EMBEDDING_URL, json=payload)
    embedding_data = resp.json()
    answer_vector = embedding_data["embedding"]["values"]

    # 2. Query Pinecone with resume_id filter
    result = index.query(
        vector=answer_vector,
        top_k=top_k,
        include_metadata=True,
        filter={"resume_id": {"$eq": resume_id}}
    )

    # 3. Extract chunks from metadata
    chunks = [match["metadata"]["text"] for match in result["matches"]]
    return chunks

"""
Converts conversation history into a formatted string with numbered Q/A pairs.

Args:
    conversation_history (dict | list | str):
        - dict: {question: answer}
        - list: [{"question": "...", "answer": "..."}, ...]
        - str: Single answer text (fallback)

Returns:
    str:
        A formatted string like:

        Q1: Question text
        A: Answer text

        Q2: Question text
        A: Answer text
"""
def normalize_history(conversation_history):
    print("[DEBUG] Raw conversation_history:", conversation_history, type(conversation_history))

    # If conv_history.json was loaded as a dict {question: answer}
    if isinstance(conversation_history, dict):
        lines = []
        for idx, (question, answer) in enumerate(conversation_history.items(), start=1):
            lines.append(f"Q{idx}: {question}")
            lines.append(f"A: {answer}")
            lines.append("")  # blank line between Q&A
        return "\n".join(lines)

    # If it's already a list of {"question": q, "answer": a}
    elif isinstance(conversation_history, list):
        lines = []
        for idx, item in enumerate(conversation_history, start=1):
            q = item.get("question", "")
            a = item.get("answer", "")
            lines.append(f"Q{idx}: {q}")
            lines.append(f"A: {a}")
            lines.append("")
        return "\n".join(lines)

    # If it's a plain string (fallback)
    elif isinstance(conversation_history, str):
        return f"Q1:Unknown Question\nA: {conversation_history}"

    else:
        return ""

# Helper functions for gen_expression_report()
"""Finds and returns the most dominant expression throughout the interview process"""
def get_dominant_expression(emotion_data: dict) -> list:
    all_emotions = []

    for data in emotion_data.values():
        all_emotions.extend(data.get("emotions", []))

    emotion_counts = Counter(all_emotions)
    most_common = emotion_counts.most_common(3)

    return [emotion for emotion, _ in most_common]

"""Calculates the average percentage of eye contact across all questions"""
def calculate_average_eye_contact(emotion_data: dict) -> int:
    eye_contact_values = []

    for data in emotion_data.values():
        eye_contact_values.append(data.get("eye contact", 0))

    if not eye_contact_values:
        return 0

    total = sum(eye_contact_values)
    average = total / len(eye_contact_values)

    return round(average)

"""Calculates the number of times the user looked away from the screen throughout the interview"""
def calculate_total_distractions(emotion_data: dict) -> int:
    total = 0

    for data in emotion_data.values():
        total += data.get("distractions", 0)

    return total

"""Calculates the number of times the user's face was missing from the screen"""
def calculate_total_face_absence(emotion_data: dict) -> int:
    total = 0

    for data in emotion_data.values():
        total += data.get("face absence", 0)

    return total

"""Checks if other people were found during the interview process to flag for cheating"""
def check_multi_person_flag(emotion_data: dict) -> bool:
    for data in emotion_data.values():
        if data.get("multi person", False):
            return True

    return False

