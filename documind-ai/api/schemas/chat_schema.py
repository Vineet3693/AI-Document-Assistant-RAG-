"""Chat request/response schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    doc_ids: Optional[List[str]] = []
    mode: Optional[str] = "standard"
    language: Optional[str] = "en"
    max_tokens: Optional[int] = 1000

class Citation(BaseModel):
    document: str
    page: Optional[int]
    text: str

class ChatResponse(BaseModel):
    answer: str
    citations: Optional[List[Citation]] = []
    confidence: str = "medium"
    tokens_used: int = 0
    model: str = "gpt-4"
