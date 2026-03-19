"""DocuMind AI - API Routes Module"""
from .upload import router as upload_router
from .chat import router as chat_router
from .documents import router as documents_router
from .features import router as features_router
from .analytics import router as analytics_router
from .export import router as export_router
from .auth import router as auth_router

__all__ = [
    "upload_router",
    "chat_router",
    "documents_router",
    "features_router",
    "analytics_router",
    "export_router",
    "auth_router"
]
