import os
from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

# JWT configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Read secret from environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

password_hash = PasswordHash.recommended()


# Hash a password securely
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# Verify a password against its hash
def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


# Generate a JWT access token
def create_access_token(username: str, role: str) -> str:
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    if role not in ("admin", "employee"):
        raise ValueError("Invalid user role")

    expires = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expires,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# Decode and validate a JWT token
def decode_access_token(token: str) -> dict:
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["sub", "role", "exp"]},
        )

        if (
            not isinstance(payload.get("sub"), str)
            or not payload["sub"]
            or payload.get("role") not in ("admin", "employee")
        ):
            raise ValueError("Invalid token claims")

        return payload

    except (InvalidTokenError, ValueError) as exc:
        raise ValueError("Invalid or expired access token") from exc
