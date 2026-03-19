"""DocuMind AI - Database Module"""
from .connection import get_db, init_db
from .models import Document, User, ChatHistory, AuditLog

__all__ = [
    "get_db",
    "init_db",
    "Document",
    "User",
    "ChatHistory",
    "AuditLog"
]
