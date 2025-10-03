"""Application configuration loaded from environment variables.

This module centralizes env parsing and provides sane defaults for local dev.
It loads Backend/.env explicitly (case-insensitive) and normalizes common types.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from urllib.parse import urlsplit, urlunsplit


# --- .env loading -----------------------------------------------------------------
def _load_env_files() -> None:
	"""Load variables from an explicit Backend/.env, with fallbacks.

	Search order:
	1) <repo>/Backend/.env or <repo>/backend/.env
	2) Default python-dotenv search from CWD upward
	"""
	here = Path(__file__).resolve()
	# Expect structure .../Backend/app/core/config.py → parents[2] == Backend
	backend_root = here.parents[2]
	candidates = [backend_root / ".env"]

	# Also try lowercase 'backend' sibling (in case of different casing)
	maybe_backend_lower = backend_root.with_name("backend")
	candidates.append(maybe_backend_lower / ".env")

	for p in candidates:
		if p.exists():
			load_dotenv(dotenv_path=p, override=True)
			return
	# Fallback to default search if explicit path doesn't exist
	load_dotenv(override=True)


def _str2bool(val: str | None, default: bool = False) -> bool:
	if val is None:
		return default
	return val.strip().lower() in {"1", "true", "yes", "on"}


def _strip_quotes(val: str | None) -> Optional[str]:
	if val is None:
		return None
	v = val.strip()
	if (v.startswith("\"") and v.endswith("\"")) or (v.startswith("'") and v.endswith("'")):
		return v[1:-1]
	return v


_load_env_files()

# --- Database configuration --------------------------------------------------------
DB_HOST: str = os.getenv("host", "aws-1-ap-southeast-1.pooler.supabase.co")
DB_PORT: int = int(os.getenv("port", "5432"))
DB_NAME: str = os.getenv("dbname", "postgres")
DB_USER: str = os.getenv("user", "postgres")
DB_PASSWORD: str = os.getenv("password", "")

# Postgres SSL mode (Supabase requires SSL). Typical values: require, verify-ca, verify-full
DB_SSLMODE: str = os.getenv("sslmode", "require")

# Engine echo logging for debugging SQL issues
DB_ECHO: bool = _str2bool(os.getenv("DB_ECHO"), False)

# Optional: force a graceful fallback to SQLite when the primary DB is unreachable (useful in local dev/offline)
DB_FALLBACK_TO_SQLITE: bool = _str2bool(os.getenv("DB_FALLBACK_TO_SQLITE"), True)
SQLITE_URL: str = os.getenv("SQLITE_URL", "sqlite:///./app.db")


def _build_database_url() -> str:
	"""Return the effective SQLAlchemy DATABASE_URL.

	Priority:
	1) Explicit DATABASE_URL env var
	2) Construct from individual DB_* components
	3) Default to SQLite
	"""
	raw_url = os.getenv("DATABASE_URL")
	raw_url = _strip_quotes(raw_url)

	if raw_url:
		# Normalize legacy scheme 'postgres://' → 'postgresql://'
		if raw_url.startswith("postgres://"):
			raw_url = "postgresql://" + raw_url.split("://", 1)[1]

		# Fix common mistake: bracketed password in URL (e.g., :[pass]@)
		try:
			parts = urlsplit(raw_url)
			if "@" in parts.netloc:
				userinfo, hostport = parts.netloc.rsplit("@", 1)
				if ":" in userinfo:
					user, pwd = userinfo.split(":", 1)
					if pwd.startswith("[") and pwd.endswith("]"):
						pwd = pwd[1:-1]
						new_netloc = f"{user}:{pwd}@{hostport}"
						parts = parts._replace(netloc=new_netloc)
						raw_url = urlunsplit(parts)
		except Exception:
			# If anything goes wrong, fall back to the original string
			pass

		return raw_url

	# Build from components if host/user provided
	if DB_HOST and DB_USER:
		# Note: SSL is enforced in SQLAlchemy via connect_args in session.py
		password = DB_PASSWORD
		auth = f"{DB_USER}:{password}" if password else DB_USER
		return f"postgresql://{auth}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

	# Fallback to local SQLite
	return SQLITE_URL


# Database URL (fallback to local SQLite for dev if not provided)
# Example Postgres URL: postgresql+psycopg2://user:pass@localhost:5432/rama
DATABASE_URL: str = _build_database_url()


# --- Auth / JWT -------------------------------------------------------------------
JWT_SECRET: str = _strip_quotes(os.getenv("JWT_SECRET")) or "CHANGE_ME"
ALGORITHM: str = _strip_quotes(os.getenv("ALGORITHM")) or "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


# --- CORS -------------------------------------------------------------------------
FRONTEND_ORIGIN: str = _strip_quotes(os.getenv("FRONTEND_ORIGIN")) or "http://localhost:3000"
