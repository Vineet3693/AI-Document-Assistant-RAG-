"""Request validation middleware"""

from fastapi import Request, HTTPException
import logging

logger = logging.getLogger(__name__)

class RequestValidator:
    def __init__(self):
        self.allowed_content_types = ['application/json', 'multipart/form-data']
    
    async def validate(self, request: Request) -> None:
        if request.method in ['POST', 'PUT'] and request.headers.get('content-type'):
            content_type = request.headers['content-type'].split(';')[0]
            if content_type not in self.allowed_content_types:
                raise HTTPException(415, f"Unsupported media type: {content_type}")

request_validator = RequestValidator()
