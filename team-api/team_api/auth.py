"""Authentication: password hashing, JWT creation and validation."""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt


def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(username: str, *, secret: str, ttl_hours: int = 24) -> str:
    """Create a JWT token for the given username."""
    payload = {
        "sub": username,
        "exp": datetime.now(UTC) + timedelta(hours=ttl_hours),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_token(token: str, *, secret: str) -> dict[str, Any]:
    """Verify and decode a JWT token."""
    return jwt.decode(token, secret, algorithms=["HS256"])
