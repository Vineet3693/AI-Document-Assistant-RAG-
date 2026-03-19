"""Rate limiting middleware"""

from fastapi import Request, HTTPException
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.limit = requests_per_minute
        self.requests = defaultdict(list)
    
    async def check_limit(self, request: Request) -> bool:
        client_ip = request.client.host
        now = time.time()
        
        # Clean old requests
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < 60]
        
        if len(self.requests[client_ip]) >= self.limit:
            return False
        
        self.requests[client_ip].append(now)
        return True

rate_limiter = RateLimiter()
