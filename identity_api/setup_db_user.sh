#!/bin/bash
# Create PostgreSQL role bkweb3dev for carbo_identity (peer auth, same OS user as systemd).
# Run ONCE on Big-K as a user that can sudo to postgres:
#
#   cd /opt/carbo/carbo-identity/identity_api
#   bash setup_db_user.sh
#
# Then: .venv/bin/python seed_identity.py

set -e
DB_NAME="${PGDATABASE:-carbo_identity}"
OS_USER="${APP_DB_USER:-bkweb3dev}"

echo "=== carbo-identity DB user: $OS_USER on database $DB_NAME ==="

sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '${OS_USER}') THEN
    CREATE ROLE ${OS_USER} WITH LOGIN;
    RAISE NOTICE 'Created role ${OS_USER}';
  ELSE
    RAISE NOTICE 'Role ${OS_USER} already exists';
  END IF;
END
\$\$;

GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${OS_USER};
SQL

sudo -u postgres psql -v ON_ERROR_STOP=1 -d "$DB_NAME" <<SQL
GRANT ALL ON SCHEMA public TO ${OS_USER};
GRANT ALL ON ALL TABLES IN SCHEMA public TO ${OS_USER};
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO ${OS_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${OS_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${OS_USER};
SQL

echo ""
echo "Done. Test connection:"
echo "  psql -d ${DB_NAME} -c 'SELECT 1'"
echo "Then:"
echo "  .venv/bin/python seed_identity.py"
