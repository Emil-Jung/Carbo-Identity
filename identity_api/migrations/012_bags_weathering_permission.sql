-- Weathering Board CIS tile (traceability.bags_weathering).
-- Grant to anyone who already has Bags Status — same office audience.

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.bags_weathering'
FROM user_permissions
WHERE permission = 'traceability.bags_status'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission)
SELECT role_id, 'traceability.bags_weathering'
FROM role_permissions
WHERE permission = 'traceability.bags_status'
ON CONFLICT DO NOTHING;
