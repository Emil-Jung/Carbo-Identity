"""
Seed default roles and a bootstrap admin for carbo-identity.

Run once after applying schema_identity.sql:
    cd identity_api
    .venv/bin/python seed_identity.py

- Creates/updates the default roles (admin, operations, finance, quality_viewer).
- Always ensures login **admin** exists with the admin role (standard CIS login).
- Also ensures BOOTSTRAP_ADMIN_LOGIN from .env if different (legacy e.g. carbo_user).

Password: BOOTSTRAP_ADMIN_PASSWORD env for new accounts, else random (printed once).
"""

from __future__ import annotations

import os
import secrets

from dotenv import load_dotenv

load_dotenv(override=True)

from app import db
from app import permissions as perms
from app.services import users as users_svc


def _ensure_roles(conn) -> dict[str, int]:
    existing = {r["name"]: r for r in users_svc.list_roles(conn)}
    role_ids: dict[str, int] = {}
    for name, spec in perms.DEFAULT_ROLES.items():
        if name in existing:
            rid = existing[name]["role_id"]
            users_svc.set_role_permissions(conn, rid, spec["permissions"])
            print(f"  role '{name}' updated")
        else:
            role = users_svc.create_role(conn, name, spec["description"], spec["permissions"])
            rid = role["role_id"]
            print(f"  role '{name}' created")
        role_ids[name] = rid
    return role_ids


def _ensure_admin_user(
    conn,
    role_ids: dict[str, int],
    login_id: str,
    display_name: str,
    password: str | None,
) -> None:
    login_id = (login_id or "").strip()
    if not login_id:
        return
    if users_svc.get_login_credentials(conn, login_id):
        print(f"Admin user '{login_id}' already exists — ensuring admin role.")
        if users_svc.ensure_user_has_role(conn, login_id, "admin"):
            print(f"  assigned 'admin' role to '{login_id}'")
        return
    generated = not password
    pwd = password or secrets.token_urlsafe(9)
    user = users_svc.create_user(
        conn,
        login_id=login_id,
        display_name=display_name,
        password=pwd,
        created_by="seed",
    )
    users_svc.set_user_roles(conn, user["user_id"], [role_ids["admin"]])
    print(f"Created admin user '{login_id}'.")
    if generated:
        print("\n" + "=" * 48)
        print(f"  ADMIN LOGIN: {login_id}")
        print(f"  ADMIN PASSWORD: {pwd}")
        print("  Save this now — it will not be shown again.")
        print("=" * 48 + "\n")


def main() -> None:
    bootstrap_login = os.environ.get("BOOTSTRAP_ADMIN_LOGIN", "admin").strip() or "admin"
    bootstrap_password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", "").strip() or None

    conn = db.get_connection()
    try:
        print("Seeding roles...")
        role_ids = _ensure_roles(conn)

        print("Ensuring admin logins...")
        _ensure_admin_user(
            conn,
            role_ids,
            "admin",
            "Administrator",
            bootstrap_password if bootstrap_login == "admin" else None,
        )
        if bootstrap_login.lower() != "admin":
            _ensure_admin_user(
                conn,
                role_ids,
                bootstrap_login,
                "Administrator",
                bootstrap_password,
            )

        conn.commit()
    finally:
        conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
