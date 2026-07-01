"""FastAPI auth dependencies for carbo-identity's own admin endpoints."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException

from app import db
from app.services import auth as auth_svc


def _extract_token(authorization: str | None, x_auth_token: str | None) -> str:
    if authorization:
        parts = authorization.split(" ", 1)
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1].strip()
        return authorization.strip()
    if x_auth_token:
        return x_auth_token.strip()
    return ""


def get_current_user(
    authorization: str | None = Header(default=None),
    x_auth_token: str | None = Header(default=None),
) -> dict:
    token = _extract_token(authorization, x_auth_token)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    conn = db.get_connection()
    try:
        user = auth_svc.resolve_token(conn, token)
        conn.commit()
    finally:
        conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    return user


def require_permission(permission: str):
    def _dep(user: dict = Depends(get_current_user)) -> dict:
        if permission not in (user.get("permissions") or []):
            raise HTTPException(status_code=403, detail=f"Missing permission: {permission}")
        return user
    return _dep
