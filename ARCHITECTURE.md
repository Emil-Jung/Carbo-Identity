# Carbo cloud — identity & viewer architecture

This describes how we "open the cloud" for people (Simon, Juliana, you) with a
single login and a single viewer, without giving humans device keys.

## The two kinds of access

| Actor        | How it authenticates        | Example                          |
|--------------|-----------------------------|----------------------------------|
| **Device**   | Device key (`X-API-Key`)    | A PWA on a tablet posting fuel   |
| **Person**   | Login + session token       | Simon opening the viewer         |

Device keys stay exactly as they are (per platform, for writes). People now go
through **carbo-identity**. The two never mix.

## Components

```
                         ┌─────────────────────────┐
   Installed CIS app ──▶ │  CIS desktop shell       │  one login, per-PC install,
   (PySide6 + web view)  │  hosts web modules       │  auto-updates from server
                         └───────────┬──────────────┘
                                     │ 1) POST /identity/api/auth/login
                                     │ 2) GET  /identity/api/auth/me  (permissions)
                                     ▼
                         ┌─────────────────────────┐
                         │  carbo-identity  :8003   │  users, roles, permissions,
                         │  own DB: carbo_identity  │  sessions (token hashes)
                         └───────────┬──────────────┘
                                     ▲  introspection (GET /auth/me + bearer)
                                     │
   CIS module reads data ──────────▶ maintenance API :8001  (and later quality, etc.)
   GET /maintenance/api/vehicles     each domain keeps its own DB
```

- **carbo-identity** owns *who* people are and *what* they may see.
- **Domain APIs** own their data. They do not store users.
- **CIS app** is a thin, installed, permission-gated launcher of modules that
  auto-updates from the server (`/cis/app/version.json`). It bundles the web
  modules, so adding a module later ships to every PC via the normal update.

## Permission model (RBAC)

- Permissions are namespaced strings (`app.area.action`) — catalog in
  `identity_api/app/permissions.py`.
- Roles bundle permissions. Seeded: `admin`, `operations`, `finance`.
- A user has roles; effective permissions = union across roles.
- The shell shows a module only if the user holds its `requires` permission.

Phase-1 permissions:

| Permission               | Unlocks module | Given to (default role) |
|--------------------------|----------------|-------------------------|
| `identity.admin`         | Identity Admin | admin                   |
| `maintenance.ops.view`   | Operations     | admin, operations       |
| `maintenance.fuel.view`  | Consumption    | admin, operations, finance |
| `maintenance.certs.view` | (Operations)   | admin, operations       |
| `quality.view`           | (future)       | admin                   |

## Sessions & security

- Password: PBKDF2-HMAC-SHA256, per-user salt, secret pepper, 200k iterations.
- Token: 32-byte random; only `sha256(pepper+token)` is stored.
- TTL configurable (`SESSION_TTL_HOURS`, default 12h).
- Disabling a user immediately revokes their active sessions.
- Revocation is instant because validation is server-side introspection (not JWT).

## Enforcement: client-side now, server-side next

**Now (phase 1):** the shell hides modules a user lacks permission for, and only
calls the endpoints those modules need. Maintenance GET endpoints are currently
open (unchanged), so nothing breaks.

**Next (phase 2):** enforce permissions on maintenance *read* endpoints too, so a
crafted request can't bypass the shell. Drop-in dependency for the maintenance API
(kept out of this repo so PWA writes are untouched until we choose to enable it):

```python
# maintenance_api/app/deps/identity_auth.py  (phase 2)
import time, urllib.request, json
from fastapi import Header, HTTPException

IDENTITY_URL = "http://127.0.0.1:8003/auth/me"
_cache = {}  # token -> (expiry_ts, user)

def _introspect(token: str) -> dict | None:
    hit = _cache.get(token)
    if hit and hit[0] > time.time():
        return hit[1]
    req = urllib.request.Request(IDENTITY_URL, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=3) as r:
            user = json.loads(r.read())
    except Exception:
        return None
    _cache[token] = (time.time() + 300, user)  # cache 5 min
    return user

def require_view_permission(permission: str):
    def _dep(authorization: str | None = Header(default=None)):
        token = (authorization or "").removeprefix("Bearer ").strip()
        user = _introspect(token) if token else None
        if not user:
            raise HTTPException(401, "Not authenticated")
        if permission not in (user.get("permissions") or []):
            raise HTTPException(403, f"Missing permission: {permission}")
        return user
    return _dep
```

Then add `dependencies=[Depends(require_view_permission("maintenance.ops.view"))]`
to the relevant GET routes. Writes keep using device keys.

## Roadmap

1. **Phase 1 (this delivery):** identity service + CIS shell with Operations,
   Consumption, Identity Admin. Client-side gating. Admin-managed accounts.
2. **Phase 2:** server-side permission enforcement on maintenance reads
   (snippet above); self-service password change; audit log of logins.
3. **Phase 3:** fold more platforms (quality, etc.) in as modules; add pricing to
   Consumption; single desktop CIS app replacing separate manager apps.
```
