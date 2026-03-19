"""Upload request/response schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UploadRequest(BaseModel):
    filename: str
    doc_type: Optional[str] = "general"
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}

class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    status: str
    pages: int = 0
    chunks: int = 0
    message: str

class BatchUploadResponse(BaseModel):
    total_files: int
    successful: int
    failed: int
    results: List[UploadResponse]
