"""
Master Orchestrator - Coordinates all agents using LangGraph
Manages the interview flow and agent interactions
"""
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from agents.interviewer_agent import InterviewerAgent
from agents.integrity_agent import IntegrityAgent
from agents.video_analysis_agent import VideoAnalysisAgent
from agents.audio_analysis_agent import AudioAnalysisAgent
from agents.base import AgentMemory
import operator

# Define the state that flows through the graph
class InterviewState(TypedDict):
    """State object that flows through the agent graph"""
    session_id: str
    resume_id: str
    job_role: str
    current_question: int
    total_questions: int
    
    # Data collected
    questions: list
    answers: list
    audio_analyses: list
    video_analyses: list
    integrity_reports: list
    
    # Agent memory
    memory: dict
    
    # Control flow
    next_action: str
    interview_complete: bool

class InterviewOrchestrator:
    """
    Master orchestrator that coordinates all agents
    Uses LangGraph for state management and agent coordination
    """
    
    def __init__(self, session_id: str, resume_id: str, job_role: str):
        self.session_id = session_id
        self.resume_id = resume_id
        self.job_role = job_role
        
        # Initialize shared memory
        self.memory = AgentMemory()
        
        # Initialize agents
        self.interviewer_agent = InterviewerAgent(resume_id, job_role, self.memory)
        self.integrity_agent = IntegrityAgent()
        self.video_agent = VideoAnalysisAgent()
        self.audio_agent = AudioAnalysisAgent()
        
        # Build the state graph
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    def _build_workflow(self) -> StateGraph:
        """Build LangGraph workflow for interview process"""
        
        workflow = StateGraph(InterviewState)
        
        # Define nodes (agent actions)
        workflow.add_node("generate_question", self._generate_question_node)
        workflow.add_node("wait_for_answer", self._wait_for_answer_node)
        workflow.add_node("analyze_audio", self._analyze_audio_node)
        workflow.add_node("analyze_video", self._analyze_video_node)
        workflow.add_node("check_integrity", self._check_integrity_node)
        workflow.add_node("decide_next", self._decide_next_node)
        workflow.add_node("finalize", self._finalize_node)
        
        # Define edges (workflow)
        workflow.set_entry_point("generate_question")
        workflow.add_edge("generate_question", "wait_for_answer")
        workflow.add_edge("wait_for_answer", "analyze_audio")
        workflow.add_edge("analyze_audio", "analyze_video")
        workflow.add_edge("analyze_video", "check_integrity")
        workflow.add_edge("check_integrity", "decide_next")
        
        # Conditional edge: continue or finalize
        workflow.add_conditional_edges(
            "decide_next",
            self._should_continue,
            {
                "continue": "generate_question",
                "finalize": "finalize"
            }
        )
        
        workflow.add_edge("finalize", END)
        
        return workflow
    
    def _generate_question_node(self, state: InterviewState) -> InterviewState:
        """Node: Generate next interview question"""
        print(f"\n[ORCHESTRATOR] Generating question {state['current_question'] + 1}")
        
        question = self.interviewer_agent.generate_next_question()
        
        state["questions"].append(question)
        state["current_question"] += 1
        state["next_action"] = "wait_for_answer"
        
        return state
    
    def _wait_for_answer_node(self, state: InterviewState) -> InterviewState:
        """Node: Wait for user to submit answer (handled externally)"""
        # This is a placeholder - actual waiting happens in the API
        state["next_action"] = "analyze_audio"
        return state
    
    def _analyze_audio_node(self, state: InterviewState) -> InterviewState:
        """Node: Analyze audio of the answer"""
        print(f"[ORCHESTRATOR] Analyzing audio for question {state['current_question']}")
        
        # Get the latest audio file path from state (set by API)
        audio_path = state.get("latest_audio_path")
        
        if audio_path:
            audio_analysis = self.audio_agent.analyze_audio(audio_path)
            state["audio_analyses"].append(audio_analysis)
            self.memory.add_analysis("audio", audio_analysis)
        
        state["next_action"] = "analyze_video"
        return state
    
    def _analyze_video_node(self, state: InterviewState) -> InterviewState:
        """Node: Analyze video of the answer"""
        print(f"[ORCHESTRATOR] Analyzing video for question {state['current_question']}")
        
        video_path = state.get("latest_video_path")
        
        if video_path:
            video_analysis = self.video_agent.analyze_video(video_path)
            state["video_analyses"].append(video_analysis)
            self.memory.add_analysis("video", video_analysis)
        
        state["next_action"] = "check_integrity"
        return state
    
    def _check_integrity_node(self, state: InterviewState) -> InterviewState:
        """Node: Check for integrity violations"""
        print(f"[ORCHESTRATOR] Checking integrity for question {state['current_question']}")
        
        video_path = state.get("latest_video_path")
        
        if video_path:
            integrity_report = self.integrity_agent.analyze_video(video_path)
            state["integrity_reports"].append(integrity_report)
            
            # Add violations to memory
            if integrity_report.get("severity") in ["high", "critical"]:
                self.memory.add_integrity_flag({
                    "question": state['current_question'],
                    "severity": integrity_report["severity"],
                    "violations": integrity_report["violations_summary"]
                })
        
        state["next_action"] = "decide_next"
        return state
    
    def _decide_next_node(self, state: InterviewState) -> InterviewState:
        """Node: Decide whether to continue or finalize interview"""
        print(f"[ORCHESTRATOR] Deciding next action...")
        
        # Check if interview should continue
        is_complete = self.interviewer_agent.is_interview_complete()
        state["interview_complete"] = is_complete
        
        if is_complete:
            state["next_action"] = "finalize"
        else:
            state["next_action"] = "generate_question"
        
        return state
    
    def _finalize_node(self, state: InterviewState) -> InterviewState:
        """Node: Finalize interview and prepare for report generation"""
        print(f"[ORCHESTRATOR] Finalizing interview...")
        state["next_action"] = "end"
        return state
    
    def _should_continue(self, state: InterviewState) -> str:
        """Determine if interview should continue or finalize"""
        if state.get("interview_complete", False):
            return "finalize"
        return "continue"
    
    def get_current_question(self) -> str:
        """Get the current question to ask"""
        return self.interviewer_agent.generate_next_question()
    
    def process_answer(self, question: str, answer: str, audio_path: str = None, video_path: str = None) -> dict:
        """
        Process a submitted answer through all analysis agents
        """
        # Add to memory
        self.memory.add_qa_pair(question, answer)
        
        # Prepare state
        state = {
            "session_id": self.session_id,
            "resume_id": self.resume_id,
            "job_role": self.job_role,
            "current_question": len(self.memory.conversation_history),
            "total_questions": 5,
            "questions": [qa["question"] for qa in self.memory.conversation_history],
            "answers": [qa["answer"] for qa in self.memory.conversation_history],
            "audio_analyses": [],
            "video_analyses": [],
            "integrity_reports": [],
            "memory": {},
            "next_action": "analyze_audio",
            "interview_complete": False,
            "latest_audio_path": audio_path,
            "latest_video_path": video_path
        }
        
        # Run analysis pipeline
        audio_result = {}
        video_result = {}
        integrity_result = {}
        
        if audio_path:
            audio_result = self.audio_agent.analyze_audio(audio_path)
            self.memory.add_analysis(f"audio_q{len(self.memory.conversation_history)}", audio_result)
        
        if video_path:
            video_result = self.video_agent.analyze_video(video_path)
            integrity_result = self.integrity_agent.analyze_video(video_path)
            self.memory.add_analysis(f"video_q{len(self.memory.conversation_history)}", video_result)
            
            if integrity_result.get("severity") in ["medium", "high", "critical"]:
                self.memory.add_integrity_flag({
                    "question": len(self.memory.conversation_history),
                    "severity": integrity_result["severity"],
                    "violations": integrity_result["violations_summary"]
                })
        
        return {
            "audio_analysis": audio_result,
            "video_analysis": video_result,
            "integrity_check": integrity_result
        }
    
    def is_interview_complete(self) -> bool:
        """Check if interview is complete"""
        return self.interviewer_agent.is_interview_complete()
    
    def get_memory_summary(self) -> dict:
        """Get summary of collected data"""
        return {
            "total_questions": len(self.memory.conversation_history),
            "audio_analyses": len([k for k in self.memory.analysis_results.keys() if k.startswith("audio")]),
            "video_analyses": len([k for k in self.memory.analysis_results.keys() if k.startswith("video")]),
            "integrity_flags": len(self.memory.integrity_flags),
            "conversation_history": self.memory.conversation_history,
            "all_analyses": self.memory.analysis_results,
            "all_violations": self.memory.integrity_flags
        }