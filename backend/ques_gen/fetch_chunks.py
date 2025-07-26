import os
from dotenv import load_dotenv
from pinecone import Pinecone
import requests

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

GEMINI_EMBED_URL = ("https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"f"?key={GEMINI_API_KEY}")

def embed_text(text: str) -> list[float]:
    payload = {"content": {"parts": [{"text": text}]}}
    headers = {"Content-Type": "application/json"}
    response = requests.post(GEMINI_EMBED_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["embedding"]["values"]

def fetch_resume_chunks(namespace: str, role: str, top_k: int = 3) -> dict:
    query_vector = embed_text(role)

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
