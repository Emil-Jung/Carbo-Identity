"""
Central permission catalog for the whole Carbo cloud.

Permissions are namespaced strings: "<app>.<area>.<action>".
Add new capabilities here as modules are added to the CIS shell; roles then
grant a subset. The shell shows a module only if the user holds its permission.
"""

from __future__ import annotations

# (key, human label, which CIS module it unlocks)
PERMISSION_CATALOG: list[dict] = [
    {"key": "identity.admin", "label": "Identity administration (users, roles)", "module": "identity_admin"},
    {"key": "maintenance.ops.view", "label": "Maintenance — Operations view", "module": "maintenance_ops"},
    {"key": "maintenance.fuel.view", "label": "Maintenance — Consumption (fuel numbers)", "module": "consumption"},
    # Future modules (declared early so roles can be prepared):
    {"key": "maintenance.certs.view", "label": "Maintenance — Certificates & licenses", "module": "maintenance_ops"},
    {"key": "quality.view", "label": "Quality — Viewer", "module": "quality_view"},
]

ALL_PERMISSIONS: set[str] = {p["key"] for p in PERMISSION_CATALOG}

# Default roles seeded on first run. Admin can edit these later.
DEFAULT_ROLES: dict[str, dict] = {
    "admin": {
        "description": "Full access incl. user administration",
        "permissions": sorted(ALL_PERMISSIONS),
    },
    "operations": {
        "description": "Operations manager — fleet health + consumption",
        "permissions": ["maintenance.ops.view", "maintenance.certs.view", "maintenance.fuel.view"],
    },
    "finance": {
        "description": "Finance manager — consumption numbers only",
        "permissions": ["maintenance.fuel.view"],
    },
}


def is_valid_permission(perm: str) -> bool:
    return perm in ALL_PERMISSIONS


def module_for_permission(perm: str) -> str | None:
    for p in PERMISSION_CATALOG:
        if p["key"] == perm:
            return p.get("module")
    return None
