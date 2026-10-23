import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure DataPulse and parent directory are on sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
parent_dir = root_dir.parent
for p in [str(parent_dir), str(root_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from DataPulse.database.connection import Base, DATABASE_URL
import DataPulse.database.models  # noqa

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set dynamic database URL
config.set_main_option("sqlalchemy.url", DATABASE_URL)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = DATABASE_URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
