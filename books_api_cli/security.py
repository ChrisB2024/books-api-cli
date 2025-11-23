import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError as JWTError
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# API Key Configuration
API_KEY = os.getenv("API_KEY", "")  # Set in .env for production
API_KEY_NAME = "X-API-Key"

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)

# Security schemes - these MUST have auto_error=False to make dependencies optional
api_key_header = APIKeyHeader(
    name=API_KEY_NAME,
    auto_error=False,
    description="API Key for authentication. Get this from your admin.",
)
bearer_scheme = HTTPBearer(
    auto_error=False,
    description="JWT Bearer token. Get this from /auth/token endpoint.",
)


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# JWT token utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# API Key validation
async def verify_api_key(api_key: str = Security(api_key_header)):
    """Validate API key from header."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required",
        )

    if API_KEY and api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key"
        )

    return api_key


# JWT Bearer token validation
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
):
    """Validate JWT bearer token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# Combined: Accept either API Key OR JWT token
async def get_api_key_or_token(
    api_key: Optional[str] = Security(api_key_header),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
):
    """Allow authentication via API key OR JWT token."""
    # Check API key first
    if api_key and API_KEY and api_key == API_KEY:
        return {"type": "api_key"}

    # Check JWT token next
    if credentials:
        payload = decode_access_token(credentials.credentials)
        if payload:
            return {"type": "jwt", "user": payload}

    # If neither API key nor token is valid, raise error
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=(
            "Invalid authentication credentials. "
            "Provide either X-API-Key header or Bearer token."
        ),
        headers={"WWW-Authenticate": "Bearer"},
    )
