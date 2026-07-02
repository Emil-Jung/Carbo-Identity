"""Authentication endpoints: login, logout, me/introspect, first sign-in password."""

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app import db
from app.deps.auth import get_current_user
from app.services import auth as auth_svc
from app.services import users as users_svc

router = APIRouter()


class LoginRequest(BaseModel):
    login_id: str
    password: str


class SetInitialPasswordRequest(BaseModel):
    login_id: str
    password: str


@router.get("/auth/account-status")
def account_status(login_id: str = ""):
    login_id = (login_id or "").strip()
    if not login_id:
        raise HTTPException(status_code=400, detail="login_id required")
    conn = db.get_connection()
    try:
        return users_svc.get_account_status(conn, login_id)
    finally:
        conn.close()


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
        if code == "password_not_set":
            raise HTTPException(
                status_code=403,
                detail="password_not_set",
            )
        raise HTTPException(status_code=401, detail="Invalid login or password")
    finally:
        conn.close()
    return result


@router.post("/auth/set-initial-password")
def set_initial_password(body: SetInitialPasswordRequest):
    login_id = (body.login_id or "").strip()
    password = body.password or ""
    if not login_id or not password:
        raise HTTPException(status_code=400, detail="login_id and password required")
    conn = db.get_connection()
    try:
        result = auth_svc.set_initial_password(conn, login_id, password)
        conn.commit()
    except ValueError as e:
        conn.rollback()
        code = str(e)
        if code == "disabled":
            raise HTTPException(status_code=403, detail="Account is disabled")
        if code == "already_set":
            raise HTTPException(status_code=409, detail="Password already set — sign in normally")
        raise HTTPException(status_code=404, detail="Unknown User ID")
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
