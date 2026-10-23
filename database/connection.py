"""
DataPulse Database Connection Management
Supports PostgreSQL 16 (Production/Docker) with graceful SQLite fallback for local development & testing.
Configures robust connection pooling, pre-ping health validation, and transaction lifecycles.
"""

import os
import logging
from pathlib import Path
from typing import Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

logger = logging.getLogger("datapulse.database")

# Load environment variables from .env file if available
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

DEFAULT_SQLITE_URL = f"sqlite:///{BASE_DIR / 'datapulse.db'}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
elif DATABASE_URL.startswith("postgresql://") and not DATABASE_URL.startswith("postgresql+"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    # Resolve relative sqlite paths consistently relative to BASE_DIR
    raw_path = DATABASE_URL.replace("sqlite:///", "")
    p = Path(raw_path)
    if not p.is_absolute():
        DATABASE_URL = f"sqlite:///{(BASE_DIR / p).resolve()}"
else:
    # Check for weak or placeholder passwords in PostgreSQL connection string
    WEAK_PASSWORDS = {
        "datapulse_secure_password", "postgres", "password", "123456",
        "admin", "replace_with_strong_password", "your_strong_local_postgres_password_here"
    }
    for weak in WEAK_PASSWORDS:
        if f":{weak}@" in DATABASE_URL:
            logger.warning(
                "[SECURITY WARNING] DATABASE_URL contains a default/placeholder password (%s). "
                "Require a strong local secret in .env before running production deployments.", weak
            )
            break

engine_kwargs = {
    "pool_pre_ping": True,
    "echo": os.getenv("SQL_ECHO", "false").lower() == "true",
}

if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Production PostgreSQL connection pool tuning
    engine_kwargs["pool_size"] = int(os.getenv("DB_POOL_SIZE", "10"))
    engine_kwargs["max_overflow"] = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    engine_kwargs["pool_recycle"] = int(os.getenv("DB_POOL_RECYCLE", "1800"))
    engine_kwargs["pool_timeout"] = int(os.getenv("DB_POOL_TIMEOUT", "30"))

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI and service dependency to yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initializes all database tables registered with Base."""
    try:
        import database.models  # noqa
    except ModuleNotFoundError:
        import database.models  # noqa
    Base.metadata.create_all(bind=engine)
