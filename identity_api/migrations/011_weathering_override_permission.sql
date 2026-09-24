-- Manager Override: daily PIN for weathering early-release on yard scanners.
-- Permission is defined in app/permissions.py. Grant to PJ here; others via CIS → Users & access.

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.weathering.override'
FROM users
WHERE lower(login_id) = 'pjs'
ON CONFLICT DO NOTHING;
