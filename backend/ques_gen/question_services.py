import os, json
from dotenv import load_dotenv
from pinecone import Pinecone
from pathlib import Path
import requests

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

REPORTS_DIR = Path("end/reports")

GEMINI_EMBED_URL = ("https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"f"?key={GEMINI_API_KEY}")

def _get_index():
    if not PINECONE_API_KEY:
        raise RuntimeError("Missing PINECONE_API_KEY")
    if not INDEX_NAME:
        raise RuntimeError("Missing PINECONE_INDEX_NAME")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if INDEX_NAME not in pc.list_indexes().names():
        raise ValueError(f"Index '{INDEX_NAME}' does not exist")
    return pc.Index(INDEX_NAME)

"""Takes the job role as an input, and returns it as a list of vectors to be able to query the Pinecone vector DB"""
def embed_text(text: str) -> list[float]:
    payload = {"content": {"parts": [{"text": text}]}}
    headers = {"Content-Type": "application/json"}
    response = requests.post(GEMINI_EMBED_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["embedding"]["values"]

"""Fetches relevant chunks from Pincone vector DB using the vector-embedded role"""
def fetch_resume_chunks(namespace: str, role: str, top_k: int = 3) -> dict:
    query_vector = embed_text(role)
    index = _get_index()
    response = index.query(
        namespace=namespace,
        top_k=top_k,
        include_metadata=True,
        vector=query_vector
    )

    chunks = [match["metadata"]["text"] for match in response["matches"]]
    return {
        "namespace": namespace,
        "chunks": chunks
    }

"""Loads conv_history.json for a resume and returns a normalized string for LLM prompts."""
def load_conversation_history(resume_id:str):
    # Location of conv_history.json file
    conv_file = REPORTS_DIR / resume_id / "conv_history.json"
    if conv_file.exists():
        with open(conv_file, "r", encoding="utf-8") as f:
            try:
                saved_history = json.load(f)
                if not isinstance(saved_history, dict):
                    saved_history = {}
            except json.JSONDecodeError:
                saved_history = {}
    else:
        saved_history = {}

    return normalize_history(saved_history)

"""Converts a conv_history dict into a formatted string for LLM prompts."""
def normalize_history(history: dict) -> str:
    if not history:
        return""
    
    segments = []

    for qid, answer in history.items():
        segments.append(f"Q: {qid}\nA: {answer.strip()}")
    return "\n\n".join(segments)