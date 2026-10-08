-- Pallet Configuration: grant to Control Room and Print Labels users (catalog managers).

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.pallet_configuration'
FROM user_permissions
WHERE permission IN (
    'traceability.access',
    'traceability.control_room',
    'traceability.labels.print',
    'traceability.stock.view'
)
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission)
SELECT role_id, 'traceability.pallet_configuration'
FROM role_permissions
WHERE permission IN (
    'traceability.access',
    'traceability.control_room',
    'traceability.labels.print',
    'traceability.stock.view'
)
ON CONFLICT DO NOTHING;
