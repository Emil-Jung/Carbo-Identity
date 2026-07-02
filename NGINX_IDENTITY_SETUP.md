# nginx — add carbo-identity (fix 404 on /identity/api/)

Identity works locally (`curl http://127.0.0.1:8004/health`). A **404 from nginx** means the
`/identity/api/` location block was never added (or is in the wrong `server { }` block).

Run on Big-K (SSH). Editing nginx needs **sudo**.

---

## 1. Confirm local API still OK

```bash
curl -s --max-time 3 http://127.0.0.1:8004/health
```

Expect: `{"status":"ok","service":"carbo-identity"}`

---

## 2. Check if identity is in nginx today

```bash
sudo grep -n "identity" /etc/nginx/sites-available/maintenance-platform
sudo grep -n "8004" /etc/nginx/sites-available/
```

If **no output** → block not added yet (your situation).

---

## 3. Add the location block

```bash
sudo nano /etc/nginx/sites-available/maintenance-platform
```

Find the **`server { }`** block that has:

- `server_name bkweb3.bigk.co.uk;`
- `listen 443 ssl;`
- existing `location /maintenance/api/ { ... }`

**Inside that same server block**, add (e.g. after the maintenance API block):

```nginx
    # --- Identity API (carbo-identity on 127.0.0.1:8004) ---
    location /identity/api/ {
        proxy_pass http://127.0.0.1:8004/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
```

**Important:** `proxy_pass` must end with **`/`** (trailing slash), port **8004** (not 8003 — that is producers-api).

Save and exit.

---

## 4. Test and reload

```bash
sudo nginx -t
sudo systemctl reload nginx
```

If `nginx -t` fails, fix the typo before reload.

---

## 5. Verify

**From your PC browser** (best — this is the real public path):

- https://bkweb3.bigk.co.uk/identity/api/health

**From the server:** do **not** curl the public hostname (often hangs — no NAT hairpin). Use localhost:

```bash
curl -s --max-time 3 http://127.0.0.1:8004/health
curl -s --max-time 5 -k -H 'Host: bkweb3.bigk.co.uk' https://127.0.0.1/identity/api/health
```

---

## Still 404?

| Check | Command |
|-------|---------|
| Block in enabled site? | `ls -la /etc/nginx/sites-enabled/` → should link to `maintenance-platform` |
| Wrong server block? | `sudo nginx -T \| grep -A2 "identity/api"` |
| Typo in path | URL must be **`/identity/api/health`** not `/identity/health` |
| Maintenance API works? | https://bkweb3.bigk.co.uk/maintenance/api/health — if this also 404, whole site config issue |

---

## CIS app

After `/identity/api/health` works in the browser, CIS login from a PC will work (it calls the same HTTPS URL).

See also: `nginx_identity.conf` in this repo, `Carbo-CIS/nginx_cis.conf` for `/cis/app/` (installer downloads).
