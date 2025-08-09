import os
import random
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from ques_gen.question_services import fetch_resume_chunks, load_conversation_history
from ques_gen.question_prompt import followup_question_prompt

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

def generate_followup_question(role: str, resume_id: str, conversation_text: str) -> str:
    chunk_data = fetch_resume_chunks(namespace=resume_id, role=role)
    resume_context = "\n\n".join(chunk_data["chunks"])

    prompt = followup_question_prompt(role, resume_context, conversation_text)

    try:
        return llm.invoke(prompt).content.strip()
    except Exception as e:
        print(f"⚠️ Gemini error (follow-up question): {e}")
        return random.choice(DEFAULT_FOLLOWUP_QUESTIONS)

"""Public entrypoint used by the router. Loads convo history and generates the next question."""
def generate_followup(role: str, resume_id: str):
    history = load_conversation_history(resume_id)
    return generate_followup_question(role, resume_id, history)
