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
    {"key": "identity.device_keys", "label": "Device keys & PWA API access", "module": "device_keys"},
    {"key": "maintenance.manager", "label": "Maintenance — Manager desktop app", "module": "maintenance_manager"},
    {"key": "maintenance.ops.view", "label": "Maintenance — Operations view", "module": "maintenance_ops"},
    {"key": "maintenance.fuel.view", "label": "Maintenance — Consumption (fuel numbers)", "module": "consumption"},
    {"key": "maintenance.certs.view", "label": "Maintenance — Certificates & licenses", "module": "maintenance_ops"},
    {"key": "quality.capture", "label": "Quality — Sieving Sheet capture", "module": "quality_capture"},
    {"key": "quality.view", "label": "Quality — Viewer", "module": "quality_view"},
    {"key": "producers.office", "label": "Producers — Office capture", "module": "producers_office"},
    {"key": "traceability.access", "label": "Traceability — scanner / supervisor", "module": "traceability"},
]

ALL_PERMISSIONS: set[str] = {p["key"] for p in PERMISSION_CATALOG}

# Default roles seeded on first run. Admin can edit these later.
DEFAULT_ROLES: dict[str, dict] = {
    "admin": {
        "description": "Full access incl. user administration",
        "permissions": sorted(ALL_PERMISSIONS),
    },
    "operations": {
        "description": "Operations manager — fleet health + consumption + Manager app",
        "permissions": [
            "maintenance.manager",
            "maintenance.ops.view",
            "maintenance.certs.view",
            "maintenance.fuel.view",
            "quality.capture",
        ],
    },
    "finance": {
        "description": "Finance manager — consumption numbers only",
        "permissions": ["maintenance.fuel.view"],
    },
    "quality_viewer": {
        "description": "Staff — view quality sheets only (CIS default for new users)",
        "permissions": ["quality.view"],
    },
}


def is_valid_permission(perm: str) -> bool:
    return perm in ALL_PERMISSIONS


def module_for_permission(perm: str) -> str | None:
    for p in PERMISSION_CATALOG:
        if p["key"] == perm:
            return p.get("module")
    return None
