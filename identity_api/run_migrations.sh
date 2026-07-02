#!/bin/bash
# Apply DB migrations after git pull (run on server from identity_api dir).
set -e
cd "$(dirname "$0")"
if [[ -z "${DATABASE_URL:-}" ]]; then
  if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
  fi
fi
if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "Set DATABASE_URL or create .env"
  exit 1
fi
for f in migrations/*.sql; do
  echo ">> $f"
  psql "$DATABASE_URL" -f "$f"
done
echo "Done."
