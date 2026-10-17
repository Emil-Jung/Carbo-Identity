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
( cd identity_api && bash run_migrations.sh )

echo ""
echo "--- seed roles ---"
cd identity_api
unset DATABASE_URL
.venv/bin/python seed_identity.py

echo ""
echo "--- restart API ---"
mkdir -p "$REPO_ROOT/logs"
restart_ok=0
if systemctl is-active --quiet carbo-identity 2>/dev/null; then
  if sudo systemctl restart carbo-identity 2>/dev/null; then
    sleep 1
    if systemctl is-active --quiet carbo-identity; then
      restart_ok=1
      echo "carbo-identity: running (systemd)"
    fi
  fi
fi
if [[ "$restart_ok" -ne 1 ]]; then
  if [[ ! -x "$REPO_ROOT/identity_api/.venv/bin/uvicorn" ]]; then
    echo "ERROR: carbo-identity not running and identity_api/.venv/bin/uvicorn missing."
    exit 1
  fi
  if command -v fuser >/dev/null 2>&1; then
    fuser -k 8004/tcp 2>/dev/null || true
    sleep 2
  fi
  echo "Starting API manually (systemd inactive or sudo restart unavailable)..."
  cd "$REPO_ROOT/identity_api"
  nohup .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8004 >> "$REPO_ROOT/logs/uvicorn.log" 2>&1 &
  sleep 2
  if curl -sf http://127.0.0.1:8004/health >/dev/null; then
    restart_ok=1
    echo "carbo-identity: running (manual uvicorn — see logs/uvicorn.log)"
  else
    echo "ERROR: API did not start on port 8004. Last log lines:"
    tail -30 "$REPO_ROOT/logs/uvicorn.log" 2>/dev/null || true
    exit 1
  fi
fi

echo ""
echo "--- health ---"
curl -sf http://127.0.0.1:8004/health && echo "" || echo "API health check failed"

echo ""
echo "Done. Public health: https://bkweb3.bigk.co.uk/identity/api/health"
