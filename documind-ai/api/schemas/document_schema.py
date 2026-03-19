"""Document schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocumentInfo(BaseModel):
    id: str
    name: str
    type: str
    pages: int
    size: int
    created_at: str
    tags: Optional[List[str]] = []

class DocumentList(BaseModel):
    documents: List[DocumentInfo]
    total_count: int

class DocumentSearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = {}
