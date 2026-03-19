"""DocuMind AI - API Schemas Module"""
from .upload_schema import UploadRequest, UploadResponse
from .chat_schema import ChatRequest, ChatResponse
from .document_schema import DocumentInfo, DocumentList
from .response_schema import SuccessResponse, ErrorResponse

__all__ = [
    "UploadRequest",
    "UploadResponse",
    "ChatRequest",
    "ChatResponse",
    "DocumentInfo",
    "DocumentList",
    "SuccessResponse",
    "ErrorResponse"
]
