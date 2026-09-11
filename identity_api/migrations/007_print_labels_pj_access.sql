-- Print Labels: grant Traceability hub + Print Labels to PJS when that user exists.
-- Does not hard-code PJS as the only authorised person — admins assign via Users & access.

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.access'
FROM users
WHERE lower(login_id) = 'pjs'
ON CONFLICT DO NOTHING;

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.labels.print'
FROM users
WHERE lower(login_id) = 'pjs'
ON CONFLICT DO NOTHING;
