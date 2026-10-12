"""
Agentic File Processing Controller
Orchestrates the entire resume processing pipeline with intelligent decision-making.
"""

import os
from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_classic.tools import Tool
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Import our agentic modules
from file.agentic_file_parse import AgenticResumeParser
from file.agentic_file_chunk import AgenticResumeChunker
from file.agentic_file_embed import AgenticEmbedder

# Import Pinecone upserter (non-agentic, but wrapped as a tool)
import sys
sys.path.append('..')
from file.file_pinecone import upsert_embeddings

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0
)


class AgenticPipelineController:
    """
    Master agent that orchestrates the entire resume processing pipeline.
    
    This agent:
    1. Decides the optimal parsing strategy
    2. Validates parsed output
    3. Chooses chunking approach
    4. Manages embedding with error recovery
    5. Ensures successful Pinecone upload
    """
    
    def __init__(self):
        self.parser = AgenticResumeParser()
        self.chunker = AgenticResumeChunker()
        self.embedder = AgenticEmbedder()
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Define pipeline tools."""
        
        def parse_resume_tool(filename: str) -> str:
            """Parse resume using intelligent agent."""
            try:
                text = self.parser.parse_resume(filename)
                if text and len(text) > 50:
                    self.parser.save_parsed_text(text, filename)
                    return f"SUCCESS: Parsed {len(text)} characters"
                else:
                    return "ERROR: Parsing failed or text too short"
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        def chunk_resume_tool(parsed_filename: str) -> str:
            """Chunk parsed resume intelligently."""
            try:
                chunks = self.chunker.chunk_parsed_resume(parsed_filename)
                if chunks and len(chunks) >= 2:
                    self.chunker.save_chunks_to_file(chunks, parsed_filename)
                    return f"SUCCESS: Created {len(chunks)} chunks"
                else:
                    return "ERROR: Chunking failed or too few chunks"
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        def embed_chunks_tool(chunks_filename: str) -> str:
            """Embed chunks with retry logic."""
            try:
                chunks = self.embedder.load_chunks_from_file(chunks_filename)
                embeddings = self.embedder.embed_chunks(chunks)
                
                if embeddings and len(embeddings) == len(chunks):
                    # Store temporarily for Pinecone upload
                    self._temp_embeddings = embeddings
                    return f"SUCCESS: Embedded {len(embeddings)} chunks"
                else:
                    return f"PARTIAL: Embedded {len(embeddings)}/{len(chunks)} chunks"
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        def upload_to_pinecone_tool(resume_id: str) -> str:
            """Upload embeddings to Pinecone."""
            try:
                if not hasattr(self, '_temp_embeddings'):
                    return "ERROR: No embeddings available to upload"
                
                upsert_embeddings(self._temp_embeddings, resume_id=resume_id)
                return f"SUCCESS: Uploaded {len(self._temp_embeddings)} vectors to Pinecone"
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        def validate_pipeline_output(resume_id: str) -> str:
            """Validate that all pipeline steps succeeded."""
            from pathlib import Path
            
            upload_dir = Path("file/uploads")
            
            checks = {
                "parsed_file": upload_dir / f"{resume_id}_parsed.txt",
                "chunks_file": upload_dir / f"{resume_id}_chunks.txt",
            }
            
            for name, path in checks.items():
                if not path.exists():
                    return f"FAILED: {name} not found"
            
            return "VALID: All pipeline artifacts present"
        
        def retry_failed_step(step_name: str, *args) -> str:
            """Retry a failed pipeline step."""
            try:
                if step_name == "parse":
                    return parse_resume_tool(*args)
                elif step_name == "chunk":
                    return chunk_resume_tool(*args)
                elif step_name == "embed":
                    return embed_chunks_tool(*args)
                elif step_name == "upload":
                    return upload_to_pinecone_tool(*args)
                else:
                    return f"ERROR: Unknown step {step_name}"
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        return [
            Tool(
                name="ParseResume",
                func=parse_resume_tool,
                description="Parse resume file intelligently. Input: filename (e.g., 'resume.pdf')"
            ),
            Tool(
                name="ChunkResume",
                func=chunk_resume_tool,
                description="Chunk parsed resume. Input: parsed_filename (e.g., 'resume_parsed.txt')"
            ),
            Tool(
                name="EmbedChunks",
                func=embed_chunks_tool,
                description="Create embeddings for chunks. Input: chunks_filename (e.g., 'resume_chunks.txt')"
            ),
            Tool(
                name="UploadToPinecone",
                func=upload_to_pinecone_tool,
                description="Upload embeddings to vector database. Input: resume_id"
            ),
            Tool(
                name="ValidatePipeline",
                func=validate_pipeline_output,
                description="Check all pipeline steps completed. Input: resume_id"
            ),
            Tool(
                name="RetryStep",
                func=retry_failed_step,
                description="Retry a failed step. Input: step_name, args"
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create master orchestration agent."""
        
        template = """You are a master resume processing agent. You orchestrate the entire pipeline from upload to vector database.

Available tools: {tools}
Tool names: {tool_names}

Pipeline steps:
1. Parse resume (PDF/DOCX → text)
2. Chunk text (text → semantic chunks)
3. Embed chunks (chunks → vectors)
4. Upload to Pinecone (vectors → database)
5. Validate completion

Strategy:
- Execute steps in order
- If a step fails, try to diagnose and retry
- Validate output after each critical step
- Report progress and final status

Use this format:
Thought: [Current situation and next action]
Action: [Tool to use]
Action Input: [Input for tool]
Observation: [Tool result]
... (repeat as needed)
Thought: Pipeline complete or failed
Final Answer: [Summary of results]

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)
        agent = create_react_agent(llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=15,
            handle_parsing_errors=True
        )
    
    def run_pipeline(self, filename: str, resume_id: str) -> Dict:
        """
        Run the complete agentic pipeline.
        Drop-in replacement for your existing run_pipeline function.
        
        Args:
            filename: Resume file name (e.g., "kunal_passan.pdf")
            resume_id: Unique identifier for the resume
            
        Returns:
            Dict with processing results
        """
        print(f"\n{'='*60}")
        print(f"🤖 AGENTIC PIPELINE STARTED")
        print(f"{'='*60}")
        print(f"File: {filename}")
        print(f"Resume ID: {resume_id}\n")
        
        try:
            # Let the agent orchestrate the entire pipeline
            result = self.agent.invoke({
                "input": f"""Process resume file '{filename}' with resume_id '{resume_id}'.
                
Complete pipeline:
1. Parse {filename}
2. Chunk {resume_id}_parsed.txt
3. Embed {resume_id}_chunks.txt
4. Upload to Pinecone with namespace {resume_id}
5. Validate all steps

Handle errors intelligently and report final status."""
            })
            
            # Extract summary
            output = result.get("output", "")
            
            # Check if successful by validating artifacts
            from pathlib import Path
            upload_dir = Path("file/uploads")
            
            parsed_exists = (upload_dir / f"{resume_id}_parsed.txt").exists()
            chunks_exists = (upload_dir / f"{resume_id}_chunks.txt").exists()
            
            if parsed_exists and chunks_exists:
                # Count chunks
                chunks = self.chunker.chunk_parsed_resume(f"{resume_id}_parsed.txt")
                
                return {
                    "status": "success",
                    "chunks": len(chunks),
                    "resume_id": resume_id,
                    "agent_summary": output,
                    "message": f"✅ Pipeline completed: {len(chunks)} chunks processed"
                }
            else:
                return {
                    "status": "partial_failure",
                    "resume_id": resume_id,
                    "agent_summary": output,
                    "message": "⚠️ Pipeline incomplete - check logs"
                }
                
        except Exception as e:
            print(f"\n❌ PIPELINE FAILED: {e}")
            return {
                "status": "failed",
                "resume_id": resume_id,
                "error": str(e),
                "message": f"❌ Pipeline failed: {e}"
            }
        finally:
            print(f"\n{'='*60}")
            print(f"🏁 PIPELINE ENDED")
            print(f"{'='*60}\n")


# Drop-in replacement function for existing codebase
def run_pipeline(filename: str, resume_id: str) -> Dict:
    """
    Drop-in replacement for backend/file/file_controller.py::run_pipeline
    
    This uses an intelligent agent to orchestrate the entire pipeline,
    replacing the manual step-by-step approach.
    """
    controller = AgenticPipelineController()
    return controller.run_pipeline(filename, resume_id)


# Example usage
if __name__ == "__main__":
    import sys
    
    # Test with your existing file
    test_filename = "kunal_passan.pdf"  # Change to your test file
    test_resume_id = "kunal_passan"
    
    print(f"\n{'*'*60}")
    print(f"TESTING AGENTIC PIPELINE CONTROLLER")
    print(f"{'*'*60}\n")
    
    result = run_pipeline(test_filename, test_resume_id)
    
    print(f"\n{'*'*60}")
    print(f"FINAL RESULT")
    print(f"{'*'*60}")
    print(f"Status: {result.get('status')}")
    print(f"Message: {result.get('message')}")
    print(f"Chunks: {result.get('chunks', 'N/A')}")
    print(f"\nAgent Summary:")
    print(result.get('agent_summary', 'N/A'))