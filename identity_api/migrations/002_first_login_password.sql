-- Invite flow: users can be created without a password and set one on first CIS sign-in.
-- Run once on existing DB:
--   psql "$DATABASE_URL" -f migrations/002_first_login_password.sql

ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;

ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN NOT NULL DEFAULT FALSE;

-- Invited users (no password yet)
UPDATE users SET must_change_password = TRUE WHERE password_hash IS NULL;
