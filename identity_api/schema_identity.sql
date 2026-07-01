-- carbo-identity schema (own database: carbo_identity)
-- Run once:  cat identity_api/schema_identity.sql | sudo -u postgres psql -d carbo_identity

-- People who log in (NOT devices/PWAs — those keep using device keys per platform).
CREATE TABLE IF NOT EXISTS users (
    user_id       SERIAL PRIMARY KEY,
    login_id      TEXT NOT NULL UNIQUE,          -- what the person types to log in
    display_name  TEXT NOT NULL,
    password_hash TEXT NOT NULL,                 -- pbkdf2_sha256$iterations$salt$hash
    status        TEXT NOT NULL DEFAULT 'active',-- active | disabled
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by    TEXT,
    last_login_at TIMESTAMPTZ
);

-- Roles bundle permissions (e.g. admin, operations, finance).
CREATE TABLE IF NOT EXISTS roles (
    role_id     SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Permission strings granted to a role. Values come from the code catalog (app/permissions.py).
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id    INTEGER NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    permission TEXT NOT NULL,
    PRIMARY KEY (role_id, permission)
);

-- Which roles a user has. Effective permissions = union across the user's roles.
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- Active login sessions. Token is stored hashed (never in plaintext), like device keys.
CREATE TABLE IF NOT EXISTS sessions (
    session_id   SERIAL PRIMARY KEY,
    token_hash   TEXT NOT NULL UNIQUE,
    user_id      INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at   TIMESTAMPTZ NOT NULL,
    last_used_at TIMESTAMPTZ,
    revoked_at   TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);
