"""
Interviewer Agent - Responsible for generating adaptive interview questions
Uses ReAct pattern to decide which questions to ask based on:
- Resume content (via RAG)
- Previous answers
- Detected gaps or inconsistencies
- Job role requirements
"""
import os
import requests
from typing import Dict, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain_classic.tools import Tool
from pinecone import Pinecone
from core.config import settings
from agents.base import AgentMemory

class InterviewerAgent:
    def __init__(self, resume_id: str, job_role: str, memory: AgentMemory):
        self.resume_id = resume_id
        self.job_role = job_role
        self.memory = memory
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-1.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7
        )
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        
        # Initialize tools
        self.tools = self._create_tools()
        self.agent_executor = self._create_agent()
        
        # Question generation goals
        self.goals = [
            "Assess technical skills relevant to role",
            "Evaluate communication clarity",
            "Test problem-solving approach",
            "Verify resume claims",
            "Understand motivation and culture fit"
        ]
        self.completed_goals = set()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the interviewer agent"""
        
        def get_resume_context(query: str) -> str:
            """Fetch relevant resume chunks based on query"""
            embedding = self._embed_text(query)
            results = self.index.query(
                vector=embedding,
                top_k=3,
                namespace=self.resume_id,
                include_metadata=True
            )
            chunks = [match['metadata']['text'] for match in results['matches']]
            return "\n\n".join(chunks)
        
        def get_conversation_history() -> str:
            """Get formatted conversation history"""
            if not self.memory.conversation_history:
                return "No previous questions asked yet."
            history = []
            for i, qa in enumerate(self.memory.conversation_history, 1):
                history.append(f"Q{i}: {qa['question']}\nA{i}: {qa['answer']}")
            return "\n\n".join(history)
        
        def check_for_inconsistencies() -> str:
            """Check if previous answers show inconsistencies"""
            if len(self.memory.conversation_history) < 2:
                return "Not enough data to check inconsistencies."
            
            # Simple heuristic: check if answer mentions different experience levels
            answers = [qa['answer'] for qa in self.memory.conversation_history]
            combined = " ".join(answers).lower()
            
            flags = []
            if "beginner" in combined and "expert" in combined:
                flags.append("Conflicting skill levels mentioned")
            if "never" in combined and "always" in combined:
                flags.append("Contradictory absolute statements")
            
            return ", ".join(flags) if flags else "No obvious inconsistencies detected."
        
        def assess_coverage() -> str:
            """Assess which goals have been covered"""
            if not self.memory.conversation_history:
                return "No goals covered yet."
            
            coverage = []
            for goal in self.goals:
                if goal.lower() in str(self.memory.conversation_history).lower():
                    coverage.append(f"✓ {goal}")
                else:
                    coverage.append(f"✗ {goal}")
            
            return "\n".join(coverage)
        
        return [
            Tool(
                name="GetResumeContext",
                func=get_resume_context,
                description="Fetch relevant sections from candidate's resume. Input should be a query about skills, experience, or projects."
            ),
            Tool(
                name="GetConversationHistory",
                func=get_conversation_history,
                description="Get all previous questions and answers in this interview. Use to avoid repetition and build on previous topics."
            ),
            Tool(
                name="CheckInconsistencies",
                func=check_for_inconsistencies,
                description="Detect potential inconsistencies in candidate's answers. Use when you notice conflicting statements."
            ),
            Tool(
                name="AssessCoverage",
                func=assess_coverage,
                description="Check which interview goals have been addressed. Use to decide what to focus on next."
            )
        ]
    
    def _embed_text(self, text: str) -> List[float]:
        """Embed text using Gemini API"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/embedding-001:embedContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "model": "models/embedding-001",
            "content": {"parts": [{"text": text}]}
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["embedding"]["values"]
    
    def _create_agent(self) -> AgentExecutor:
        """Create ReAct agent with prompt template"""
        template = """You are an expert technical interviewer conducting an interview for a {job_role} position.

Your goals:
{goals}

Available tools:
{tools}

Tool names: {tool_names}

Current interview context:
{context_summary}

Instructions:
1. Think step-by-step about what information you need
2. Use tools to gather context before asking questions
3. Generate questions that are:
   - Relevant to the job role
   - Based on the candidate's resume
   - Build on previous answers
   - Test specific skills or claims
4. Avoid repetitive or generic questions
5. If you detect inconsistencies, probe deeper
6. Return ONLY the next question text, no explanation or preamble

Question: {input}

Thought: {agent_scratchpad}"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["job_role", "goals", "tools", "tool_names", "context_summary", "input", "agent_scratchpad"]
        )
        
        agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    def generate_next_question(self) -> str:
        """Generate the next interview question using the agent"""
        context = self.memory.get_context_summary()
        goals_str = "\n".join([f"- {g}" for g in self.goals])
        
        result = self.agent_executor.invoke({
            "job_role": self.job_role,
            "goals": goals_str,
            "context_summary": context,
            "input": "Generate the next interview question"
        })
        
        question = result.get("output", "").strip()
        
        # Fallback if agent fails
        if not question or len(question) < 10:
            question = self._fallback_question()
        
        return question
    
    def _fallback_question(self) -> str:
        """Fallback questions if agent fails"""
        fallbacks = [
            f"Can you describe your experience with technologies relevant to {self.job_role}?",
            "Tell me about a challenging project you worked on and how you approached it.",
            "How do you stay updated with new developments in your field?",
            "Describe a situation where you had to solve a complex technical problem.",
            "What interests you most about this role?"
        ]
        idx = len(self.memory.conversation_history) % len(fallbacks)
        return fallbacks[idx]
    
    def is_interview_complete(self) -> bool:
        """Determine if enough questions have been asked"""
        # Complete after 5 questions or when key goals are covered
        if len(self.memory.conversation_history) >= 5:
            return True
        
        # Check if critical goals are met
        critical_goals = ["technical skills", "problem-solving", "verify resume"]
        covered = sum(1 for goal in critical_goals 
                     if any(goal.lower() in str(qa).lower() 
                           for qa in self.memory.conversation_history))
        
        return covered >= 2 and len(self.memory.conversation_history) >= 3