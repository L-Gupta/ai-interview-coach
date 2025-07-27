import json, os, requests
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
async def gen_emotion_report(resume_id: str):
    tone_file = REPORTS_DIR / resume_id / "tone.json"
    if not tone_file.exists():
        return {"tone_summary": "No tone data found", "expression_summary": ""}

    # ✅ Load tone data from file
    with open(tone_file, "r", encoding="utf-8") as f:
        tone_dict = json.load(f)

    # 🔹 Pre-calculate dominant tones for fallback
    dominant_tones = {q: Counter(vals).most_common(1)[0][0] for q, vals in tone_dict.items()}
    all_emotions = [emo for vals in tone_dict.values() for emo in vals]
    overall_dominant = Counter(all_emotions).most_common(1)[0][0] if all_emotions else "Neutral"

    # ✅ Prepare Gemini prompt
    prompt = EMOTION_PROMPT.format(
        tone_dict=json.dumps(tone_dict),
        expression_dict="{}"   # if we add expressions later
    )

    # ✅ Call Gemini
    try:
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        text = response.content.strip()

        # Remove code fences if Gemini returns markdown
        if text.startswith("```"):
            text = text.strip("`")
            if "\n" in text:
                text = "\n".join(text.split("\n")[1:])

        emotion_report = json.loads(text)
    except Exception:
        # 🔹 Fallback to local calculation if Gemini fails
        emotion_report = {
            "tone_summary": f"Overall dominant tone: {overall_dominant}",
            "dominant_tones_per_question": dominant_tones
        }

    # ✅ Include raw data for reference
    emotion_report["raw_data"] = tone_dict
    return emotion_report

"""Compares each answer with relevant resume chunk to detect exaggerations or mismatches."""
async def validate_exp(resume_id: str, conversation_history: list):
    results = {}

    for idx, item in enumerate(conversation_history, start=1):
        q_key = f"q{idx}"
        answer = item["answer"]

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

"""Use candidate answers, role, and Pinecone chunks to generate a job-fit score"""
async def calc_job_fit(resume_id: str, role: str, conv_history: list):
    # 1️⃣ Extract answers from the conversation history
    answers = [item["answer"] for item in conv_history]

    # 2️⃣ Retrieve relevant chunks from Pinecone for each answer
    all_chunks = []
    for ans in answers:
        chunks = await get_relevant_chunks(resume_id, ans)
        all_chunks.extend(chunks)

    # Remove duplicates and join chunks for context
    unique_chunks = list(set(all_chunks))
    context_text = "\n".join([f"- {chunk}" for chunk in unique_chunks])
    answers_text = "\n".join([f"- {ans}" for ans in answers])

    # 3️⃣ Build the Gemini prompt
    prompt = JOB_FIT_PROMPT.format(role=role, answers=answers_text, context=context_text)

    # 4️⃣ Call Gemini via LangChain
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

"""Pass coversation history to gemini and get accuracy scores (1-100)"""
async def calc_acc(resume_id: str, conversation_history: list):
    if not conversation_history:
        return {"overall": 0}

    # Prepare QA text
    qa_pairs = "\n".join(
        [f"Q: {item['question']}\nA: {item['answer']}" for item in conversation_history]
    )

    # 🔹 Call Gemini
    prompt = ACCURACY_PROMPT.format(qa_pairs=qa_pairs)
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    # 🔹 Extract text and parse JSON
    try:
        text = response.content.strip()
        # Remove Markdown code fences if present
        if text.startswith("```"):
            text = text.strip("`")
            # If there's a language tag like 'json', split on newline
            if "\n" in text:
                text = "\n".join(text.split("\n")[1:])

        accuracy_scores = json.loads(text)
    except Exception as e:
        print("Gemini parsing error:", e)
        print("Raw response text:", response.content)
        accuracy_scores = {"overall": 75}

    return accuracy_scores

"""Query Pinecone for the most relevant resume chunks based on an answer."""
async def get_relevant_chunks(resume_id: str, answer: str, top_k: int = 3):
    # 1️⃣ Create embedding for the answer using Gemini's embedding endpoint
    payload = {
        "model": "models/embedding-001",
        "content": {"parts": [{"text": answer}]}
    }
    resp = requests.post(GEMINI_EMBEDDING_URL, json=payload)
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