"""
This module generates follow-up interview questions using Gemini.
It considers:
1. Candidate's job role
2. Resume content (fetched from Pinecone)
3. Previous conversation history (Q&A)

Output: A single follow-up question as a string.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from ques_gen.fetch_chunks import fetch_resume_chunks

# Load environment variables (API Key)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini LLM (using 1.5 Flash for speed)
llm = ChatGoogleGenerativeAI(model = "models/gemini-1.5-flash-latest", google_api_key = GEMINI_API_KEY)

def format_history(history: list[dict]) -> str:
    """
    Convert conversation history (list of dicts) into readable text for prompt.

    Example Input:
    [
        {"question": "Tell me about X", "answer": "I worked on Y"},
        {"question": "What tech stack?", "answer": "React, Node.js"}
    ]

    Output:
    Q: Tell me about X
    A: I worked on Y

    Q: What tech stack?
    A: React, Node.js
    """
    
    convo = []
    for dialogue in history:
        ques = dialogue.get("question", "").strip()
        ans = dialogue.get("answer", "").strip()
        if ques and ans:
            convo.append(f"Q: {ques}\nA: {ans}")
    return "\n\n".join(convo)

def generate_followup_question(role: str, namespace: str, history: list[dict], top_k: int = 5) -> str:
    """
    Generate a follow-up interview question using:
    - Candidate role
    - Resume content (Pinecone chunks)
    - Conversation history

    Args:
        role (str): Candidate's job role
        namespace (str): Pinecone namespace (resume_id)
        history (list[dict]): Conversation so far [{question, answer}, ...]
        top_k (int): Number of chunks to retrieve from Pinecone (default=5)

    Returns:
        str: A follow-up question string
    """

    # 1️⃣ Fetch relevant resume chunks from Pinecone
    chunk_data = fetch_resume_chunks(namespace=namespace, role=role, top_k=top_k)
    resume_context = "\n\n".join(chunk_data["chunks"])

    # 2️⃣ Format conversation history into readable text
    conversation = format_history(history)

    # 3️⃣ Build the prompt for Gemini
    prompt = (
        f"You are an AI interview coach. The candidate is applying for the role of {role}.\n"
        f"Here is a summary of their resume:\n\n"
        f"{resume_context}\n\n"
        f"Here is the conversation so far:\n\n"
        f"{conversation}\n\n"
        f"The answers are transcripts from speech recognition and may not be perfectly structured. "
        f"Based on the above, generate the next logical follow-up question. "
        f"The question should be role-specific and build on what the candidate has already answered."
    )

    # 4️⃣ Generate the question using Gemini
    response = llm.invoke(prompt)

    # 5️⃣ Return only the question text
    return response.content.strip()
