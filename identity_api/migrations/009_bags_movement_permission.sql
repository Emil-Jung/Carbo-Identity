-- CIS report tile: Bags Movement (daily sieve scan-in).

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.bags_movement'
FROM user_permissions
WHERE permission IN (
    'traceability.access',
    'traceability.stock.view',
    'quality.view',
    'producers.view'
)
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission)
SELECT role_id, 'traceability.bags_movement'
FROM role_permissions
WHERE permission IN (
    'traceability.access',
    'traceability.stock.view',
    'quality.view',
    'producers.view'
)
ON CONFLICT DO NOTHING;
