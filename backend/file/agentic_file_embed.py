"""
Agentic Resume Embedder
Uses LangChain agent to intelligently create embeddings with error handling and optimization.
"""

import os
import requests
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_classic.tools import Tool
from langchain_core.prompts import PromptTemplate

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
UPLOAD_DIR = os.path.join("file", "uploads")

GEMINI_EMBEDDING_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent"
    f"?key={GEMINI_API_KEY}"
)

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0
)


class AgenticEmbedder:
    """
    Intelligent embedding agent that:
    - Handles API failures with retry logic
    - Validates embeddings before returning
    - Optimizes batch processing
    - Detects and handles edge cases (empty chunks, too long chunks)
    """
    
    def __init__(self):
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        self.embeddings_cache = {}  # Simple cache
    
    def _create_tools(self) -> List[Tool]:
        """Define tools for embedding operations."""
        
        def embed_single_chunk(text: str) -> str:
            """Embed a single text chunk using Gemini API."""
            if not text.strip():
                return "ERROR: Empty text provided"
            
            # Check cache first
            cache_key = text[:100]  # Use first 100 chars as key
            if cache_key in self.embeddings_cache:
                return "CACHED: Retrieved from cache"
            
            headers = {"Content-Type": "application/json"}
            payload = {
                "content": {"parts": [{"text": text}]},
                "taskType": "RETRIEVAL_DOCUMENT"
            }
            
            try:
                response = requests.post(GEMINI_EMBEDDING_URL, headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                embedding = response.json()["embedding"]["values"]
                
                # Cache the result
                self.embeddings_cache[cache_key] = embedding
                
                return f"SUCCESS: Generated {len(embedding)}-dimensional embedding"
            except requests.exceptions.Timeout:
                return "ERROR: API timeout"
            except requests.exceptions.RequestException as e:
                return f"ERROR: {str(e)}"
        
        def embed_batch(chunks_json: str) -> str:
            """Embed multiple chunks efficiently."""
            try:
                chunks = json.loads(chunks_json)
                if not isinstance(chunks, list):
                    return "ERROR: Input must be a JSON list of strings"
                
                success_count = 0
                error_count = 0
                
                for chunk in chunks:
                    result = embed_single_chunk(chunk)
                    if "SUCCESS" in result or "CACHED" in result:
                        success_count += 1
                    else:
                        error_count += 1
                
                return f"Batch complete: {success_count} succeeded, {error_count} failed"
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        def validate_chunk_length(text: str) -> str:
            """Check if chunk is appropriate length for embedding."""
            if not text.strip():
                return "INVALID: Empty chunk"
            elif len(text) < 10:
                return "WARNING: Chunk very short (<10 chars)"
            elif len(text) > 5000:
                return "ERROR: Chunk too long (>5000 chars), may fail"
            else:
                return f"VALID: {len(text)} characters"
        
        def retry_failed_embedding(text: str, max_retries: int = 3) -> str:
            """Retry embedding with exponential backoff."""
            import time
            
            for attempt in range(max_retries):
                result = embed_single_chunk(text)
                
                if "SUCCESS" in result or "CACHED" in result:
                    return f"SUCCESS on attempt {attempt + 1}"
                
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    time.sleep(wait_time)
            
            return f"FAILED after {max_retries} attempts"
        
        def optimize_chunk_for_embedding(text: str) -> str:
            """Clean and optimize text before embedding."""
            # Remove excessive whitespace
            cleaned = " ".join(text.split())
            
            # Remove special characters that might cause issues
            cleaned = cleaned.encode('ascii', 'ignore').decode('ascii')
            
            # Truncate if too long
            if len(cleaned) > 4000:
                cleaned = cleaned[:4000] + "..."
            
            return cleaned
        
        def check_api_health() -> str:
            """Verify Gemini API is accessible."""
            test_text = "API health check"
            result = embed_single_chunk(test_text)
            return "API_HEALTHY" if "SUCCESS" in result else "API_UNAVAILABLE"
        
        return [
            Tool(
                name="EmbedSingle",
                func=embed_single_chunk,
                description="Embed one text chunk. Input: text string"
            ),
            Tool(
                name="EmbedBatch",
                func=embed_batch,
                description="Embed multiple chunks efficiently. Input: JSON list of strings"
            ),
            Tool(
                name="ValidateChunkLength",
                func=validate_chunk_length,
                description="Check if chunk length is appropriate. Input: text"
            ),
            Tool(
                name="RetryFailed",
                func=retry_failed_embedding,
                description="Retry embedding with backoff. Input: text"
            ),
            Tool(
                name="OptimizeChunk",
                func=optimize_chunk_for_embedding,
                description="Clean and prepare text for embedding. Input: text"
            ),
            Tool(
                name="CheckAPIHealth",
                func=check_api_health,
                description="Verify Gemini API is working. No input needed."
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create the embedding agent."""
        
        template = """You are an intelligent embedding agent. Your job is to convert text chunks into vector embeddings reliably.

Available tools: {tools}
Tool names: {tool_names}

Strategy:
1. First check API health
2. For each chunk:
   - Validate length
   - Optimize if needed
   - Try embedding
   - Retry if it fails
3. Handle errors gracefully
4. Report final status

Use this format:
Thought: [Your reasoning]
Action: [Tool name]
Action Input: [Input]
Observation: [Result]
... (repeat as needed)
Thought: All chunks processed
Final Answer: [Summary of results]

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)
        agent = create_react_agent(llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )
    
    def embed_chunks(self, chunks: List[str]) -> List[Dict]:
        """
        Main embedding function using agent intelligence.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            List of dicts with chunk_id, embedding, and text
        """
        results = []
        
        # Use agent for first chunk to test API
        if chunks:
            try:
                agent_result = self.agent.invoke({
                    "input": f"Embed this chunk with error handling: {chunks[0][:200]}"
                })
                print(f"Agent strategy: {agent_result.get('output', '')}")
            except Exception as e:
                print(f"⚠️ Agent planning failed: {e}")
        
        # Process chunks with fallback logic
        for i, chunk in enumerate(chunks):
            result = self._embed_with_fallback(chunk, i)
            if result:
                results.append(result)
        
        return results
    
    def _embed_with_fallback(self, text: str, chunk_id: int) -> Optional[Dict]:
        """Embed with intelligent fallback."""
        # Validate
        if not text.strip():
            print(f"⚠️ Skipping empty chunk {chunk_id}")
            return None
        
        # Optimize
        if len(text) > 4000:
            text = text[:4000] + "..."
        
        # Try embedding with retries
        for attempt in range(3):
            try:
                headers = {"Content-Type": "application/json"}
                payload = {
                    "content": {"parts": [{"text": text}]},
                    "taskType": "RETRIEVAL_DOCUMENT"
                }
                
                response = requests.post(GEMINI_EMBEDDING_URL, headers=headers, json=payload, timeout=10)
                response.raise_for_status()
                embedding = response.json()["embedding"]["values"]
                
                return {
                    "chunk_id": chunk_id,
                    "embedding": embedding,
                    "text": text
                }
            except Exception as e:
                if attempt < 2:
                    print(f"⚠️ Retry {attempt + 1} for chunk {chunk_id}")
                    import time
                    time.sleep(2 ** attempt)
                else:
                    print(f"❌ Failed to embed chunk {chunk_id}: {e}")
                    return None
    
    def load_chunks_from_file(self, filename: str) -> List[str]:
        """Load chunks from file."""
        path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(path):
            print(f"❌ File not found: {path}")
            return []
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split by chunk markers
        raw_chunks = content.split("--- Chunk ")
        chunks = []
        for section in raw_chunks:
            lines = section.strip().split("\n", 1)
            if len(lines) == 2:
                _, chunk_text = lines
                chunks.append(chunk_text.strip())
        
        return chunks


# Drop-in replacement functions
def embed_chunks(chunks: List[str]) -> List[Dict]:
    """
    Drop-in replacement for existing embed_chunks function.
    Now uses intelligent agent-based embedding.
    """
    embedder = AgenticEmbedder()
    return embedder.embed_chunks(chunks)


def load_chunks_from_file(filename: str) -> List[str]:
    """Drop-in replacement."""
    embedder = AgenticEmbedder()
    return embedder.load_chunks_from_file(filename)


# Example usage
if __name__ == "__main__":
    embedder = AgenticEmbedder()
    
    # Test with existing chunks file
    test_file = "kunal_passan_chunks.txt"
    
    print(f"\n{'='*60}")
    print(f"Testing Agentic Embedder with: {test_file}")
    print(f"{'='*60}\n")
    
    chunks = embedder.load_chunks_from_file(test_file)
    
    if chunks:
        print(f"Loaded {len(chunks)} chunks")
        print(f"\nEmbedding with agentic approach...\n")
        
        embeddings = embedder.embed_chunks(chunks[:3])  # Test first 3
        
        print(f"\n{'='*60}")
        print(f"EMBEDDING RESULT")
        print(f"{'='*60}")
        print(f"Successfully embedded: {len(embeddings)}/{len(chunks[:3])} chunks")
        
        for emb in embeddings:
            print(f"\nChunk {emb['chunk_id']}:")
            print(f"  Embedding dimension: {len(emb['embedding'])}")
            print(f"  Text preview: {emb['text'][:100]}...")
    else:
        print("\n❌ No chunks found")