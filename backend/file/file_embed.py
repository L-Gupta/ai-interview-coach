import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY")

UPLOAD_DIR = os.path.join("file", "uploads")

GEMINI_EMBEDDING_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"
    f"?key={GEMINI_API_KEY}"
)

def load_chunks_from_file(filename: str) -> list[str]:
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return []
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by --- Chunk X --- markers
    raw_chunks = content.split("--- Chunk ")
    chunks = []
    for section in raw_chunks:
        lines = section.strip().split("\n", 1)
        if len(lines) == 2:
            _, chunk_text = lines
            chunks.append(chunk_text.strip())
    return chunks


def embed_chunks(chunks: list[str]) -> list[dict]:
    headers = {
        "Content-Type": "application/json"
    }

    results = []
    for i, chunk in enumerate(chunks):
        payload = {"content": {"parts": [{"text": chunk}]},
                "taskType": "RETRIEVAL_DOCUMENT"}

        try:
            response = requests.post(GEMINI_EMBEDDING_URL, headers=headers, json=payload)
            response.raise_for_status()
            embedding = response.json()["embedding"]["values"]
            results.append({"chunk_id": i, "embedding": embedding, "text":chunk})
        except Exception as e:
            print(f"❌ Error embedding chunk {i+1}: {e}")
    
    return results
