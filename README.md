# carbo-identity

Standalone authentication & permissions service for the Carbo cloud. People log
in here and receive a session token; other services (maintenance, quality) check
that token and its permissions. **Device keys stay per-platform** for PWA writes —
this service is only about *people*.

## Why separate

- One place to create/disable a person and instantly kill their sessions.
- One login for the manager viewer (CIS shell) instead of many device keys.
- Permission-gated: each person sees only the modules their role allows.
- A clean foundation for the full Carbo Integrated System (CIS).

## Layout

```
identity_api/
  app/
    main.py            FastAPI app (root_path /identity/api)
    config.py          env + pepper + session TTL
    db.py              psycopg2 connection (carbo_identity DB)
    security.py        pbkdf2 password hashing + token hashing
    permissions.py     PERMISSION CATALOG + default roles  <-- add new capabilities here
    services/
      users.py         users, roles, role_permissions, user_roles
      auth.py          login, token resolve/introspect, logout
    deps/auth.py       get_current_user / require_permission
    api/
      health.py        /health, /schema_version
      auth.py          /auth/login, /auth/logout, /auth/me
      admin.py         /users, /roles, /permissions  (require identity.admin)
  schema_identity.sql  tables
  seed_identity.py     default roles + bootstrap admin
  requirements.txt
  .env.example
  carbo-identity.service
nginx_identity.conf
DEPLOY.md
```

## Concepts

- **User** — a person with `login_id` + password (pbkdf2, peppered, salted).
- **Role** — a named bundle of permissions (admin / operations / finance seeded).
- **Permission** — namespaced string, e.g. `maintenance.fuel.view`. See
  `app/permissions.py`. Effective permissions of a user = union across their roles.
- **Session** — random token; only its hash is stored; TTL from `SESSION_TTL_HOURS`.

## API

| Method | Path                          | Auth              | Purpose |
|--------|-------------------------------|-------------------|---------|
| POST   | `/auth/login`                 | none              | `{login_id, password}` → `{token, user, permissions, expires_at}` |
| POST   | `/auth/logout`                | bearer            | revoke current token |
| GET    | `/auth/me`                    | bearer            | introspect: user + permissions |
| GET    | `/permissions`                | `identity.admin`  | permission catalog |
| GET    | `/users`                      | `identity.admin`  | list users (+roles, +permissions) |
| POST   | `/users`                      | `identity.admin`  | create user (`login_id, display_name, password, role_ids?`) |
| PATCH  | `/users/{id}`                 | `identity.admin`  | update name/status/password/roles |
| GET    | `/roles`                      | `identity.admin`  | list roles + their permissions |
| POST   | `/roles`                      | `identity.admin`  | create role |
| PUT    | `/roles/{id}/permissions`     | `identity.admin`  | set a role's permissions |

Send the token as `Authorization: Bearer <token>` (or `X-Auth-Token: <token>`).

## Local run

```bash
cd identity_api
python -m venv .venv && .venv\Scripts\pip install -r requirements.txt   # Windows
set IDENTITY_SECRET_PEPPER=dev-pepper
set DATABASE_URL=postgresql://postgres:password@localhost:5432/carbo_identity
.venv\Scripts\python seed_identity.py
.venv\Scripts\uvicorn app.main:app --port 8003
```

Then browse `http://localhost:8003/docs`.
