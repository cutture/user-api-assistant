from typing import TypedDict, Annotated, List, Dict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    The shared state of the Agentic Mesh.
    """
    # Chat History (Accumulates messages)
    messages: Annotated[List[BaseMessage], add_messages]
    
    # User's Intent (e.g., "Documentation", "Code Generation", "Explanation")
    intent: str
    
    # Retrieved Documents from Vector Store
    # List of strings or dicts containing snippets
    context: List[str]
    
    # The final planned approach
    plan: str
    
    # The generated code snippet
    generated_code: str
    
    # Error state (if compilation/validation fails)
    error: str

    # Self-Correction State
    feedback: str # Critique from the validator
    attempt_count: int # Number of retries
