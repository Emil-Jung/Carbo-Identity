"""Login sessions and token validation for carbo-identity."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app import config as app_config
from app.security import generate_session_token, hash_token, verify_password
from app.services import users as users_svc


def login(conn, login_id: str, password: str) -> dict:
    """Validate credentials, create a session, return {token, user, permissions, expires_at}.

    Raises ValueError('invalid') for bad login/password, ('disabled') for disabled user.
    """
    creds = users_svc.get_login_credentials(conn, login_id)
    if not creds:
        raise ValueError("invalid")
    if not verify_password(password, creds["password_hash"]):
        raise ValueError("invalid")
    if creds["status"] != "active":
        raise ValueError("disabled")

    user_id = creds["user_id"]
    token = generate_session_token()
    token_h = hash_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=app_config.SESSION_TTL_HOURS)

    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO sessions (token_hash, user_id, expires_at, last_used_at)
            VALUES (%s, %s, %s, NOW())
            """,
            (token_h, user_id, expires_at),
        )
    finally:
        cur.close()

    users_svc.touch_last_login(conn, user_id)
    permissions = users_svc.get_effective_permissions(conn, user_id)

    return {
        "token": token,
        "expires_at": expires_at.isoformat(),
        "user": {
            "user_id": user_id,
            "login_id": creds["login_id"],
            "display_name": creds["display_name"],
        },
        "permissions": permissions,
    }


def resolve_token(conn, token: str, update_last_used: bool = True) -> dict | None:
    """Return {user_id, login_id, display_name, permissions} for a valid token, else None."""
    if not token:
        return None
    token_h = hash_token(token)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT s.session_id, s.user_id, s.expires_at, s.revoked_at,
                   u.login_id, u.display_name, u.status
            FROM sessions s
            JOIN users u ON u.user_id = s.user_id
            WHERE s.token_hash = %s
            """,
            (token_h,),
        )
        row = cur.fetchone()
    finally:
        cur.close()
    if not row:
        return None

    session_id, user_id, expires_at, revoked_at, login_id, display_name, status = row
    if revoked_at is not None:
        return None
    if status != "active":
        return None
    now = datetime.now(timezone.utc)
    if expires_at and expires_at <= now:
        return None

    if update_last_used:
        cur = conn.cursor()
        try:
            cur.execute("UPDATE sessions SET last_used_at = NOW() WHERE session_id = %s", (session_id,))
        finally:
            cur.close()

    permissions = users_svc.get_effective_permissions(conn, user_id)
    return {
        "user_id": user_id,
        "login_id": login_id,
        "display_name": display_name,
        "permissions": permissions,
    }


def logout(conn, token: str) -> None:
    if not token:
        return
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE sessions SET revoked_at = NOW() WHERE token_hash = %s AND revoked_at IS NULL",
            (hash_token(token),),
        )
    finally:
        cur.close()
