#!/bin/bash
# Deploy latest Carbo-Identity from git (run ON bkweb3.bigk.co.uk)
#
# Usage:
#   cd /opt/carbo/carbo-identity
#   bash deploy_on_server.sh

set -e
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

echo "=== Carbo Identity deploy ==="
echo "Repo: $REPO_ROOT"
echo ""

echo "--- git pull ---"
git pull origin master

echo ""
echo "--- Python deps ---"
if [[ -x identity_api/.venv/bin/pip ]]; then
  identity_api/.venv/bin/pip install -r identity_api/requirements.txt -q
else
  echo "WARN: identity_api/.venv not found — run identity_api/bootstrap_on_server.sh first"
fi

echo ""
echo "--- database migrations ---"
bash run_migrations.sh

echo ""
echo "--- seed roles ---"
cd identity_api
unset DATABASE_URL
.venv/bin/python seed_identity.py

echo ""
echo "--- restart API ---"
if systemctl is-active --quiet carbo-identity 2>/dev/null; then
  sudo systemctl restart carbo-identity
  sleep 1
  systemctl is-active carbo-identity && echo "carbo-identity: running"
else
  echo "WARN: carbo-identity service not running — enable with DEPLOY.md"
fi

echo ""
echo "--- health ---"
curl -sf http://127.0.0.1:8004/health && echo "" || echo "API health check failed"

echo ""
echo "Done. Public health: https://bkweb3.bigk.co.uk/identity/api/health"
