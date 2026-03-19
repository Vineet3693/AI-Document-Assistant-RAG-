"""Access control and permissions"""

from typing import Dict, List, Optional
from enum import Enum

class Role(Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class AccessControl:
    def __init__(self):
        self.permissions: Dict[str, Dict] = {}
    
    def grant_access(self, user_id: str, doc_id: str, role: Role):
        if doc_id not in self.permissions:
            self.permissions[doc_id] = {}
        self.permissions[doc_id][user_id] = role
    
    def check_access(self, user_id: str, doc_id: str, required_role: Role) -> bool:
        if doc_id not in self.permissions:
            return False
        user_role = self.permissions[doc_id].get(user_id)
        if not user_role:
            return False
        hierarchy = {Role.VIEWER: 0, Role.EDITOR: 1, Role.ADMIN: 2}
        return hierarchy[user_role] >= hierarchy[required_role]
    
    def list_documents(self, user_id: str) -> List[str]:
        return [doc_id for doc_id, users in self.permissions.items() if user_id in users]
