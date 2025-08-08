import os
import random
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from .question_services import fetch_resume_chunks, load_conversation_history

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

# Fallback follow-up questions
DEFAULT_FOLLOWUP_QUESTIONS = [
    "What would you say is your biggest strength relevant to this position?",
    "Tell me about a challenge you faced and how you overcame it.",
    "How do you stay updated with new technologies in your field?",
    "What attracted you to this company or role?",
    "Describe a project you’re most proud of and your role in it."
]

def followup_question_prompt(role: str, resume_context: str, conversation_text: str) -> str:
    return (
        f"You are an AI interview coach. The candidate is applying for the role of {role}.\n"
        f"Resume summary:\n\n{resume_context}\n\n"
        f"Conversation so far:\n\n{conversation_text}\n\n"
        f"Your task:\n"
        f"- Generate ONLY the next follow-up interview question.\n"
        f"- Base it on the candidate's previous answers and the job role.\n"
        f"- DO NOT include explanations, greetings, or any text other than the question.\n"
        f"- Return ONLY the question as plain text, no quotes, no prefixes like 'Q:'."
    )

def generate_followup_question(role: str, resume_id: str, conversation_text: str) -> str:
    chunk_data = fetch_resume_chunks(namespace=resume_id, role=role)
    resume_context = "\n\n".join(chunk_data["chunks"])

    prompt = followup_question_prompt(role, resume_context, conversation_text)

    try:
        return llm.invoke(prompt).content.strip()
    except Exception as e:
        print(f"⚠️ Gemini error (follow-up question): {e}")
        return random.choice(DEFAULT_FOLLOWUP_QUESTIONS)

def generate_followup(role: str, resume_id: str):
    history = load_conversation_history(resume_id)
    return generate_followup_question(role, resume_id, history)
