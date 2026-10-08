# Adding a CIS permission — default OFF

Every new capability gets a catalog entry in `identity_api/app/permissions.py`.
**Nobody receives it until an administrator ticks the box** (or a migration names
specific `login_id` values).

## Do

1. Add one row to `PERMISSION_CATALOG` (`parent` = module id for nested options under a tile).
2. Wire CIS: `requires: "your.permission.key"` on the module or Traceability hub option.
3. Wire API: `_require_identity_permission(..., "your.permission.key")`.
4. Optional migration: grant **named users only**:
   ```sql
   INSERT INTO user_permissions (user_id, permission)
   SELECT user_id, 'your.permission.key'
   FROM users
   WHERE lower(login_id) IN ('someone')
   ON CONFLICT DO NOTHING;
   ```

## Do not

- `INSERT … SELECT … FROM user_permissions WHERE permission = 'traceability.access'` (or any broad copy).
- Add sensitive permissions to `operations`, `production_office`, or other default role templates.
- Assume `git pull` on Identity grants the permission — catalog alone changes checkboxes, not assignments.

## Admin role note

Re-running `seed_identity.py` refreshes the **admin** role with every key in
`ALL_PERMISSIONS`. For highly restricted tools, prefer **user-level** grants in
Users & access rather than assigning the admin role on shared accounts.

## After deploy

```bash
cd /opt/carbo/carbo-identity && git pull && sudo systemctl restart carbo-identity
```

Users must **sign out and in** for CIS to reload permissions.
