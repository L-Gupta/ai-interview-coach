from .question_services import fetch_resume_chunks, load_conversation_history
from .question_generate import generate_first_question, generate_followup_question

def generate_first(role: str, resume_id: str):
    chunks = fetch_resume_chunks(resume_id, role)
    question = generate_first_question(role, chunks)
    return question

def generate_followup(role: str, resume_id: str):
    # Use conv_history.json to load this
    history = load_conversation_history(resume_id)
    question = generate_followup_question(role, resume_id, history)
    return question
