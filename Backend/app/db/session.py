from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from ..core import config
import logging

logger = logging.getLogger(__name__)

def _create_engine_with_fallback(primary_url: str):
    """Create engine for primary_url, test connectivity, and fall back to SQLite if enabled.

    Returns (engine, url_used)
    """
    def _mask_url(url: str) -> str:
        # Mask password portion in URLs like postgresql://user:pass@host/db
        try:
            if "@" in url and "://" in url:
                scheme_sep = url.split("://", 1)
                cred_host = scheme_sep[1]
                if "@" in cred_host and ":" in cred_host.split("@", 1)[0]:
                    user = cred_host.split(":", 1)[0]
                    return f"{scheme_sep[0]}://{user}:***@" + cred_host.split("@", 1)[1]
        except Exception:
            pass
        return url

    def _mk_engine(url: str):
        # Enforce SSL for Postgres (Supabase requires it)
        if url.startswith("postgresql"):
            connect_args = {"sslmode": config.DB_SSLMODE}
        else:
            connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        return create_engine(
            url,
            pool_pre_ping=True,
            connect_args=connect_args,
            echo=config.DB_ECHO,
        )

    # Attempt primary
    engine = _mk_engine(primary_url)
    try:
        with engine.connect() as conn:
            # lightweight ping
            conn.execute(text("SELECT 1"))
        return engine, primary_url
    except Exception as e:
        masked = _mask_url(primary_url)
        logger.exception("Primary DB connection failed for %s: %s", masked, getattr(e, "orig", e))
        if config.DB_FALLBACK_TO_SQLITE:
            # Fall back to SQLite
            sqlite_engine = _mk_engine(config.SQLITE_URL)
            logger.warning("DB connection failed for primary URL; falling back to SQLite at %s", config.SQLITE_URL)
            return sqlite_engine, config.SQLITE_URL
        raise


# Create an SQLAlchemy engine and a session factory with fallback
engine, _active_db_url = _create_engine_with_fallback(config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session in request handlers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
