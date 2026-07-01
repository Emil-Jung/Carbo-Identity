# carbo-identity — deploy (Big-K server)

Canonical server reference: `Maintenance-Platform/BIG_K_SERVER.md`.
SSH: `ssh bkweb3dev@192.168.89.101` (VPN on). Public host: `bkweb3.bigk.co.uk`.

Identity is a **standalone service** with its **own database**. It never shares a
database with maintenance or quality.

| Thing            | Value                                         |
|------------------|-----------------------------------------------|
| Code dir         | `/opt/carbo/carbo-identity`                    |
| Service (uvicorn)| `127.0.0.1:8003`, systemd unit `carbo-identity`|
| Public API       | `https://bkweb3.bigk.co.uk/identity/api/`      |
| Database         | `carbo_identity` (Postgres, peer/local)        |

## 1. Get the code on the server

```bash
sudo mkdir -p /opt/carbo/carbo-identity
sudo chown -R bkweb3dev:bkweb3dev /opt/carbo/carbo-identity
# then git clone / rsync the Carbo-Identity project into /opt/carbo/carbo-identity
cd /opt/carbo/carbo-identity/identity_api
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 2. Create the database

```bash
sudo -u postgres createdb carbo_identity
sudo -u postgres createuser carbo_identity            # if using a role
# Peer/local auth (matches maintenance style). Adjust DATABASE_URL in .env to taste.
cat schema_identity.sql | sudo -u postgres psql -d carbo_identity
```

## 3. Configure secrets

```bash
cp .env.example .env
# EDIT .env:
#   IDENTITY_SECRET_PEPPER=<a long random string>   <-- REQUIRED, keep secret
#   DATABASE_URL=...                                  <-- point at carbo_identity
nano .env
```

Generate a pepper: `python3 -c "import secrets;print(secrets.token_urlsafe(48))"`

## 4. Seed roles + bootstrap admin

```bash
cd /opt/carbo/carbo-identity/identity_api
.venv/bin/python seed_identity.py
# Copy the printed ADMIN PASSWORD (shown once) if you did not set BOOTSTRAP_ADMIN_PASSWORD.
```

## 5. Run as a service

```bash
sudo cp carbo-identity.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now carbo-identity
sudo systemctl status carbo-identity
curl -s http://127.0.0.1:8003/health
```

## 6. Nginx

Add the blocks from `nginx_identity.conf` into the existing HTTPS server block for
`bkweb3.bigk.co.uk`, then:

```bash
sudo nginx -t && sudo systemctl reload nginx
curl -s https://bkweb3.bigk.co.uk/identity/api/health
```

## Updating later

```bash
cd /opt/carbo/carbo-identity && git pull
cd identity_api && .venv/bin/pip install -r requirements.txt
# apply any new schema_*.sql, then:
sudo systemctl restart carbo-identity
```

## How other services check tokens (introspection)

A service (e.g. maintenance API) that wants to enforce a permission on a read
endpoint calls identity with the caller's bearer token:

```
GET https://bkweb3.bigk.co.uk/identity/api/auth/me
Authorization: Bearer <token>
```

200 → JSON `{user_id, login_id, display_name, permissions[]}`; check the permission.
401 → invalid/expired. Cache the positive result ~5–15 min to survive brief outages.
