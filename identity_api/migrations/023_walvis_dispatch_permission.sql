-- traceability.walvis_dispatch — Walvis Bay dispatch tile + API (catalog in permissions.py).
-- Default OFF; grant named users only. Do not copy from traceability.access or bags_status.

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.walvis_dispatch'
FROM users
WHERE lower(login_id) IN ('pieterjans')
ON CONFLICT DO NOTHING;

-- PJ (pjs) never had this key; clear if it was toggled manually by mistake.
DELETE FROM user_permissions up
USING users u
WHERE up.user_id = u.user_id
  AND lower(u.login_id) = 'pjs'
  AND up.permission = 'traceability.walvis_dispatch';
