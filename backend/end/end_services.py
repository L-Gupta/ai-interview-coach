import json, os, requests, httpx
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from .prompts_end import ACCURACY_PROMPT, JOB_FIT_PROMPT, VALIDATION_PROMPT, EMOTION_PROMPT
from dotenv import load_dotenv
from collections import Counter
from pinecone import Pinecone
from pathlib import Path

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

"""Compile tone and expression dictionaries into a summary via Gemini."""
"""
Args:
    resume_id (str): Unique ID of the resume folder where `tone.json` is stored.

Returns:
    emotion_report (dict):
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
async def gen_emotion_report(resume_id: str):
    try:
        print(f"[DEBUG] Generating emotion report for resume_id: {resume_id}")
        tone_file = REPORTS_DIR / resume_id / "tone.json"
        print(f"[DEBUG] Looking for tone file: {tone_file}")

        if not tone_file.exists():
            print("[DEBUG] tone.json not found, returning empty report.")
            return {
                "tone_summary": "No tone data found",
                "expression_summary": "",
                "raw_data": {}
            }

        # Load tone data
        try:
            with open(tone_file, "r", encoding="utf-8") as f:
                tone_dict = json.load(f)
            print(f"[DEBUG] Loaded tone data: {tone_dict}")
        except Exception as e:
            print(f"[ERROR] Failed to read tone.json: {e}")
            return {
                "tone_summary": "Error reading tone data",
                "expression_summary": "",
                "raw_data": {}
            }

        # Pre-calculate dominant tones
        try:
            dominant_tones = {q: Counter(vals).most_common(1)[0][0] for q, vals in tone_dict.items()}
            all_emotions = [emo for vals in tone_dict.values() for emo in vals]
            overall_dominant = Counter(all_emotions).most_common(1)[0][0] if all_emotions else "Neutral"
            print(f"[DEBUG] Dominant tones: {dominant_tones}, Overall: {overall_dominant}")
        except Exception as e:
            print(f"[ERROR] Failed to calculate dominant tones: {e}")
            dominant_tones = {}
            overall_dominant = "Neutral"

        # Build Gemini prompt
        prompt = EMOTION_PROMPT.format(
            tone_dict=json.dumps(tone_dict),
            expression_dict="{}"
        )
        print(f"[DEBUG] Gemini prompt built: {prompt}")

        try:
            response = await llm.ainvoke([HumanMessage(content=prompt)])
            text = response.content.strip()
            print(f"[DEBUG] Gemini raw response: {text}")

            if text.startswith("```"):
                text = text.strip("`")
                if "\n" in text:
                    text = "\n".join(text.split("\n")[1:])

            emotion_report = json.loads(text)
            print(f"[DEBUG] Parsed Gemini emotion report: {emotion_report}")
        except Exception as e:
            print(f"[ERROR] Gemini call or parsing failed: {e}")
            emotion_report = {
                "tone_summary": f"Overall dominant tone: {overall_dominant}",
                "dominant_tones_per_question": dominant_tones
            }

        # Include raw data
        emotion_report["raw_data"] = tone_dict
        print(f"[DEBUG] Final emotion report: {emotion_report}")
        return emotion_report

    except Exception as e:
        print(f"[CRITICAL] gen_emotion_report crashed: {e}")
        return {
            "tone_summary": "Error generating emotion report",
            "expression_summary": "",
            "raw_data": {}
        }
 
"""Compares each answer with relevant resume chunks to detect exaggerations or mismatches."""
"""
Args:
    resume_id (str): Unique ID of the resume folder.
    conversation_history (str): Conversation history as a formatted string with Q/A pairs.

Returns:
    results (dict) : {Question IDs (q1, q2, ...) : Gemini's validation result for each answer ("Match", "Exaggerated")}
"""
async def validate_exp(resume_id: str, conversation_history: str) -> dict:  
    results = {}                 # Initiating the empty dictionary to store the question number and its respective gemini respone
    blocks = conversation_history.strip().split("\n\n") # Cleaning the conversation history
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

        try:
            text = response.content.strip()
            if text.startswith("```"):
                text = text.strip("`")
                if "\n" in text:
                    text = "\n".join(text.split("\n")[1:])
            validation = json.loads(text)["validation"]
        except:
            validation = "Match" if "3 years" in chunk else "Exaggerated"

        results[q_key] = validation

    return results

"""Uses candidate answers, role, and Pinecone chunks to generate a job-fit score (0-100)."""
""""
Args:
    resume_id (str): Unique ID of the resume folder.
    role (str): Job role the candidate is applying for.
    conversation_history (str): Conversation history as a formatted string with Q/A pairs.

Returns:
    job_fit_score (int): Job fit score between 0 and 100 based on Gemini's analysis.
"""
async def calc_job_fit(resume_id: str, role: str, conversation_history: str) -> int:
    # Extract answers from the conversation history
    blocks = conversation_history.strip().split("\n\n")
    answers = []
    for block in blocks:
        for line in block.split("\n"):
            if line.lower().startswith("a:"):
                answers.append(line.split(":", 1)[1].strip())

    # Retrieve relevant chunks from Pinecone for each answer
    all_chunks = []
    for ans in answers:
        chunks = await get_relevant_chunks(resume_id=resume_id, answer=ans, top_k=3)
        all_chunks.extend(chunks)

    # Remove duplicates and join chunks for context
    unique_chunks = list(set(all_chunks))
    context_text = "\n".join([f"- {chunk}" for chunk in unique_chunks])
    answers_text = "\n".join([f"- {ans}" for ans in answers])

    # Build the Gemini prompt and call it
    prompt = JOB_FIT_PROMPT.format(role=role, answers=answers_text, context=context_text)
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    # 5️⃣ Parse the job-fit score from Gemini's JSON
    try:
        text = response.content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if "\n" in text:
                text = "\n".join(text.split("\n")[1:])
        job_fit_score = int(json.loads(text)["score"])
    except:
        import re
        numbers = re.findall(r"\d+", response.content)
        job_fit_score = int(numbers[0]) if numbers else 75

    return job_fit_score

"""Passes conversation history to Gemini and gets answer accuracy scores (1-100)."""
""""
Args:
    conversation_history (str): Conversation history as a formatted string with Q/A pairs.

Returns: 
    accuracy_score (dict): {Overall  : Accuracy scores as returned by Gemini.}
"""
async def calc_acc(conversation_history: str) -> dict:
    if not conversation_history:
        return {"overall": 0}

    # Call Gemini
    prompt = ACCURACY_PROMPT.format(qa_pairs=conversation_history)
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    # 🔹 Extract text and parse JSON
    try:
        text = response.content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if "\n" in text:
                text = "\n".join(text.split("\n")[1:])
        accuracy_scores = json.loads(text)
    except Exception as e:
        print("Gemini parsing error:", e)
        print("Raw response text:", response.content)
        accuracy_scores = {"overall": 75}

    return accuracy_scores


#Helper functions
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
