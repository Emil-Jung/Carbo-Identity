"""
Seed default roles and a bootstrap admin for carbo-identity.

Run once after applying schema_identity.sql:
    cd identity_api
    python seed_identity.py

- Creates/updates the default roles (admin, operations, finance) and their permissions.
- Creates the bootstrap admin user if it does not exist.
  Password: BOOTSTRAP_ADMIN_PASSWORD env, else a random one printed ONCE here.

Simon and Juliana are created afterwards from the Identity Admin module in the shell.
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


def main() -> None:
    login_id = os.environ.get("BOOTSTRAP_ADMIN_LOGIN", "admin").strip() or "admin"
    password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", "").strip()
    generated = False
    if not password:
        password = secrets.token_urlsafe(9)
        generated = True

    conn = db.get_connection()
    try:
        print("Seeding roles...")
        role_ids = _ensure_roles(conn)

        if users_svc.get_login_credentials(conn, login_id):
            print(f"Admin user '{login_id}' already exists — ensuring admin role.")
            if users_svc.ensure_user_has_role(conn, login_id, "admin"):
                print(f"  assigned 'admin' role to '{login_id}'")
        else:
            user = users_svc.create_user(
                conn, login_id=login_id, display_name="Administrator",
                password=password, created_by="seed",
            )
            users_svc.set_user_roles(conn, user["user_id"], [role_ids["admin"]])
            print(f"Created admin user '{login_id}'.")
            if generated:
                print("\n" + "=" * 48)
                print(f"  ADMIN LOGIN: {login_id}")
                print(f"  ADMIN PASSWORD: {password}")
                print("  Save this now — it will not be shown again.")
                print("=" * 48 + "\n")
        conn.commit()
    finally:
        conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
