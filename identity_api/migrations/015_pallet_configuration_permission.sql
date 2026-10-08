-- Pallet Configuration permission is defined in app/permissions.py (catalog checkbox).
-- Grant explicitly per user in CIS → Users & access, or run scripts/grant_pallet_configuration_permissions.sql on traceability repo.

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.pallet_configuration'
FROM users
WHERE lower(login_id) = 'pjs'
ON CONFLICT DO NOTHING;
