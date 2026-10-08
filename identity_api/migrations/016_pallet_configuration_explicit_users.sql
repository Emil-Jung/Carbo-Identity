-- Pallet Configuration: default OFF for everyone.
-- Revoke any bulk grants (e.g. from an earlier wide migration) and grant only named users.

DELETE FROM role_permissions
WHERE permission = 'traceability.pallet_configuration';

DELETE FROM user_permissions
WHERE permission = 'traceability.pallet_configuration';

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.pallet_configuration'
FROM users
WHERE lower(login_id) IN ('emilj', 'pjs', 'pieterjans')
ON CONFLICT DO NOTHING;
