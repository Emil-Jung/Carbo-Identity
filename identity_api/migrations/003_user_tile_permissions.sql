-- Per-user CIS tile permissions (individual access beyond or instead of roles).
-- Effective access = user_permissions if any rows, else permissions from roles (legacy).

CREATE TABLE IF NOT EXISTS user_permissions (
    user_id    INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    permission TEXT NOT NULL,
    PRIMARY KEY (user_id, permission)
);

CREATE INDEX IF NOT EXISTS idx_user_permissions_user ON user_permissions(user_id);
