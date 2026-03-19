"""Audit logging for compliance"""

import json, logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AuditLogger:
    def __init__(self, log_file: str = "logs/audit.log"):
        self.log_file = log_file
    
    def log(self, event_type: str, user_id: str, details: Dict[str, Any]):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details
        }
        logger.info(json.dumps(entry))
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def log_upload(self, user_id: str, doc_id: str, filename: str):
        self.log("DOCUMENT_UPLOAD", user_id, {"doc_id": doc_id, "filename": filename})
    
    def log_access(self, user_id: str, doc_id: str):
        self.log("DOCUMENT_ACCESS", user_id, {"doc_id": doc_id})
    
    def log_query(self, user_id: str, query: str, doc_ids: list):
        self.log("QUERY_EXECUTED", user_id, {"query": query[:100], "doc_ids": doc_ids})
    
    def log_delete(self, user_id: str, doc_id: str):
        self.log("DOCUMENT_DELETE", user_id, {"doc_id": doc_id})
