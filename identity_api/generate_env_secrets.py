#!/usr/bin/env python3
"""
Generate .env secrets for carbo-identity (first-time server setup).

Creates identity_api/.env from .env.example with:
  - IDENTITY_SECRET_PEPPER  (long random — never share)
  - BOOTSTRAP_ADMIN_LOGIN   (default carbo_user)
  - BOOTSTRAP_ADMIN_PASSWORD (random passphrase you can give to staff)

Run on the server after git clone, BEFORE seed_identity.py:

    cd /opt/carbo/carbo-identity/identity_api
    python3 generate_env_secrets.py

Does not overwrite an existing .env unless you pass --force.
"""

from __future__ import annotations

import argparse
import secrets
from pathlib import Path

# Short word list — easy to read aloud / write down (not email, Carbo-style User ID login).
_WORDS = (
    "carbo", "charcoal", "forklift", "harvest", "kiln", "manager", "namibia",
    "quality", "register", "sieve", "trace", "vehicle", "warehouse", "yard",
    "amber", "river", "sunset", "north", "south", "clear", "solid", "secure",
)


def generate_pepper() -> str:
    return secrets.token_urlsafe(48)


def generate_passphrase(word_count: int = 4) -> str:
    """e.g. carbo-river-sunset-secure-7K2 (words + short suffix)."""
    words = [secrets.choice(_WORDS) for _ in range(word_count)]
    suffix = secrets.token_hex(2).upper()  # 4 hex chars
    return "-".join(words) + "-" + suffix


def build_env_text(
    pepper: str,
    login_id: str,
    password: str,
    example_path: Path,
) -> str:
    lines = example_path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    for line in lines:
        if line.startswith("IDENTITY_SECRET_PEPPER="):
            out.append(f"IDENTITY_SECRET_PEPPER={pepper}")
        elif line.startswith("BOOTSTRAP_ADMIN_LOGIN="):
            out.append(f"BOOTSTRAP_ADMIN_LOGIN={login_id}")
        elif line.startswith("BOOTSTRAP_ADMIN_PASSWORD="):
            out.append(f"BOOTSTRAP_ADMIN_PASSWORD={password}")
        else:
            out.append(line)
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate carbo-identity .env secrets")
    parser.add_argument("--login", default="carbo_user", help="Bootstrap User ID (default: carbo_user)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing .env")
    parser.add_argument("--print-only", action="store_true", help="Print values, do not write .env")
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    env_path = here / ".env"
    example_path = here / ".env.example"

    if not example_path.is_file():
        raise SystemExit(f"Missing {example_path}")

    if env_path.is_file() and not args.force and not args.print_only:
        raise SystemExit(
            f"{env_path} already exists. Use --force to replace, or edit it manually."
        )

    pepper = generate_pepper()
    password = generate_passphrase()

    if args.print_only:
        print("Copy into .env (or re-run without --print-only to create .env):\n")
        print(f"IDENTITY_SECRET_PEPPER={pepper}")
        print(f"BOOTSTRAP_ADMIN_LOGIN={args.login}")
        print(f"BOOTSTRAP_ADMIN_PASSWORD={password}")
        print("\n--- CIS login (save for staff) ---")
        print(f"  User ID:  {args.login}")
        print(f"  Password: {password}")
        return

    text = build_env_text(pepper, args.login, password, example_path)
    env_path.write_text(text, encoding="utf-8")

    print(f"Wrote {env_path}")
    print("")
    print("=" * 52)
    print("  SAVE THESE — needed for CIS login and support")
    print("=" * 52)
    print(f"  User ID:  {args.login}")
    print(f"  Password: {password}")
    print("=" * 52)
    print("")
    print("Next:")
    print("  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt")
    print("  bash bootstrap_on_server.sh")
    print("  .venv/bin/python seed_identity.py")
    print("  bash install_service_on_server.sh")


if __name__ == "__main__":
    main()
