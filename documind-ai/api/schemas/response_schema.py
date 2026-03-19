"""Generic response schemas"""

from pydantic import BaseModel
from typing import Optional, Any, List

class SuccessResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str
    details: Optional[Any] = None

class PaginatedResponse(BaseModel):
    status: str = "success"
    data: List[Any]
    total: int
    page: int
    per_page: int
