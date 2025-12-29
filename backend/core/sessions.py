
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
    def __init__(self, persistence_file: str = "data/sessions.json"):
        self.persistence_file = persistence_file
        self._ensure_data_dir()
        self._sessions: Dict[str, SessionData] = self._load_sessions()

    def _ensure_data_dir(self):
        import os
        from pathlib import Path
        path = Path(self.persistence_file)
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

    def _load_sessions(self) -> Dict[str, SessionData]:
        import json
        from pathlib import Path
        path = Path(self.persistence_file)
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return {
                sid: SessionData(**s_data) 
                for sid, s_data in data.items()
            }
        except Exception as e:
            print(f"⚠️ Error loading sessions: {e}")
            return {}

    def _save_sessions(self):
        import json
        from pathlib import Path
        try:
            path = Path(self.persistence_file)
            data = {sid: s.model_dump() for sid, s in self._sessions.items()}
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"⚠️ Error saving sessions: {e}")

    def create_session(self, user_id: str = "default_user") -> SessionData:
        session_id = str(uuid.uuid4())
        session = SessionData(
            id=session_id,
            user_id=user_id,
            created_at=time.time(),
            messages=[]
        )
        self._sessions[session_id] = session
        self._save_sessions()
        return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        # Always reload to sync across processes (CLI vs API)
        self._sessions = self._load_sessions()
        return self._sessions.get(session_id)

    def list_sessions(self, user_id: Optional[str] = None) -> List[SessionData]:
        self._sessions = self._load_sessions()
        if user_id:
             return [s for s in self._sessions.values() if s.user_id == user_id]
        return list(self._sessions.values())

    def add_message(self, session_id: str, role: str, content: str):
        self._sessions = self._load_sessions()
        session = self.get_session(session_id) # Reloaded
        if session:
            msg = SessionMessage(role=role, content=content, timestamp=time.time())
            session.messages.append(msg)
            self._save_sessions()

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        session = self.get_session(session_id)
        if not session:
            return []
        
        # Convert to format expected by Agent (or similar)
        return [{"role": m.role, "content": m.content} for m in session.messages]

    def clear_session(self, session_id: str):
         self._sessions = self._load_sessions()
         if session_id in self._sessions:
             self._sessions[session_id].messages = []
             self._save_sessions()

# Singleton
session_manager = SessionManager()
