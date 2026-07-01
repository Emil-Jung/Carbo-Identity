#!/bin/bash
# Install/update carbo-identity Python venv + systemd service on Big-K.
# Run after git pull when code or requirements change.
#
#   cd /opt/carbo/carbo-identity/identity_api
#   bash install_service_on_server.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -f .env ]]; then
  echo "ERROR: .env missing. Copy from .env.example and set IDENTITY_SECRET_PEPPER first."
  exit 1
fi

echo "=== carbo-identity install ==="

if [[ ! -d .venv ]]; then
  echo "Creating venv ..."
  python3 -m venv .venv
fi

echo "Installing requirements ..."
.venv/bin/pip install -q -r requirements.txt

echo "Installing systemd unit ..."
sudo cp carbo-identity.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable carbo-identity
sudo systemctl restart carbo-identity

sleep 1
echo ""
echo "Health check:"
curl -s http://127.0.0.1:8004/health || true
echo ""
sudo systemctl status carbo-identity --no-pager -l | head -15
