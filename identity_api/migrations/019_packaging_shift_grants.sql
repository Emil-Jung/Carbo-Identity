-- Packaging shift: grant to floor managers who already run Movement schedule,
-- plus Emil / PieterJan (same pattern as pallet configuration).

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.packaging_shift'
FROM user_permissions
WHERE permission = 'traceability.movement_jobs'
ON CONFLICT DO NOTHING;

INSERT INTO user_permissions (user_id, permission)
SELECT user_id, 'traceability.packaging_shift'
FROM users
WHERE lower(login_id) IN ('emilj', 'pieterjans', 'pjs')
ON CONFLICT DO NOTHING;
