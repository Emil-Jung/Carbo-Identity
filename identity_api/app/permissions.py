"""
Central permission catalog for the whole Carbo cloud.

Each permission unlocks exactly one CIS dashboard tile (module).
Roles are optional templates; assign tiles individually per user in Users & access.
"""

from __future__ import annotations

# (key, human label, CIS module id, dashboard section for admin UI)
PERMISSION_CATALOG: list[dict] = [
    {"key": "identity.admin", "label": "Users & access", "module": "identity_admin", "section": "Administration"},
    {"key": "identity.device_keys", "label": "Device keys", "module": "device_keys", "section": "Administration"},
    {"key": "producers.office", "label": "Producers (office)", "module": "producers_office", "section": "Applications"},
    {"key": "traceability.access", "label": "Traceability", "module": "traceability", "section": "Applications"},
    {"key": "quality.capture", "label": "Quality (capture)", "module": "quality_capture", "section": "Applications"},
    {"key": "maintenance.manager", "label": "Maintenance (desktop app)", "module": "maintenance_manager", "section": "Applications"},
    {"key": "producers.public.view", "label": "FSC Public register", "module": "producers_public", "section": "Reports & lookups"},
    {"key": "quality.view", "label": "Quality Analysis", "module": "quality_view", "section": "Reports & lookups"},
    {"key": "traceability.stock.view", "label": "Big-K bag stock", "module": "bag_stock", "section": "Reports & lookups"},
    {"key": "maintenance.ops.view", "label": "Maintenance — Operations", "module": "maintenance_ops", "section": "Reports & lookups"},
    {"key": "maintenance.fuel.view", "label": "Consumption (diesel / fuel)", "module": "consumption", "section": "Reports & lookups"},
    {"key": "maintenance.certs.view", "label": "Maintenance — Certificates", "module": "maintenance_certs", "section": "Reports & lookups"},
]

ALL_PERMISSIONS: set[str] = {p["key"] for p in PERMISSION_CATALOG}

# Default roles = starter templates only (admin can change; users can mix tiles individually).
DEFAULT_ROLES: dict[str, dict] = {
    "admin": {
        "description": "Full access incl. user administration",
        "permissions": sorted(ALL_PERMISSIONS),
    },
    "operations": {
        "description": "Template — fleet ops, manager app, quality capture (adjust per person)",
        "permissions": [
            "maintenance.manager",
            "maintenance.ops.view",
            "maintenance.certs.view",
            "maintenance.fuel.view",
            "quality.capture",
        ],
    },
    "finance": {
        "description": "Template — consumption / diesel numbers only",
        "permissions": ["maintenance.fuel.view"],
    },
    "quality_viewer": {
        "description": "Template — view quality sheets only",
        "permissions": ["quality.view"],
    },
    "production_office": {
        "description": "Template — quality capture, view, and producers office",
        "permissions": [
            "quality.capture",
            "quality.view",
            "producers.office",
        ],
    },
}


def is_valid_permission(perm: str) -> bool:
    return perm in ALL_PERMISSIONS


def module_for_permission(perm: str) -> str | None:
    for p in PERMISSION_CATALOG:
        if p["key"] == perm:
            return p.get("module")
    return None


def catalog_by_section() -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for p in PERMISSION_CATALOG:
        section = p.get("section") or "Other"
        grouped.setdefault(section, []).append(p)
    return grouped
