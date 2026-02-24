"""
State Management for AI Research Agent
Defines the state structure and types used throughout the agent workflow
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ThoughtType(str, Enum):
    """Enum for different types of thoughts in the thinking log"""
    PLANNING = "planning"
    SEARCHING = "searching"
    ANALYZING = "analyzing"
    REASONING = "reasoning"
    DECIDING = "deciding"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    ERROR = "error"

class Thought(TypedDict):
    """Structure for each thought entry in the thinking log"""
    type: ThoughtType
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]]

class ResearchState(TypedDict):
    """Main state structure for the research agent"""
    # Query and planning
    query: str
    research_plan: List[str]
    current_step: int
    
    # Search related
    search_queries: List[str]
    search_results: List[Dict[str, Any]]
    
    # Results
    final_answer: Optional[str]
    
    # Thinking log
    thoughts: List[Thought]
    
    # Control flow
    iteration_count: int
    max_iterations: int
    status: str  # "planning", "researching", "analyzing", "completed", "failed"

def create_initial_state(query: str) -> ResearchState:
    """
    Helper function to create an initial state with default values
    
    Args:
        query: The research query to investigate
        
    Returns:
        ResearchState: Initialized state dictionary
    """
    return {
        "query": query,
        "research_plan": [],
        "current_step": 0,
        "search_queries": [],
        "search_results": [],
        "final_answer": None,
        "thoughts": [],
        "iteration_count": 0,
        "max_iterations": 3,
        "status": "planning"
    }

def add_thought(state: ResearchState, thought_type: ThoughtType, 
                content: str, metadata: Dict[str, Any] = None) -> ResearchState:
    """
    Helper function to add a thought to the thinking log
    
    Args:
        state: Current research state
        thought_type: Type of thought
        content: Thought content
        metadata: Additional metadata
        
    Returns:
        ResearchState: Updated state with new thought
    """
    thought = Thought(
        type=thought_type,
        content=content,
        timestamp=datetime.now().isoformat(),
        metadata=metadata or {}
    )
    
    # Create a new thoughts list to avoid mutation issues
    updated_thoughts = state["thoughts"].copy()
    updated_thoughts.append(thought)
    
    # Return updated state
    return {
        **state,
        "thoughts": updated_thoughts
    }

def get_thoughts_summary(state: ResearchState) -> str:
    """
    Get a formatted summary of all thoughts
    
    Args:
        state: Current research state
        
    Returns:
        str: Formatted thought summary
    """
    if not state["thoughts"]:
        return "No thoughts recorded yet."
    
    summary = "\n=== THINKING LOG ===\n"
    for i, thought in enumerate(state["thoughts"], 1):
        timestamp = thought["timestamp"][11:19]  # Extract HH:MM:SS
        thought_type = thought["type"].value if hasattr(thought["type"], 'value') else thought["type"]
        summary += f"{i}. [{timestamp}] {thought_type.upper()}: {thought['content']}\n"
        
        # Add metadata if present
        if thought.get("metadata"):
            for key, value in thought["metadata"].items():
                if value and key not in ["error"]:
                    summary += f"   └─ {key}: {value}\n"
    
    return summary

# Simple test to verify the file works
if __name__ == "__main__":
    print("🔧 Testing state.py...")
    
    # Test 1: Create initial state
    state = create_initial_state("What is LangGraph?")
    print("✅ create_initial_state() works")
    
    # Test 2: Add a thought
    state = add_thought(
        state, 
        ThoughtType.PLANNING, 
        "Testing the state management",
        {"test": True}
    )
    print("✅ add_thought() works")
    
    # Test 3: Get summary
    summary = get_thoughts_summary(state)
    print("✅ get_thoughts_summary() works")
    print(summary)
    
    print("\n🎉 state.py is ready to use!")