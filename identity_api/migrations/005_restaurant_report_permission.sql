-- New CIS tile: Restaurant quality report (separate from Quality Analysis viewer).

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'quality.restaurant_report'
FROM user_permissions
WHERE permission = 'quality.view'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission)
SELECT role_id, 'quality.restaurant_report'
FROM role_permissions
WHERE permission = 'quality.view'
ON CONFLICT DO NOTHING;
