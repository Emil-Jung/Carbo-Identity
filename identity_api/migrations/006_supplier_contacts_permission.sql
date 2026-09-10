-- New CIS tile: Supplier contacts (dormant supplier call list).

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'production.supplier_contacts'
FROM user_permissions
WHERE permission = 'quality.restaurant_report'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission)
SELECT role_id, 'production.supplier_contacts'
FROM role_permissions
WHERE permission = 'quality.restaurant_report'
ON CONFLICT DO NOTHING;
