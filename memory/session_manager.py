"""Session Manager - Tracks conversation sessions."""
from typing import Dict, List, Optional
from datetime import datetime


class SessionManager:
    """Manages conversation sessions for continuity."""
    
    def __init__(self):
        """Initialize session manager."""
        self.sessions = {}  # session_id -> session_data
    
    def create_session(self, session_id: str, household_id: str):
        """Create a new session."""
        self.sessions[session_id] = {
            "session_id": session_id,
            "household_id": household_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "context": {}
        }
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session."""
        if session_id in self.sessions:
            self.sessions[session_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
    
    def update_context(self, session_id: str, context: Dict):
        """Update session context."""
        if session_id in self.sessions:
            self.sessions[session_id]["context"].update(context)
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data."""
        return self.sessions.get(session_id)
    
    def get_context(self, session_id: str) -> Dict:
        """Get session context."""
        if session_id in self.sessions:
            return self.sessions[session_id]["context"]
        return {}
    
    def get_messages(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent messages."""
        if session_id in self.sessions:
            messages = self.sessions[session_id]["messages"]
            return messages[-limit:] if len(messages) > limit else messages
        return []


# Global instance
session_manager = SessionManager()
