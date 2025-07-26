from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model = "models/gemini-1.5-flash-latest", google_api_key = GEMINI_API_KEY)

def generate_first_question(role: str, chunks: list[str]) -> str:
    resume_context = "\n\n".join(chunks)
    prompt = (
        f"You are an AI interview coach. The candidate is applying for the role of {role}.\n"
        f"Below is a summary of their resume:\n\n"
        f"{resume_context}\n\n"
        f"Generate the first question you'd ask in an interview. "
        f"Start with a general question to introduce the candidate."
    )
    return llm.invoke(prompt).content.strip()
