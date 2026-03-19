"""
Auth Routes
Handles user authentication, signup, login, and session management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
import os
import uuid
import hashlib
from datetime import datetime, timedelta

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)


# In-memory user store (use database in production)
users_store: Dict[str, Dict[str, Any]] = {}
sessions_store: Dict[str, Dict[str, Any]] = {}


# Request/Response Models
class SignupRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    company: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]


# Helper functions
def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token(user_id: str, email: str, expires_hours: int = 24) -> str:
    """Generate JWT token for user."""
    if not JWT_AVAILABLE:
        # Fallback: simple token
        return f"token_{user_id}_{uuid.uuid4().hex}"
    
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(hours=expires_hours),
        'iat': datetime.utcnow()
    }
    
    secret = os.getenv('SECRET_KEY', 'documind-secret-key-change-in-production')
    return jwt.encode(payload, secret, algorithm='HS256')


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token."""
    if not JWT_AVAILABLE:
        # Fallback: accept any token starting with 'token_'
        if token.startswith('token_'):
            parts = token.split('_')
            if len(parts) >= 2:
                return {'user_id': parts[1]}
        return None
    
    try:
        secret = os.getenv('SECRET_KEY', 'documind-secret-key-change-in-production')
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except Exception:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Get current authenticated user from token."""
    if not credentials:
        return None
    
    payload = verify_token(credentials.credentials)
    if not payload:
        return None
    
    user_id = payload.get('user_id')
    return users_store.get(user_id)


@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    """
    Create a new user account.
    
    Args:
        email: User email
        password: User password
        name: Optional user name
        company: Optional company name
        
    Returns:
        Access token and user info
    """
    # Check if user already exists
    existing_user = next(
        (u for u in users_store.values() if u['email'] == request.email),
        None
    )
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create user
    user_id = str(uuid.uuid4())
    user = {
        'id': user_id,
        'email': request.email,
        'password_hash': hash_password(request.password),
        'name': request.name or '',
        'company': request.company or '',
        'created_at': datetime.utcnow().isoformat(),
        'role': 'user',
        'is_active': True
    }
    
    users_store[user_id] = user
    
    # Generate token
    token = generate_token(user_id, request.email)
    
    # Remove sensitive data from response
    user_response = {k: v for k, v in user.items() if k != 'password_hash'}
    
    return TokenResponse(
        access_token=token,
        expires_in=86400,  # 24 hours
        user=user_response
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login with email and password.
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Access token and user info
    """
    # Find user
    user = next(
        (u for u in users_store.values() if u['email'] == request.email),
        None
    )
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Verify password
    if user['password_hash'] != hash_password(request.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=403,
            detail="Account is deactivated"
        )
    
    # Generate token
    token = generate_token(user['id'], user['email'])
    
    # Update last login
    user['last_login'] = datetime.utcnow().isoformat()
    
    # Remove sensitive data from response
    user_response = {k: v for k, v in user.items() if k != 'password_hash'}
    
    return TokenResponse(
        access_token=token,
        expires_in=86400,
        user=user_response
    )


@router.post("/logout")
async def logout(
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Logout current user.
    
    Args:
        user: Current user (from token)
        
    Returns:
        Logout confirmation
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # In production, would invalidate token/sessions
    # For now, just return success
    
    return JSONResponse({
        "status": "success",
        "message": "Logged out successfully"
    })


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get current user information.
    
    Args:
        user: Current user (from token)
        
    Returns:
        User profile information
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Remove sensitive data
    user_response = {k: v for k, v in user.items() if k != 'password_hash'}
    
    return user_response


@router.put("/me")
async def update_user_profile(
    name: Optional[str] = None,
    company: Optional[str] = None,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update user profile.
    
    Args:
        name: New name
        company: New company
        user: Current user
        
    Returns:
        Updated user profile
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if name is not None:
        user['name'] = name
    if company is not None:
        user['company'] = company
    
    user['updated_at'] = datetime.utcnow().isoformat()
    
    user_response = {k: v for k, v in user.items() if k != 'password_hash'}
    
    return JSONResponse({
        "status": "success",
        "user": user_response
    })


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Change user password.
    
    Args:
        current_password: Current password
        new_password: New password
        user: Current user
        
    Returns:
        Success confirmation
    """
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Verify current password
    if user['password_hash'] != hash_password(current_password):
        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect"
        )
    
    # Update password
    user['password_hash'] = hash_password(new_password)
    user['updated_at'] = datetime.utcnow().isoformat()
    
    return JSONResponse({
        "status": "success",
        "message": "Password changed successfully"
    })


@router.post("/google")
async def login_with_google(
    id_token: str,
    name: Optional[str] = None,
    email: Optional[str] = None
):
    """
    Login/signup with Google OAuth.
    
    Args:
        id_token: Google ID token
        name: User name from Google
        email: Email from Google
        
    Returns:
        Access token
    """
    # Placeholder - would verify Google token
    # For demo, create/find user by email
    
    if not email:
        email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    
    # Find or create user
    user = next(
        (u for u in users_store.values() if u['email'] == email),
        None
    )
    
    if not user:
        user_id = str(uuid.uuid4())
        user = {
            'id': user_id,
            'email': email,
            'name': name or '',
            'auth_provider': 'google',
            'created_at': datetime.utcnow().isoformat(),
            'role': 'user',
            'is_active': True
        }
        users_store[user_id] = user
    
    token = generate_token(user['id'], user['email'])
    user_response = {k: v for k, v in user.items() if k != 'password_hash'}
    
    return TokenResponse(
        access_token=token,
        expires_in=86400,
        user=user_response
    )


@router.post("/microsoft")
async def login_with_microsoft(
    id_token: str,
    name: Optional[str] = None,
    email: Optional[str] = None
):
    """
    Login/signup with Microsoft OAuth.
    
    Similar to Google login but for Microsoft accounts.
    """
    # Placeholder implementation
    return await login_with_google(id_token, name, email)
