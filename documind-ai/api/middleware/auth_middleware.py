"""Authentication middleware"""

from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt, os
from datetime import datetime

security = HTTPBearer()

class AuthMiddleware:
    def __init__(self):
        self.secret = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    async def verify_token(self, request: Request, credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
        try:
            payload = jwt.decode(credentials.credentials, self.secret, algorithms=['HS256'])
            if datetime.fromtimestamp(payload['exp']) < datetime.now():
                raise HTTPException(401, "Token expired")
            return payload
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Invalid token")

auth_middleware = AuthMiddleware()
