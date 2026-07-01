#!/bin/bash
# One-time carbo-identity database setup on Big-K.
# Run ON the server after git clone and BEFORE seed_identity.py / systemd.
#
#   cd /opt/carbo/carbo-identity/identity_api
#   bash bootstrap_on_server.sh
#
# Creates database carbo_identity (if missing) and applies schema_identity.sql.
# Uses sudo -u postgres (same style as maintenance migrations).

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DB_NAME="${PGDATABASE:-carbo_identity}"

echo "=== carbo-identity bootstrap ==="
echo "Database: $DB_NAME"

if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
  echo "Creating database $DB_NAME ..."
  sudo -u postgres createdb "$DB_NAME"
else
  echo "Database $DB_NAME already exists."
fi

echo "Applying schema_identity.sql ..."
cat schema_identity.sql | sudo -u postgres psql -d "$DB_NAME"

echo ""
echo "Bootstrap done."
echo "Next:"
echo "  1. bash setup_db_user.sh          (creates PostgreSQL role bkweb3dev — once)"
echo "  2. python3 generate_env_secrets.py   OR  cp .env.example .env && nano .env"
echo "  3. .venv/bin/python seed_identity.py"
echo "  4. bash install_service_on_server.sh"
