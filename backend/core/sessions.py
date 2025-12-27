
import uuid
import time
from typing import Dict, List, Optional
from pydantic import BaseModel

class SessionMessage(BaseModel):
    role: str
    content: str
    timestamp: float = 0.0

class SessionData(BaseModel):
    id: str
    user_id: str
    created_at: float
    messages: List[SessionMessage] = []
    
class SessionManager:
    """
    Manages chat sessions and history.
    Currently In-Memory. In production, swap with Redis/Postgres.
    """
    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}

    def create_session(self, user_id: str = "default_user") -> SessionData:
        session_id = str(uuid.uuid4())
        session = SessionData(
            id=session_id,
            user_id=user_id,
            created_at=time.time(),
            messages=[]
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        return self._sessions.get(session_id)

    def list_sessions(self, user_id: Optional[str] = None) -> List[SessionData]:
        if user_id:
             return [s for s in self._sessions.values() if s.user_id == user_id]
        return list(self._sessions.values())

    def add_message(self, session_id: str, role: str, content: str):
        session = self.get_session(session_id)
        if session:
            msg = SessionMessage(role=role, content=content, timestamp=time.time())
            session.messages.append(msg)

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        session = self.get_session(session_id)
        if not session:
            return []
        
        # Convert to format expected by Agent (or similar)
        return [{"role": m.role, "content": m.content} for m in session.messages]

    def clear_session(self, session_id: str):
         if session_id in self._sessions:
             self._sessions[session_id].messages = []

# Singleton
session_manager = SessionManager()
