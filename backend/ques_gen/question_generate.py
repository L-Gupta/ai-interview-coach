import os, random
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from .question_prompt import first_question_prompt, followup_question_prompt
from .question_services import fetch_resume_chunks

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

# Fallback defaults
DEFAULT_FIRST_QUESTION = "Can you tell me a bit about yourself and why you're interested in this role?"
DEFAULT_FOLLOWUP_QUESTIONS = [
    "What would you say is your biggest strength relevant to this position?",
    "Tell me about a challenge you faced and how you overcame it.",
    "How do you stay updated with new technologies in your field?",
    "What attracted you to this company or role?",
    "Describe a project you’re most proud of and your role in it."
]

def generate_first_question(role: str, chunks: list[str]) -> str:
    resume_context = "\n\n".join(chunks)
    prompt = first_question_prompt(role, resume_context)

    try:
        return llm.invoke(prompt).content.strip()
    except Exception as e:
        print(f"⚠️ Gemini error (first question): {e}")
        return DEFAULT_FIRST_QUESTION

def generate_followup_question(role: str, resume_id: str, conversation_text: str) -> str:
    chunk_data = fetch_resume_chunks(namespace=resume_id, role=role)
    resume_context = "\n\n".join(chunk_data["chunks"])

    prompt = followup_question_prompt(role, resume_context, conversation_text)

    try:
        return llm.invoke(prompt).content.strip()
    except Exception as e:
        print(f"⚠️ Gemini error (follow-up question): {e}")
        return random.choice(DEFAULT_FOLLOWUP_QUESTIONS)
