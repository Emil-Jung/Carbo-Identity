-- Control Room: grant nested option to anyone who already has the Traceability hub.
-- Admins can remove or assign individually via Users & access.

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.control_room'
FROM user_permissions
WHERE permission = 'traceability.access'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission)
SELECT role_id, 'traceability.control_room'
FROM role_permissions
WHERE permission = 'traceability.access'
ON CONFLICT DO NOTHING;
