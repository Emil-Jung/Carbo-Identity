"""Admin endpoints (require identity.admin): users, roles, permissions.

Used by the CIS shell's Identity Admin module.
"""

from fastapi import APIRouter, Depends, HTTPException

from app import db
from app import permissions as perms
from app.deps.auth import require_permission
from app.services import users as users_svc

router = APIRouter()

_admin = require_permission("identity.admin")


@router.get("/permissions")
def list_permissions(_: dict = Depends(_admin)):
    return {"permissions": perms.PERMISSION_CATALOG}


# ---- Users ----

@router.get("/users")
def list_users(_: dict = Depends(_admin)):
    conn = db.get_connection()
    try:
        return {"users": users_svc.list_users(conn)}
    finally:
        conn.close()


@router.post("/users")
def create_user(body: dict, admin: dict = Depends(_admin)):
    conn = db.get_connection()
    try:
        password = (body.get("password") or "").strip()
        invite = not password
        user = users_svc.create_user(
            conn,
            login_id=body.get("login_id"),
            display_name=body.get("display_name"),
            password=password or None,
            created_by=admin.get("login_id"),
            invite=invite,
        )
        role_ids = body.get("role_ids")
        if role_ids:
            users_svc.set_user_roles(conn, user["user_id"], role_ids)
        if "tile_permissions" in body:
            users_svc.set_user_tile_permissions(conn, user["user_id"], body.get("tile_permissions") or [])
        conn.commit()
        full = users_svc.get_user(conn, user["user_id"])
        login_id = full["login_id"]
        full["invite_url"] = f"/cis/?user={login_id}"
        return full
    except ValueError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


@router.patch("/users/{user_id}")
def update_user(user_id: int, body: dict, _: dict = Depends(_admin)):
    conn = db.get_connection()
    try:
        updated = users_svc.update_user(
            conn,
            user_id,
            display_name=body.get("display_name"),
            status=body.get("status"),
            password=body.get("password"),
        )
        if updated is None:
            raise HTTPException(status_code=404, detail="User not found")
        if "role_ids" in body:
            users_svc.set_user_roles(conn, user_id, body.get("role_ids") or [])
        if "tile_permissions" in body:
            users_svc.set_user_tile_permissions(conn, user_id, body.get("tile_permissions") or [])
        conn.commit()
        return users_svc.get_user(conn, user_id)
    except ValueError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


# ---- Roles ----

@router.get("/roles")
def list_roles(_: dict = Depends(_admin)):
    conn = db.get_connection()
    try:
        return {"roles": users_svc.list_roles(conn)}
    finally:
        conn.close()


@router.post("/roles")
def create_role(body: dict, _: dict = Depends(_admin)):
    conn = db.get_connection()
    try:
        role = users_svc.create_role(
            conn,
            name=body.get("name"),
            description=body.get("description"),
            permissions=body.get("permissions") or [],
        )
        conn.commit()
        return role
    except ValueError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


@router.put("/roles/{role_id}/permissions")
def set_role_permissions(role_id: int, body: dict, _: dict = Depends(_admin)):
    conn = db.get_connection()
    try:
        role = users_svc.set_role_permissions(conn, role_id, body.get("permissions") or [])
        if role is None:
            raise HTTPException(status_code=404, detail="Role not found")
        conn.commit()
        return role
    except ValueError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
