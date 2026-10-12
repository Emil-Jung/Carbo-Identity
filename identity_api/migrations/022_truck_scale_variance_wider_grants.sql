-- production.truck_scale_variance — grant to production + traceability office users
-- (021 only copied deliveries_register; many investigators use bags_status / hub access).

INSERT INTO user_permissions (user_id, permission)
SELECT DISTINCT user_id, 'production.truck_scale_variance'
FROM user_permissions
WHERE permission IN (
  'production.deliveries_register',
  'traceability.bags_status',
  'traceability.delivery_confirmations',
  'traceability.access'
)
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission)
SELECT DISTINCT role_id, 'production.truck_scale_variance'
FROM role_permissions
WHERE permission IN (
  'production.deliveries_register',
  'traceability.bags_status',
  'traceability.delivery_confirmations',
  'traceability.access'
)
ON CONFLICT DO NOTHING;
