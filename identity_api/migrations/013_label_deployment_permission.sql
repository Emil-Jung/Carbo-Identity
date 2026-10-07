-- Label Deployment: grant to anyone who already has Print Labels (office can record excisions).

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.labels.deployment'
FROM user_permissions
WHERE permission = 'traceability.labels.print'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission)
SELECT role_id, 'traceability.labels.deployment'
FROM role_permissions
WHERE permission = 'traceability.labels.print'
ON CONFLICT DO NOTHING;
