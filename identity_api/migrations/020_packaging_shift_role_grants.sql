-- Packaging shift: same roles (and any missed users) as Movement schedule.

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.packaging_shift'
FROM user_permissions
WHERE permission = 'traceability.movement_jobs'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission)
SELECT role_id, 'traceability.packaging_shift'
FROM role_permissions
WHERE permission = 'traceability.movement_jobs'
ON CONFLICT DO NOTHING;
