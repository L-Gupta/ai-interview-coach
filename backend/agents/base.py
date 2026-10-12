"""
Base tools and utilities for all agents
"""
from langchain_classic.tools import Tool
from typing import Callable, List, Any, Dict
from pydantic import BaseModel, Field

class AgentTool(BaseModel):
    """Enhanced tool with metadata for agent decision-making"""
    name: str
    description: str
    func: Callable
    requires_context: List[str] = Field(default_factory=list)
    produces: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True
    
    def to_langchain_tool(self) -> Tool:
        """Convert to LangChain Tool format"""
        return Tool(
            name=self.name,
            description=self.description,
            func=self.func
        )

class AgentMemory:
    """Shared memory across all agents"""
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.analysis_results: Dict[str, Any] = {}
        self.integrity_flags: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
    
    def add_qa_pair(self, question: str, answer: str):
        """Add question-answer pair to memory"""
        self.conversation_history.append({
            "question": question,
            "answer": answer
        })
    
    def add_analysis(self, analysis_type: str, data: Any):
        """Add analysis result"""
        self.analysis_results[analysis_type] = data
    
    def add_integrity_flag(self, flag: Dict[str, Any]):
        """Add integrity violation"""
        self.integrity_flags.append(flag)
    
    def get_context_summary(self) -> str:
        """Get formatted summary of current context"""
        summary = []
        summary.append(f"Questions asked: {len(self.conversation_history)}")
        summary.append(f"Analyses completed: {list(self.analysis_results.keys())}")
        summary.append(f"Integrity flags: {len(self.integrity_flags)}")
        return "\n".join(summary)