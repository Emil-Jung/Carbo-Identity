"""Configuration for carbo-identity (standalone auth service)."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Always prefer identity_api/.env over a shell DATABASE_URL (e.g. producers export).
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
if _ENV_FILE.is_file():
    load_dotenv(_ENV_FILE, override=True)

ENV = os.environ.get("ENV", "dev")
# Identity has its OWN database — never shared with maintenance/quality.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://carbo_identity@/carbo_identity?host=/var/run/postgresql",
)

# Mixed into password and token hashes. Must be set (and kept secret) in production.
SECRET_PEPPER = os.environ.get("IDENTITY_SECRET_PEPPER", "").strip()

# Session token lifetime (hours).
try:
    SESSION_TTL_HOURS = int(os.environ.get("SESSION_TTL_HOURS", "12"))
except ValueError:
    SESSION_TTL_HOURS = 12


def effective_pepper() -> str:
    return SECRET_PEPPER or "carbo-identity-dev-pepper-change-me"
