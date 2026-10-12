"""
Agentic Resume Parser
Uses LangChain agent to intelligently parse resumes based on file type and content structure.
"""

import os
from typing import Optional, Dict, List
import fitz  # PyMuPDF
from docx import Document
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_classic.tools import Tool
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.path.join("file", "uploads")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0
)


class AgenticResumeParser:
    """
    An intelligent agent that decides how to parse resumes based on:
    - File format (PDF vs DOCX)
    - Content structure (formatted vs plain text)
    - Quality issues (corrupted, scanned images, etc.)
    """
    
    def __init__(self):
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        
    def _create_tools(self) -> List[Tool]:
        """Define tools the agent can use for parsing."""
        
        def parse_pdf_text(filepath: str) -> str:
            """Extract text from PDF using PyMuPDF."""
            try:
                doc = fitz.open(filepath)
                text = "\n".join([page.get_text() for page in doc])
                doc.close()
                return text.strip() if text.strip() else "NO_TEXT_FOUND"
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        def parse_pdf_advanced(filepath: str) -> str:
            """Extract text with layout analysis from PDF."""
            try:
                doc = fitz.open(filepath)
                text_blocks = []
                for page in doc:
                    blocks = page.get_text("dict")["blocks"]
                    for block in blocks:
                        if "lines" in block:
                            for line in block["lines"]:
                                for span in line["spans"]:
                                    text_blocks.append({
                                        "text": span["text"],
                                        "size": span["size"],
                                        "font": span["font"]
                                    })
                doc.close()
                
                # Reconstruct with formatting hints
                formatted = []
                for block in text_blocks:
                    if block["size"] > 12:  # Likely a header
                        formatted.append(f"\n### {block['text']}")
                    else:
                        formatted.append(block['text'])
                
                return "\n".join(formatted)
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        def parse_docx_simple(filepath: str) -> str:
            """Extract plain text from DOCX."""
            try:
                doc = Document(filepath)
                return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        def parse_docx_styled(filepath: str) -> str:
            """Extract text with style information from DOCX."""
            try:
                doc = Document(filepath)
                styled_text = []
                for para in doc.paragraphs:
                    if para.text.strip():
                        if para.style.name.startswith('Heading'):
                            styled_text.append(f"\n### {para.text}")
                        elif para.runs and para.runs[0].bold:
                            styled_text.append(f"\n**{para.text}**")
                        else:
                            styled_text.append(para.text)
                return "\n".join(styled_text)
            except Exception as e:
                return f"ERROR: {str(e)}"
        
        def check_file_type(filepath: str) -> str:
            """Determine file type and characteristics."""
            if not os.path.exists(filepath):
                return "ERROR: File not found"
            
            ext = os.path.splitext(filepath)[1].lower()
            size = os.path.getsize(filepath)
            
            info = f"Extension: {ext}\nSize: {size} bytes"
            
            if ext == ".pdf":
                try:
                    doc = fitz.open(filepath)
                    page_count = len(doc)
                    first_page = doc[0]
                    text_sample = first_page.get_text()[:200]
                    doc.close()
                    info += f"\nPages: {page_count}\nSample text: {text_sample}"
                except:
                    info += "\nPDF appears corrupted or image-based"
            
            return info
        
        def ocr_fallback(filepath: str) -> str:
            """Fallback OCR for scanned PDFs (mock implementation)."""
            # In production, you'd use pytesseract or similar
            return "OCR_NOT_IMPLEMENTED: This would use Tesseract for scanned documents"
        
        return [
            Tool(
                name="CheckFileType",
                func=check_file_type,
                description="Use this first to understand the file format, size, and characteristics. Input: filepath"
            ),
            Tool(
                name="ParsePDFSimple",
                func=parse_pdf_text,
                description="Extract plain text from PDF. Use for standard PDFs. Input: filepath"
            ),
            Tool(
                name="ParsePDFAdvanced",
                func=parse_pdf_advanced,
                description="Extract text with formatting hints from PDF. Use when simple parsing loses structure. Input: filepath"
            ),
            Tool(
                name="ParseDOCXSimple",
                func=parse_docx_simple,
                description="Extract plain text from Word document. Use for standard DOCX files. Input: filepath"
            ),
            Tool(
                name="ParseDOCXStyled",
                func=parse_docx_styled,
                description="Extract text preserving styles from DOCX. Use when formatting matters. Input: filepath"
            ),
            Tool(
                name="OCRFallback",
                func=ocr_fallback,
                description="Use OCR on scanned/image PDFs when text extraction fails. Input: filepath"
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create the ReAct agent with parsing tools."""
        
        template = """You are an intelligent resume parsing agent. Your job is to extract text from resume files efficiently.

Available tools: {tools}
Tool names: {tool_names}

Strategy:
1. ALWAYS start by checking the file type and characteristics
2. Choose the appropriate parsing method based on what you find:
   - For PDFs: Try simple parsing first, use advanced if structure is lost
   - For DOCX: Use styled parsing to preserve headers/sections
   - If text extraction fails: Consider OCR fallback
3. Verify the output has reasonable content
4. Return the parsed text

Use this format:
Thought: [Your reasoning about what to do next]
Action: [Tool name to use]
Action Input: [Input to the tool]
Observation: [Result from the tool]
... (repeat Thought/Action/Observation as needed)
Thought: I now have the parsed text
Final Answer: [The extracted text]

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)
        
        agent = create_react_agent(llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    def parse_resume(self, filename: str) -> Optional[str]:
        """
        Main entry point - agent decides how to parse the file.
        
        Args:
            filename: Name of the file in UPLOAD_DIR
            
        Returns:
            Extracted text or None if parsing failed
        """
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"❌ File not found: {filepath}")
            return None
        
        try:
            result = self.agent.invoke({
                "input": f"Parse the resume at {filepath} and extract all text content. Be intelligent about the parsing method."
            })
            
            parsed_text = result.get("output", "")
            
            # Validate output
            if len(parsed_text) < 50:
                print("⚠️ Parsed text seems too short, might be an error")
                return None
            
            return parsed_text
            
        except Exception as e:
            print(f"❌ Agent parsing failed: {e}")
            return None
    
    def save_parsed_text(self, text: str, original_filename: str):
        """Save parsed text to file."""
        base_name = os.path.splitext(original_filename)[0]
        output_path = os.path.join(UPLOAD_DIR, f"{base_name}_parsed.txt")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"📄 Parsed text saved to: {output_path}")


# Convenience function for existing codebase
def parse_resume(filename: str) -> Optional[str]:
    """
    Parse a resume file using an intelligent agent.
    Drop-in replacement for your existing parse_resume function.
    """
    parser = AgenticResumeParser()
    return parser.parse_resume(filename)


def save_parsed_text_to_file(text: str, original_filename: str):
    """Save parsed text - drop-in replacement."""
    parser = AgenticResumeParser()
    parser.save_parsed_text(text, original_filename)


# Example usage
if __name__ == "__main__":
    # Test with your existing files
    parser = AgenticResumeParser()
    
    test_file = "kunal_passan.pdf"  # Change to your test file
    
    print(f"\n{'='*60}")
    print(f"Testing Agentic Parser with: {test_file}")
    print(f"{'='*60}\n")
    
    parsed = parser.parse_resume(test_file)
    
    if parsed:
        print(f"\n{'='*60}")
        print("PARSED OUTPUT (first 500 chars):")
        print(f"{'='*60}")
        print(parsed[:500])
        print(f"\n... (total {len(parsed)} characters)")
        
        parser.save_parsed_text(parsed, test_file)
    else:
        print("\n❌ Parsing failed")