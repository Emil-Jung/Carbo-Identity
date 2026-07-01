# Big-K server — first-time setup: carbo-identity + CIS
#
# Run these steps ON the server (VPN → ssh bkweb3dev@192.168.89.101).
# Canonical reference: Maintenance-Platform/BIG_K_SERVER.md
#
# =============================================================================
# OVERVIEW
# =============================================================================
#
#   /opt/carbo/carbo-identity/     git: Carbo-Identity  →  API :8004
#   /opt/carbo/carbo-cis/          git: Carbo-CIS       →  shell source (optional)
#   /opt/carbo/cis/app/            CIS installer + version.json (upload from PC)
#   /opt/carbo/cis/shell/          optional web copy of shell/
#
# Public URLs after nginx:
#   https://bkweb3.bigk.co.uk/identity/api/health
#   https://bkweb3.bigk.co.uk/cis/app/version.json
#
# =============================================================================
# PART A — Clone repos (once)
# =============================================================================
#
# If /opt/carbo does not exist or bkweb3dev cannot write there, ask admin once:
#   sudo mkdir -p /opt/carbo
#   sudo chown bkweb3dev:bkweb3dev /opt/carbo
#
cd /opt/carbo

git clone https://github.com/Emil-Jung/Carbo-Identity.git carbo-identity
git clone https://github.com/Emil-Jung/Carbo-CIS.git carbo-cis
#
# Private repos: use a GitHub PAT or deploy key if clone asks for credentials.
#
# =============================================================================
# PART B — carbo-identity (API + database)
# =============================================================================
#
cd /opt/carbo/carbo-identity/identity_api

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

bash bootstrap_on_server.sh
# Creates DB carbo_identity + applies schema_identity.sql

cp .env.example .env
nano .env
# Set IDENTITY_SECRET_PEPPER (long random string). Save.

.venv/bin/python seed_identity.py
# SAVE THE PRINTED ADMIN PASSWORD (shown once).

bash install_service_on_server.sh
# Installs systemd unit, starts carbo-identity on 127.0.0.1:8004

curl -s http://127.0.0.1:8004/health
# Expect: {"status":"ok","service":"carbo-identity"}
#
# =============================================================================
# PART C — CIS directories (static + app updates)
# =============================================================================
#
cd /opt/carbo/carbo-cis
bash setup_cis_server_dirs.sh

# Optional: publish web shell for browser testing
cp -r shell/* /opt/carbo/cis/shell/
#
# Upload installer from your Windows PC (VPN on):
#   Carbo-CIS\UPLOAD-CIS-TO-SERVER.cmd
# Then on server:
#   sudo cp ~/cis_app_upload/* /opt/carbo/cis/app/
#
# =============================================================================
# PART D — Nginx (once, needs sudo)
# =============================================================================
#
sudo nano /etc/nginx/sites-available/maintenance-platform
#
# Add INSIDE the existing server { } block for bkweb3.bigk.co.uk:
#   - Carbo-Identity/nginx_identity.conf   →  /identity/api/
#   - Carbo-CIS/nginx_cis.conf             →  /cis/app/ and /cis/
#
sudo nginx -t && sudo systemctl reload nginx
#
curl -s https://bkweb3.bigk.co.uk/identity/api/health
curl -s https://bkweb3.bigk.co.uk/cis/app/version.json
#
# =============================================================================
# ROUTINE UPDATES (after first setup)
# =============================================================================
#
# Identity code:
#   cd /opt/carbo/carbo-identity && git pull
#   cd identity_api && bash install_service_on_server.sh
#   # New SQL: cat identity_api/some_migration.sql | sudo -u postgres psql -d carbo_identity
#
# CIS installer (from Windows PC after BUILD + stage):
#   UPLOAD-CIS-TO-SERVER.cmd  →  sudo cp ~/cis_app_upload/* /opt/carbo/cis/app/
#
# CIS shell only (optional web copy):
#   cd /opt/carbo/carbo-cis && git pull
#   cp -r shell/* /opt/carbo/cis/shell/
#
# =============================================================================
# SMOKE TEST
# =============================================================================
#
# 1. Install CarboCIS-Setup.exe on a PC (or use existing test install).
# 2. Login as admin (password from seed_identity.py).
# 3. Identity Admin → create Simon (operations), Juliana (finance).
# 4. CIS shows correct modules per user.
