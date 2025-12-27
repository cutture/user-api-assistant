
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import time

try:
    from backend.core.sessions import session_manager, SessionData
    from backend.agent.graph import app_graph
    from backend.utils.sanitization import sanitize_html
except ImportError:
    # Fallback for direct execution
    from core.sessions import session_manager, SessionData
    from agent.graph import app_graph
    from utils.sanitization import sanitize_html

from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter(prefix="/sessions", tags=["sessions"])

# --- Models ---
class CreateSessionRequest(BaseModel):
    user_id: str = "default_user"

class ChatMessageData(BaseModel):
    role: str
    content: str
    timestamp: float

class SessionResponse(BaseModel):
    id: str
    user_id: str
    created_at: float
    message_count: int

class SessionChatRequest(BaseModel):
    query: str

class SessionChatResponse(BaseModel):
    response: str
    plan: Optional[str] = None

# --- Endpoints ---

@router.post("/", response_model=SessionResponse)
async def create_new_session(req: CreateSessionRequest):
    session = session_manager.create_session(req.user_id)
    return SessionResponse(
        id=session.id,
        user_id=session.user_id,
        created_at=session.created_at,
        message_count=0
    )

@router.get("/", response_model=List[SessionResponse])
async def list_sessions(user_id: Optional[str] = None):
    sessions = session_manager.list_sessions(user_id)
    # Sort by created_at desc
    sessions.sort(key=lambda x: x.created_at, reverse=True)
    return [
        SessionResponse(
            id=s.id, user_id=s.user_id, created_at=s.created_at, message_count=len(s.messages)
        ) for s in sessions
    ]

@router.get("/{session_id}/history", response_model=List[ChatMessageData])
async def get_session_history(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return [
        ChatMessageData(role=m.role, content=m.content, timestamp=m.timestamp) 
        for m in session.messages
    ]

@router.post("/{session_id}/chat", response_model=SessionChatResponse)
async def chat_in_session(session_id: str, req: SessionChatRequest):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    query = req.query
    
    # 1. Add User Msg to History
    session_manager.add_message(session_id, "user", query)
    
    # 2. Build LangChain Messages from History
    # Note: We rely on SessionManager to keep full history, 
    # but for context window limits, we might want to slice it inside agent or here.
    # For now, let's pass smart history or full history.
    
    history_msgs = []
    for m in session.messages:
        if m.role == "user":
            history_msgs.append(HumanMessage(content=sanitize_html(m.content)))
        else:
            history_msgs.append(AIMessage(content=sanitize_html(m.content)))
            
    # The agent expects a list of messages. The last one should be the user's latest query
    # But since we just added it to history_msgs, we are good.
    # Actually Agent inputs usually distinguish 'messages' (conversation).
    
    inputs = {
        "messages": history_msgs,
        "intent": "general",
        "context": [],
        "plan": "",
        "generated_code": "",
        "error": ""
    }
    
    try:
        # 3. Invoke Agent
        result = app_graph.invoke(inputs)
        
        response_content = result.get("generated_code", "")
        plan_content = result.get("plan", "")
        
        # Fallback logic similar to main.py
        if not response_content:
             if "STATUS: INCOMPLETE" in plan_content:
                 response_content = f"Clarification Needed:\n{plan_content}"
             else:
                 response_content = "No code generated."

        # 4. Add Assistant Msg to History
        session_manager.add_message(session_id, "assistant", response_content)
        
        return SessionChatResponse(response=response_content, plan=plan_content)
        
    except Exception as e:
        # Log error in session? Maybe. Be careful of loops.
        msg = f"Error: {str(e)}"
        session_manager.add_message(session_id, "assistant", msg)
        raise HTTPException(status_code=500, detail=str(e))
