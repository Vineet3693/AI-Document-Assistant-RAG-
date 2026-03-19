"""Database models"""

from datetime import datetime
from typing import Optional, List, Dict, Any

class Document:
    def __init__(self, id: str, name: str, user_id: str, 
                 file_type: str, size: int, pages: int = 0):
        self.id = id
        self.name = name
        self.user_id = user_id
        self.file_type = file_type
        self.size = size
        self.pages = pages
        self.created_at = datetime.utcnow()
        self.tags: List[str] = []
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "file_type": self.file_type,
            "size": self.size,
            "pages": self.pages,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags
        }

class User:
    def __init__(self, id: str, email: str, name: str):
        self.id = id
        self.email = email
        self.name = name
        self.created_at = datetime.utcnow()
        self.role = "user"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }

class ChatSession:
    def __init__(self, id: str, user_id: str):
        self.id = id
        self.user_id = user_id
        self.messages = []
        self.created_at = datetime.utcnow()
    
    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
