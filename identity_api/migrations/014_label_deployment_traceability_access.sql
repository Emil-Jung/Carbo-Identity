-- Label Deployment: grant to anyone with Traceability hub access (office staff).
-- Migration 013 copied from Print Labels only; this covers users who have the hub but not print.

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.labels.deployment'
FROM user_permissions
WHERE permission = 'traceability.access'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission)
SELECT role_id, 'traceability.labels.deployment'
FROM role_permissions
WHERE permission = 'traceability.access'
ON CONFLICT DO NOTHING;
