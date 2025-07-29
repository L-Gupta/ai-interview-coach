import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from .question_prompt import first_question_prompt, followup_question_prompt
from .question_services import fetch_resume_chunks

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

def generate_first_question(role: str, chunks: list[str]) -> str:
    resume_context = "\n\n".join(chunks)
    prompt = first_question_prompt(role, resume_context)
    return llm.invoke(prompt).content.strip()

def generate_followup_question(role: str, resume_id: str, conversation_text: str) -> str:
    chunk_data = fetch_resume_chunks(namespace=resume_id, role=role)
    resume_context = "\n\n".join(chunk_data["chunks"])

    prompt = followup_question_prompt(role, resume_context, conversation_text)
    return llm.invoke(prompt).content.strip()
