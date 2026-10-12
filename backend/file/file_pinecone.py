"""
Pinecone Vector Database Operations
Handles upserting embeddings to Pinecone for RAG retrieval.
"""
import os
from typing import List, Dict, Any
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "interview-index")

# Initialize Pinecone
pc = None
index = None

def init_pinecone():
    """Initialize Pinecone client and index."""
    global pc, index
    
    if not PINECONE_API_KEY or PINECONE_API_KEY == "your-pinecone-api-key":
        print("⚠️  Warning: PINECONE_API_KEY not set. Skipping Pinecone operations.")
        return False
    
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists
        if PINECONE_INDEX_NAME not in pc.list_indexes().names():
            print(f"Creating index: {PINECONE_INDEX_NAME}")
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=768,  # Gemini embedding dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
        
        index = pc.Index(PINECONE_INDEX_NAME)
        print(f"✅ Pinecone initialized: {PINECONE_INDEX_NAME}")
        return True
        
    except Exception as e:
        print(f"❌ Pinecone initialization failed: {e}")
        return False


def upsert_embeddings(embeddings: List[Dict[str, Any]], resume_id: str) -> bool:
    """
    Upsert embeddings to Pinecone.
    
    Args:
        embeddings: List of dicts with 'text' and 'embedding' keys
        resume_id: Resume identifier for metadata
        
    Returns:
        bool: Success status
    """
    global index
    
    if index is None:
        if not init_pinecone():
            print("⚠️  Skipping Pinecone upsert (not initialized)")
            return False
    
    try:
        # Prepare vectors for upsert
        vectors = []
        for i, item in enumerate(embeddings):
            vectors.append({
                "id": f"{resume_id}_chunk_{i}",
                "values": item["embedding"],
                "metadata": {
                    "resume_id": resume_id,
                    "text": item["text"][:1000],  # Pinecone metadata limit
                    "chunk_index": i
                }
            })
        
        # Batch upsert
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch)
        
        print(f"✅ Upserted {len(vectors)} vectors to Pinecone")
        return True
        
    except Exception as e:
        print(f"❌ Pinecone upsert failed: {e}")
        return False


def query_resume(query_embedding: List[float], resume_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Query Pinecone for relevant resume chunks.
    
    Args:
        query_embedding: Query vector
        resume_id: Filter by resume ID
        top_k: Number of results
        
    Returns:
        List of matches with text and scores
    """
    global index
    
    if index is None:
        if not init_pinecone():
            return []
    
    try:
        results = index.query(
            vector=query_embedding,
            filter={"resume_id": resume_id},
            top_k=top_k,
            include_metadata=True
        )
        
        matches = []
        for match in results["matches"]:
            matches.append({
                "text": match["metadata"]["text"],
                "score": match["score"],
                "chunk_index": match["metadata"].get("chunk_index", 0)
            })
        
        return matches
        
    except Exception as e:
        print(f"❌ Pinecone query failed: {e}")
        return []


def delete_resume_vectors(resume_id: str) -> bool:
    """Delete all vectors for a resume."""
    global index
    
    if index is None:
        if not init_pinecone():
            return False
    
    try:
        index.delete(filter={"resume_id": resume_id})
        print(f"✅ Deleted vectors for resume: {resume_id}")
        return True
        
    except Exception as e:
        print(f"❌ Delete failed: {e}")
        return False
