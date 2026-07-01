"""Password hashing and session-token helpers for carbo-identity.

- Passwords: PBKDF2-HMAC-SHA256 (stdlib), per-user random salt, peppered.
- Tokens:    random 32-byte urlsafe secret; only its SHA256(pepper+token) is stored.
Both use constant-time comparison.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

from app import config as app_config

_PBKDF2_ITERATIONS = 200_000
_PBKDF2_ALGO = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    password = password or ""
    if len(password) < 6:
        raise ValueError("password must be at least 6 characters")
    salt = secrets.token_hex(16)
    peppered = (app_config.effective_pepper() + password).encode("utf-8")
    digest = hashlib.pbkdf2_hmac("sha256", peppered, bytes.fromhex(salt), _PBKDF2_ITERATIONS)
    return f"{_PBKDF2_ALGO}${_PBKDF2_ITERATIONS}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iterations_s, salt, expected_hex = (stored or "").split("$", 3)
        if algo != _PBKDF2_ALGO:
            return False
        iterations = int(iterations_s)
    except (ValueError, AttributeError):
        return False
    peppered = (app_config.effective_pepper() + (password or "")).encode("utf-8")
    digest = hashlib.pbkdf2_hmac("sha256", peppered, bytes.fromhex(salt), iterations)
    return hmac.compare_digest(digest.hex(), expected_hex)


def generate_session_token() -> str:
    """Raw token given to the client (never stored in plaintext)."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    raw = (app_config.effective_pepper() + (token or "")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
