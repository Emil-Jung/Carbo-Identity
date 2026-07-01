"""User, role and permission storage for carbo-identity."""

from __future__ import annotations

from typing import Any

from app import permissions as perms
from app.security import hash_password


# ---- Users -------------------------------------------------------------

def _user_row(row: tuple) -> dict[str, Any]:
    return {
        "user_id": row[0],
        "login_id": row[1],
        "display_name": row[2],
        "status": row[3],
        "created_at": row[4].isoformat() if row[4] else None,
        "created_by": row[5],
        "last_login_at": row[6].isoformat() if row[6] else None,
    }


_USER_COLS = "user_id, login_id, display_name, status, created_at, created_by, last_login_at"


def list_users(conn) -> list[dict]:
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT {_USER_COLS} FROM users ORDER BY login_id")
        users = [_user_row(r) for r in cur.fetchall()]
    finally:
        cur.close()
    for u in users:
        u["roles"] = get_user_role_names(conn, u["user_id"])
        u["permissions"] = get_effective_permissions(conn, u["user_id"])
    return users


def get_user(conn, user_id: int) -> dict | None:
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT {_USER_COLS} FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
    finally:
        cur.close()
    if not row:
        return None
    user = _user_row(row)
    user["roles"] = get_user_role_names(conn, user_id)
    user["permissions"] = get_effective_permissions(conn, user_id)
    return user


def get_login_credentials(conn, login_id: str) -> dict | None:
    """Return {user_id, login_id, display_name, status, password_hash} or None."""
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT user_id, login_id, display_name, status, password_hash "
            "FROM users WHERE lower(login_id) = lower(%s)",
            ((login_id or "").strip(),),
        )
        row = cur.fetchone()
    finally:
        cur.close()
    if not row:
        return None
    return {
        "user_id": row[0],
        "login_id": row[1],
        "display_name": row[2],
        "status": row[3],
        "password_hash": row[4],
    }


def create_user(conn, login_id: str, display_name: str, password: str,
                created_by: str | None = None) -> dict:
    login_id = (login_id or "").strip()
    display_name = (display_name or "").strip()
    if not login_id:
        raise ValueError("login_id required")
    if not display_name:
        raise ValueError("display_name required")
    pwd_hash = hash_password(password)  # raises ValueError if too short
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM users WHERE lower(login_id) = lower(%s)", (login_id,))
        if cur.fetchone():
            raise ValueError("login_id already exists")
        cur.execute(
            f"""
            INSERT INTO users (login_id, display_name, password_hash, created_by)
            VALUES (%s, %s, %s, %s)
            RETURNING {_USER_COLS}
            """,
            (login_id, display_name, pwd_hash, created_by),
        )
        row = cur.fetchone()
    finally:
        cur.close()
    return _user_row(row)


def update_user(conn, user_id: int, display_name: str | None = None,
                status: str | None = None, password: str | None = None) -> dict | None:
    updates = []
    params: list[Any] = []
    if display_name is not None:
        display_name = display_name.strip()
        if not display_name:
            raise ValueError("display_name cannot be empty")
        updates.append("display_name = %s")
        params.append(display_name)
    if status is not None:
        status = status.strip().lower()
        if status not in ("active", "disabled"):
            raise ValueError("invalid status")
        updates.append("status = %s")
        params.append(status)
    if password is not None:
        updates.append("password_hash = %s")
        params.append(hash_password(password))
    if not updates:
        return get_user(conn, user_id)
    params.append(user_id)
    cur = conn.cursor()
    try:
        cur.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s RETURNING user_id",
            tuple(params),
        )
        row = cur.fetchone()
    finally:
        cur.close()
    if not row:
        return None
    # Disabling a user kills their active sessions immediately.
    if status == "disabled":
        revoke_user_sessions(conn, user_id)
    return get_user(conn, user_id)


def touch_last_login(conn, user_id: int) -> None:
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET last_login_at = NOW() WHERE user_id = %s", (user_id,))
    finally:
        cur.close()


# ---- Roles & permissions ----------------------------------------------

def list_roles(conn) -> list[dict]:
    cur = conn.cursor()
    try:
        cur.execute("SELECT role_id, name, description FROM roles ORDER BY name")
        rows = cur.fetchall()
    finally:
        cur.close()
    roles = []
    for r in rows:
        roles.append({
            "role_id": r[0],
            "name": r[1],
            "description": r[2],
            "permissions": get_role_permissions(conn, r[0]),
        })
    return roles


def get_role_permissions(conn, role_id: int) -> list[str]:
    cur = conn.cursor()
    try:
        cur.execute("SELECT permission FROM role_permissions WHERE role_id = %s ORDER BY permission", (role_id,))
        return [r[0] for r in cur.fetchall()]
    finally:
        cur.close()


def create_role(conn, name: str, description: str | None, permissions: list[str]) -> dict:
    name = (name or "").strip()
    if not name:
        raise ValueError("role name required")
    bad = [p for p in (permissions or []) if not perms.is_valid_permission(p)]
    if bad:
        raise ValueError(f"unknown permission(s): {', '.join(bad)}")
    cur = conn.cursor()
    try:
        cur.execute("SELECT 1 FROM roles WHERE lower(name) = lower(%s)", (name,))
        if cur.fetchone():
            raise ValueError("role already exists")
        cur.execute(
            "INSERT INTO roles (name, description) VALUES (%s, %s) RETURNING role_id",
            (name, description),
        )
        role_id = cur.fetchone()[0]
        for p in sorted(set(permissions or [])):
            cur.execute(
                "INSERT INTO role_permissions (role_id, permission) VALUES (%s, %s)",
                (role_id, p),
            )
    finally:
        cur.close()
    return {"role_id": role_id, "name": name, "description": description,
            "permissions": sorted(set(permissions or []))}


def set_role_permissions(conn, role_id: int, permissions: list[str]) -> dict | None:
    bad = [p for p in (permissions or []) if not perms.is_valid_permission(p)]
    if bad:
        raise ValueError(f"unknown permission(s): {', '.join(bad)}")
    cur = conn.cursor()
    try:
        cur.execute("SELECT name, description FROM roles WHERE role_id = %s", (role_id,))
        row = cur.fetchone()
        if not row:
            return None
        cur.execute("DELETE FROM role_permissions WHERE role_id = %s", (role_id,))
        for p in sorted(set(permissions or [])):
            cur.execute(
                "INSERT INTO role_permissions (role_id, permission) VALUES (%s, %s)",
                (role_id, p),
            )
    finally:
        cur.close()
    return {"role_id": role_id, "name": row[0], "description": row[1],
            "permissions": sorted(set(permissions or []))}


def get_user_role_names(conn, user_id: int) -> list[str]:
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT r.name FROM user_roles ur
            JOIN roles r ON r.role_id = ur.role_id
            WHERE ur.user_id = %s ORDER BY r.name
            """,
            (user_id,),
        )
        return [r[0] for r in cur.fetchall()]
    finally:
        cur.close()


def set_user_roles(conn, user_id: int, role_ids: list[int]) -> None:
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM user_roles WHERE user_id = %s", (user_id,))
        for rid in sorted(set(role_ids or [])):
            cur.execute(
                "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s) "
                "ON CONFLICT DO NOTHING",
                (user_id, rid),
            )
    finally:
        cur.close()


def get_effective_permissions(conn, user_id: int) -> list[str]:
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT DISTINCT rp.permission
            FROM user_roles ur
            JOIN role_permissions rp ON rp.role_id = ur.role_id
            WHERE ur.user_id = %s
            ORDER BY rp.permission
            """,
            (user_id,),
        )
        return [r[0] for r in cur.fetchall()]
    finally:
        cur.close()


def revoke_user_sessions(conn, user_id: int) -> None:
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE sessions SET revoked_at = NOW() WHERE user_id = %s AND revoked_at IS NULL",
            (user_id,),
        )
    finally:
        cur.close()
