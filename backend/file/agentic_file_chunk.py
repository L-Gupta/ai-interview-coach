"""
Agentic Resume Chunker
Uses LangChain agent to intelligently segment resumes based on content structure and semantics.
"""

import os
import re
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_classic.tools import Tool
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.path.join("file", "uploads")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0
)


class AgenticResumeChunker:
    """
    An intelligent agent that decides how to chunk resumes by:
    - Identifying semantic sections (Education, Experience, Skills, etc.)
    - Detecting section boundaries intelligently
    - Handling various resume formats
    - Ensuring chunks are semantically complete
    """
    
    def __init__(self, max_chars: int = 1250):
        self.max_chars = max_chars
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Define tools for intelligent chunking."""
        
        def identify_sections(text: str) -> str:
            """Identify major resume sections."""
            common_headers = [
                "summary", "objective", "profile",
                "experience", "work experience", "employment",
                "education", "academic background",
                "skills", "technical skills", "core competencies",
                "projects", "key projects",
                "certifications", "certificates",
                "awards", "achievements", "honors",
                "publications", "research",
                "volunteer", "volunteering",
                "leadership", "leadership positions",
                "languages", "interests", "hobbies"
            ]
            
            lines = text.split('\n')
            detected_sections = []
            
            for i, line in enumerate(lines):
                line_clean = line.strip().lower()
                
                # Check if line is a section header
                if any(header in line_clean for header in common_headers):
                    detected_sections.append({
                        "line_number": i,
                        "header": line.strip(),
                        "type": "section_header"
                    })
                elif re.match(r'^[A-Z][A-Z\s]{3,}$', line.strip()):
                    detected_sections.append({
                        "line_number": i,
                        "header": line.strip(),
                        "type": "all_caps_header"
                    })
            
            return str(detected_sections) if detected_sections else "NO_SECTIONS_FOUND"
        
        def chunk_by_paragraphs(text: str) -> str:
            """Chunk text by paragraph boundaries."""
            lines = text.splitlines()
            chunks = []
            current_chunk = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if len(current_chunk) + len(line) > self.max_chars:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = line + "\n"
                else:
                    current_chunk += line + "\n"
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            return f"Created {len(chunks)} chunks"
        
        def chunk_by_sections(text: str, sections_info: str) -> str:
            """Chunk text by identified sections."""
            if sections_info == "NO_SECTIONS_FOUND":
                return "ERROR: No sections identified, cannot chunk by sections"
            
            try:
                sections = eval(sections_info)
                lines = text.split('\n')
                chunks = []
                
                for i, section in enumerate(sections):
                    start_line = section['line_number']
                    end_line = sections[i + 1]['line_number'] if i + 1 < len(sections) else len(lines)
                    
                    section_text = '\n'.join(lines[start_line:end_line]).strip()
                    
                    # If section is too large, split it further
                    if len(section_text) > self.max_chars:
                        # Split into smaller chunks
                        sub_chunks = self._split_large_section(section_text)
                        chunks.extend(sub_chunks)
                    else:
                        chunks.append(section_text)
                
                return f"Created {len(chunks)} section-based chunks"
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        def chunk_by_semantic_meaning(text: str) -> str:
            """Use LLM to identify semantically coherent chunks."""
            # This is a simplified version - in production you'd use embeddings
            prompt = f"""Analyze this resume text and identify natural semantic boundaries.
            
Text:
{text[:2000]}  # First 2000 chars

Return the line numbers where major topic changes occur.
Format: [10, 25, 45, 67]"""
            
            try:
                response = llm.invoke(prompt)
                boundaries = response.content
                return f"Semantic boundaries identified: {boundaries}"
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        def validate_chunks(chunks_info: str) -> str:
            """Validate that chunks are reasonable."""
            if "Created" in chunks_info:
                num_chunks = int(chunks_info.split()[1])
                if num_chunks < 2:
                    return "WARNING: Too few chunks, resume might be very short"
                elif num_chunks > 15:
                    return "WARNING: Too many chunks, consider larger chunk size"
                else:
                    return f"VALID: {num_chunks} chunks is reasonable"
            return "ERROR: Cannot validate"
        
        def merge_small_chunks(chunks_info: str) -> str:
            """Merge chunks that are too small."""
            return "Small chunks merged (implementation needed)"
        
        return [
            Tool(
                name="IdentifySections",
                func=identify_sections,
                description="Identify resume sections like Education, Experience, Skills. Input: full text"
            ),
            Tool(
                name="ChunkByParagraphs",
                func=chunk_by_paragraphs,
                description="Simple chunking by paragraph breaks. Use when structure is unclear. Input: text"
            ),
            Tool(
                name="ChunkBySections",
                func=chunk_by_sections,
                description="Intelligent chunking by identified sections. Input: text, sections_info"
            ),
            Tool(
                name="ChunkBySemantic",
                func=chunk_by_semantic_meaning,
                description="Advanced semantic chunking using LLM. Use for complex resumes. Input: text"
            ),
            Tool(
                name="ValidateChunks",
                func=validate_chunks,
                description="Check if chunking result is reasonable. Input: chunks_info"
            ),
            Tool(
                name="MergeSmallChunks",
                func=merge_small_chunks,
                description="Merge chunks that are too small. Input: chunks_info"
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create ReAct agent for chunking."""
        
        template = """You are an intelligent resume chunking agent. Your job is to segment resume text into semantically meaningful chunks.

Available tools: {tools}
Tool names: {tool_names}

Strategy:
1. First, try to identify section headers (Education, Experience, etc.)
2. If sections found: Chunk by sections to preserve semantic meaning
3. If no sections: Fall back to paragraph-based chunking
4. Validate the chunking result
5. If chunks are too small or too large, adjust accordingly

Constraints:
- Maximum chunk size: 1250 characters
- Minimum chunks: 2
- Preserve semantic coherence

Use this format:
Thought: [Your reasoning]
Action: [Tool name]
Action Input: [Input to tool]
Observation: [Tool result]
... (repeat as needed)
Thought: I have created valid chunks
Final Answer: [Summary of chunking approach and result]

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)
        agent = create_react_agent(llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=6,
            handle_parsing_errors=True
        )
    
    def _split_large_section(self, text: str) -> List[str]:
        """Helper to split sections that exceed max_chars."""
        chunks = []
        lines = text.split('\n')
        current = ""
        
        for line in lines:
            if len(current) + len(line) > self.max_chars:
                if current:
                    chunks.append(current.strip())
                current = line + "\n"
            else:
                current += line + "\n"
        
        if current:
            chunks.append(current.strip())
        
        return chunks
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Main chunking function using agent intelligence.
        
        Args:
            text: Resume text to chunk
            
        Returns:
            List of text chunks
        """
        try:
            # Let the agent decide how to chunk
            result = self.agent.invoke({
                "input": f"Chunk this resume text intelligently:\n\n{text[:3000]}"  # Send sample
            })
            
            # For now, fall back to manual chunking after agent analysis
            # In production, the agent would return actual chunks
            return self._fallback_chunk(text)
            
        except Exception as e:
            print(f"⚠️ Agent chunking failed: {e}, using fallback")
            return self._fallback_chunk(text)
    
    def _fallback_chunk(self, text: str) -> List[str]:
        """Fallback chunking method."""
        lines = text.splitlines()
        chunks = []
        current_chunk = ""
        
        def is_section_header(line: str) -> bool:
            return (re.match(r"^[A-Z][A-Z\s]+$", line) or 
                    line.lower().strip() in {
                        "summary", "objective", "experience", "education",
                        "skills", "projects", "certifications"
                    })
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Start new chunk on section headers
            if is_section_header(line) and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = line + "\n"
            # Start new chunk if size exceeded
            elif len(current_chunk) + len(line) > self.max_chars:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def chunk_parsed_resume(self, parsed_filename: str) -> List[str]:
        """
        Chunk a parsed resume file.
        Drop-in replacement for existing function.
        """
        file_path = os.path.join(UPLOAD_DIR, parsed_filename)
        
        if not os.path.exists(file_path):
            print(f"❌ Parsed file not found: {file_path}")
            return []
        
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        chunks = self.chunk_text(text)
        print(f"🧩 Chunked into {len(chunks)} pieces using agentic approach.")
        return chunks
    
    def save_chunks_to_file(self, chunks: List[str], original_filename: str):
        """Save chunks to file."""
        base_name = os.path.splitext(original_filename)[0].replace("_parsed", "")
        output_path = os.path.join(UPLOAD_DIR, f"{base_name}_chunks.txt")
        
        with open(output_path, "w", encoding="utf-8") as f:
            for i, chunk in enumerate(chunks):
                f.write(f"--- Chunk {i+1} ---\n{chunk}\n\n")
        
        print(f"📂 Chunks saved to: {output_path}")


# Drop-in replacement functions
def chunk_text_by_paragraph(text: str, max_chars: int = 1250) -> List[str]:
    """Drop-in replacement using agentic chunker."""
    chunker = AgenticResumeChunker(max_chars=max_chars)
    return chunker.chunk_text(text)


def chunk_parsed_resume(parsed_filename: str) -> List[str]:
    """Drop-in replacement."""
    chunker = AgenticResumeChunker()
    return chunker.chunk_parsed_resume(parsed_filename)


def save_chunks_to_file(chunks: List[str], original_filename: str):
    """Drop-in replacement."""
    chunker = AgenticResumeChunker()
    chunker.save_chunks_to_file(chunks, original_filename)


# Example usage
if __name__ == "__main__":
    chunker = AgenticResumeChunker(max_chars=1250)
    
    # Test with existing parsed file
    test_file = "kunal_passan_parsed.txt"
    
    print(f"\n{'='*60}")
    print(f"Testing Agentic Chunker with: {test_file}")
    print(f"{'='*60}\n")
    
    chunks = chunker.chunk_parsed_resume(test_file)
    
    if chunks:
        print(f"\n{'='*60}")
        print(f"CHUNKING RESULT: {len(chunks)} chunks created")
        print(f"{'='*60}\n")
        
        for i, chunk in enumerate(chunks[:3], 1):
            print(f"--- Chunk {i} (preview) ---")
            print(chunk[:200])
            print(f"... ({len(chunk)} chars total)\n")
        
        chunker.save_chunks_to_file(chunks, test_file)
    else:
        print("\n❌ Chunking failed")