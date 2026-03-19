"""DocuMind AI - Security Module"""
from .encryption import EncryptionManager as Encryption
from .access_control import AccessControl as AccessControlManager
from .audit_logger import AuditLogger

__all__ = [
    "Encryption",
    "AccessControl",
    "AuditLogger"
]

# Backward compatibility aliases
AccessControl = AccessControlManager
