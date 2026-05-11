"""
shared/auth/jwt.py
──────────────────
JWT creation, verification, and dependency injection helpers.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


# ──────────────────────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────────────────────

SECRET_KEY: str = os.getenv(
    "SECRET_KEY",
    "dev-secret-change-in-production-abc123"
)

ALGORITHM: str = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)


# IMPORTANT:
# Use pbkdf2_sha256 instead of bcrypt.
# Much more stable on Python 3.12.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

bearer_scheme = HTTPBearer(auto_error=False)


# ──────────────────────────────────────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────────────────────────────────────

class TokenPayload(BaseModel):
    sub: str
    name: str
    role: str = "farmer"
    exp: Optional[int] = None


class UserInToken(BaseModel):
    farmer_id: str
    name: str
    role: str


# ──────────────────────────────────────────────────────────────────────────────
# Password Helpers
# ──────────────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """
    Hash a plain-text password.
    """
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify plain password against stored hash.
    """
    return pwd_context.verify(plain, hashed)


# ──────────────────────────────────────────────────────────────────────────────
# JWT Helpers
# ──────────────────────────────────────────────────────────────────────────────

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode["exp"] = expire

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_token(token: str) -> TokenPayload:

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return TokenPayload(**payload)

    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ──────────────────────────────────────────────────────────────────────────────
# FastAPI Dependencies
# ──────────────────────────────────────────────────────────────────────────────

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        bearer_scheme
    ),
) -> UserInToken:

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)

    return UserInToken(
        farmer_id=payload.sub,
        name=payload.name,
        role=payload.role,
    )


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        bearer_scheme
    ),
) -> Optional[UserInToken]:

    if credentials is None:
        return None

    try:
        payload = decode_token(credentials.credentials)

        return UserInToken(
            farmer_id=payload.sub,
            name=payload.name,
            role=payload.role,
        )

    except HTTPException:
        return None