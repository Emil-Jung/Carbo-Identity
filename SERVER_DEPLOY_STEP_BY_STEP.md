# Big-K — first-time deploy: carbo-identity + CIS

**One step at a time.** Do not continue until the **Verify** line for that step succeeds.

SSH: `bkweb3dev@192.168.89.101` (VPN on).  
Public host: `bkweb3.bigk.co.uk`

---

## Where you are now (if identity setup already ran)

You may already have completed **Steps 1–8** (repo, DB, `.env`, seed, systemd).  
Local API works: `curl -s --max-time 3 http://127.0.0.1:8004/health` → `carbo-identity`

**Your next step is Step 9** (nginx for identity only). Do not upload CIS until Step 9 passes in a browser.

---

## Step 1 — Clone the repo

```bash
cd /opt/carbo
git clone https://github.com/Emil-Jung/Carbo-Identity.git carbo-identity
```

**Verify:**

```bash
test -f /opt/carbo/carbo-identity/identity_api/app/main.py && echo OK
```

---

## Step 2 — Create database and tables

```bash
cd /opt/carbo/carbo-identity/identity_api
bash bootstrap_on_server.sh
```

**Verify:** ends with `Bootstrap done.` (NOTICE “already exists” is fine on re-run)

---

## Step 3 — PostgreSQL role for the app

```bash
cd /opt/carbo/carbo-identity/identity_api
bash setup_db_user.sh
```

**Verify:**

```bash
psql -d carbo_identity -c 'SELECT 1'
```

Expect a row with `1`. If “role bkweb3dev does not exist”, this step failed — do not continue.

---

## Step 4 — Create `.env` (secrets)

```bash
cd /opt/carbo/carbo-identity/identity_api
python3 generate_env_secrets.py --force
```

**Verify:** prints **User ID** and **Password** — write them down (CIS login later).

```bash
grep -q '^IDENTITY_SECRET_PEPPER=' .env && grep -v 'change-me' .env | grep -q IDENTITY_SECRET_PEPPER && echo OK
```

---

## Step 5 — Python virtual environment

```bash
cd /opt/carbo/carbo-identity/identity_api
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**Verify:**

```bash
.venv/bin/python -c "import fastapi; print('OK')"
```

---

## Step 6 — Seed roles and carbo_user

```bash
cd /opt/carbo/carbo-identity/identity_api
.venv/bin/python seed_identity.py
```

**Verify:** ends with `Done.` and either `Created admin user 'carbo_user'` or `already exists`.

```bash
sudo -u postgres psql -d carbo_identity -c "SELECT login_id FROM users;"
```

Expect `carbo_user` in the list.

---

## Step 7 — Start systemd service

```bash
cd /opt/carbo/carbo-identity/identity_api
bash install_service_on_server.sh
```

**Verify:**

```bash
curl -s --max-time 3 http://127.0.0.1:8004/health
```

Must show: `{"status":"ok","service":"carbo-identity"}`  
Must **not** show `producers-api` (that is port 8003).

---

## Step 8 — Login on localhost (no nginx yet)

Use the User ID and password from Step 4:

```bash
cd /opt/carbo/carbo-identity/identity_api
.venv/bin/python - <<'PY'
import json, os, urllib.request
from dotenv import load_dotenv
load_dotenv(".env")
body = json.dumps({
    "login_id": os.environ.get("BOOTSTRAP_ADMIN_LOGIN", "carbo_user"),
    "password": os.environ["BOOTSTRAP_ADMIN_PASSWORD"],
}).encode()
req = urllib.request.Request("http://127.0.0.1:8004/auth/login", data=body,
    headers={"Content-Type": "application/json"}, method="POST")
print(urllib.request.urlopen(req, timeout=10).read().decode()[:200])
PY
```

**Verify:** output contains `"token"`.  
If this fails, fix before nginx — nginx cannot fix a broken API.

---

## Step 9 — nginx: expose identity on HTTPS

**This is the step that fixes browser 404.** Nothing public works until this is done.

```bash
sudo nano /etc/nginx/sites-available/maintenance-platform
```

Inside the **`server { }`** block that has `server_name bkweb3.bigk.co.uk;` and `listen 443 ssl;`, add:

```nginx
    location /identity/api/ {
        proxy_pass http://127.0.0.1:8004/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
```

Save. Then:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

**Verify (browser on your PC — not curl if it hangs):**

Open: https://bkweb3.bigk.co.uk/identity/api/health  

Must show JSON: `{"status":"ok","service":"carbo-identity"}`  

**Stop here until that URL works.** CIS and public login depend on this.

---

## Step 10 — Public login test (browser)

Open: https://bkweb3.bigk.co.uk/identity/api/docs  

1. **POST /auth/login** → Try it out  
2. Body: `{"login_id":"carbo_user","password":"YOUR_PASSWORD_FROM_STEP_4"}`  
3. Execute → must return `"token"`

**Verify:** `"token"` in response.  
Then identity deploy is **complete**.

---

## Step 11 — CIS folders on server

```bash
cd /opt/carbo
git clone https://github.com/Emil-Jung/Carbo-CIS.git carbo-cis
bash /opt/carbo/carbo-cis/setup_cis_server_dirs.sh
```

**Verify:**

```bash
ls -la /opt/carbo/cis/app /opt/carbo/cis/shell
```

---

## Step 12 — nginx: CIS installer URL

Edit the same nginx file as Step 9. Add **after** the identity block:

```nginx
    location /cis/app/ {
        alias /opt/carbo/cis/app/;
        default_type application/octet-stream;
        add_header Cache-Control "no-store";
    }
```

```bash
sudo nginx -t
sudo systemctl reload nginx
```

**Verify:** opening https://bkweb3.bigk.co.uk/cis/app/ may 403/404 until Step 13 — that is OK for now.  
After Step 13, `version.json` must load.

---

## Step 13 — Upload CIS installer (from your Windows PC)

On your PC (VPN on), after building/staging:

```powershell
cd "G:\My Coding Projects\Carbo-CIS"
UPLOAD-CIS-TO-SERVER.cmd
```

On the server:

```bash
sudo cp ~/cis_app_upload/* /opt/carbo/cis/app/
ls -la /opt/carbo/cis/app/
```

**Verify (browser):**  
https://bkweb3.bigk.co.uk/cis/app/version.json  

Must show JSON with `"version": "1.0.0"` (or your current version).

---

## Step 14 — Install CIS on a PC and sign in

1. Run `CarboCIS-Setup.exe` (from build folder or download URL above).  
2. User ID: `carbo_user`  
3. Password: from Step 4  

**Verify:** login screen → modules visible (Identity Admin, etc.).

---

## Step 15 — Create Simon and Juliana (later)

In CIS → **Identity Admin** → new users, roles `operations` and `finance`.

---

## If something fails

| Failed step | Do not proceed to |
|-------------|-------------------|
| Step 7–8 | Step 9 (nginx) |
| Step 9 | Step 10–14 |
| Step 13 | Step 14 (CIS cannot update/login to cloud) |

Fix the failed step only. Re-run its **Verify** before continuing.
