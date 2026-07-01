"""Authentication endpoints: login, logout, me/introspect.

Other Carbo services introspect a bearer token by calling GET /auth/me with the
token. They should cache the result briefly (e.g. 5-15 min) so a short identity
outage does not immediately drop active sessions.
"""

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app import db
from app.deps.auth import get_current_user
from app.services import auth as auth_svc

router = APIRouter()


class LoginRequest(BaseModel):
    login_id: str
    password: str


@router.post("/auth/login")
def login(body: LoginRequest):
    login_id = (body.login_id or "").strip()
    password = body.password or ""
    if not login_id or not password:
        raise HTTPException(status_code=400, detail="login_id and password required")
    conn = db.get_connection()
    try:
        result = auth_svc.login(conn, login_id, password)
        conn.commit()
    except ValueError as e:
        conn.rollback()
        code = str(e)
        if code == "disabled":
            raise HTTPException(status_code=403, detail="Account is disabled")
        raise HTTPException(status_code=401, detail="Invalid login or password")
    finally:
        conn.close()
    return result


@router.post("/auth/logout")
def logout(authorization: str | None = Header(default=None),
           x_auth_token: str | None = Header(default=None)):
    token = ""
    if authorization:
        parts = authorization.split(" ", 1)
        token = parts[1].strip() if len(parts) == 2 and parts[0].lower() == "bearer" else authorization.strip()
    elif x_auth_token:
        token = x_auth_token.strip()
    if token:
        conn = db.get_connection()
        try:
            auth_svc.logout(conn, token)
            conn.commit()
        finally:
            conn.close()
    return {"status": "ok"}


@router.get("/auth/me")
def me(user: dict = Depends(get_current_user)):
    """Validate the caller's token and return identity + effective permissions."""
    return {
        "user_id": user["user_id"],
        "login_id": user["login_id"],
        "display_name": user["display_name"],
        "permissions": user.get("permissions") or [],
    }
