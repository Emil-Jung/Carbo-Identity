-- Traceability hub: nested options under the Traceability dashboard tile.
-- Stock is the common option — grant it to anyone who already has the hub.
-- Do NOT grant bag-label printing here; that is assigned per person.

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.stock.view'
FROM user_permissions
WHERE permission = 'traceability.access'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission)
SELECT role_id, 'traceability.stock.view'
FROM role_permissions
WHERE permission = 'traceability.access'
ON CONFLICT DO NOTHING;
