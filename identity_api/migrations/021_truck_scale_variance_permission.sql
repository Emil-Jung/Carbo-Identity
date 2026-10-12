-- production.truck_scale_variance — digital scale vs Charcoal intake investigation report.

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'production.truck_scale_variance'
FROM user_permissions
WHERE permission = 'production.deliveries_register'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission)
SELECT role_id, 'production.truck_scale_variance'
FROM role_permissions
WHERE permission = 'production.deliveries_register'
ON CONFLICT DO NOTHING;
