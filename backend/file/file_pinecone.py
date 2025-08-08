import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

"""
Upserts embedded resume chunks into Pinecone using the filename (without extension)as the namespace. 
Each item must have 'chunk_id', 'embedding', and 'text'.
"""
def upsert_embeddings(embedding_results: list[dict], resume_id: str):
    if INDEX_NAME not in pc.list_indexes().names():
        raise ValueError(f"Index '{INDEX_NAME}' does not exist.")

    vectors = []
    for item in embedding_results:
        if "chunk_id" not in item or "embedding" not in item or "text" not in item:
            raise ValueError("Each item must have 'chunk_id', 'embedding', and 'text' keys")

        vector_id = f"{resume_id}_chunk_{item['chunk_id']}"
        vectors.append({
            "id": vector_id,
            "values": item["embedding"],
            "metadata": {
                "resume_id": resume_id,
                "text": item["text"]
            }
        })

    index.upsert(vectors=vectors, namespace=resume_id)
    print(f"✅ {len(vectors)} embeddings upserted to Pinecone (namespace: {resume_id})")